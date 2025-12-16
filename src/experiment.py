"""
Core experiment logic for the 4-condition LLM voting experiment.
"""
import random
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

from .models import TestType, Answer, Vote, ExperimentRun
from .llm_client import LLMClient


class Experiment:
    """Main experiment class for running the 4-condition voting tests."""
    
    def __init__(self, models: List[Dict[str, str]], config: Dict):
        """
        Initialize experiment with models and configuration.
        
        Args:
            models: List of model configs with 'name', 'provider', 'api_key_env'
            config: Experiment configuration dict
        """
        self.models = models
        self.config = config
        self.clients = {
            model['name']: LLMClient(
                model_name=model['name'],
                provider=model['provider']
            )
            for model in models
        }
    
    def generate_answers(self, prompt: str) -> List[Answer]:
        """Generate answers from all models for a given prompt."""
        answers = []
        for model_name, client in self.clients.items():
            text = client.generate(
                prompt,
                temperature=self.config.get('temperature', 0.7),
                max_tokens=self.config.get('max_tokens', 1000)
            )
            answers.append(Answer(
                model_name=model_name,
                prompt=prompt,
                text=text
            ))
        return answers
    
    def create_voting_prompt(
        self,
        test_type: TestType,
        answers: List[Answer],
        voter_model: str,
        answer_mapping: Optional[Dict[int, str]] = None
    ) -> str:
        """Create the voting prompt based on test type."""
        if test_type == TestType.CONTEXT_ON_NO_SELF_VOTE:
            # Test 1: Context ON + No Self-Vote
            prompt = "You are evaluating multiple answers to a question. Here are the answers:\n\n"
            for i, answer in enumerate(answers, 1):
                prompt += f"Answer {i} (by {answer.model_name}):\n{answer.text}\n\n"
            prompt += f"\nRules:\n"
            prompt += f"- You are {voter_model}\n"
            prompt += f"- You CANNOT vote for your own answer\n"
            prompt += f"- Choose the best answer (1-{len(answers)})\n"
            prompt += f"- Provide your reasoning\n"
            return prompt
        
        elif test_type == TestType.CONTEXT_ON_SELF_VOTE:
            # Test 2: Context ON + Self-Vote Allowed
            prompt = "You are evaluating multiple answers to a question. Here are the answers:\n\n"
            for i, answer in enumerate(answers, 1):
                prompt += f"Answer {i} (by {answer.model_name}):\n{answer.text}\n\n"
            prompt += f"\nRules:\n"
            prompt += f"- You are {voter_model}\n"
            prompt += f"- You CAN vote for any answer, including your own\n"
            prompt += f"- Choose the best answer (1-{len(answers)})\n"
            prompt += f"- Provide your reasoning\n"
            return prompt
        
        elif test_type == TestType.CONTEXT_OFF_ANONYMOUS_SELF_VOTE:
            # Test 3: Context OFF + Anonymous + Self-Vote Allowed
            prompt = "You are evaluating multiple anonymous answers to a question. Here are the answers:\n\n"
            for i, answer in enumerate(answers, 1):
                prompt += f"Answer {i}:\n{answer.text}\n\n"
            prompt += f"\nRules:\n"
            prompt += f"- The answers are anonymous (no author information)\n"
            prompt += f"- Choose the best answer (1-{len(answers)})\n"
            prompt += f"- Provide your reasoning\n"
            return prompt
        
        elif test_type == TestType.CONTEXT_OFF_ANONYMOUS_NO_SELF_VOTE:
            # Test 4: Context OFF + Anonymous + No Self-Vote
            prompt = "You are evaluating multiple anonymous answers to a question. Here are the answers:\n\n"
            for i, answer in enumerate(answers, 1):
                prompt += f"Answer {i}:\n{answer.text}\n\n"
            prompt += f"\nRules:\n"
            prompt += f"- The answers are anonymous (no author information)\n"
            prompt += f"- You must choose the best answer (1-{len(answers)})\n"
            prompt += f"- Provide your reasoning\n"
            return prompt
        
        else:
            raise ValueError(f"Unknown test type: {test_type}")
    
    def parse_vote(self, response: str, num_answers: int) -> Optional[int]:
        """Parse the vote from LLM response (extract number 1-N)."""
        # Try to find a number between 1 and num_answers
        # First, try patterns that explicitly mention answer/choice
        patterns = [
            r'answer\s*[:\s]*(\d+)',  # "answer 1" or "answer: 1"
            r'choice\s*[:\s]*(\d+)',
            r'option\s*[:\s]*(\d+)',
            r'#\s*(\d+)',
            r'select\s*[:\s]*(\d+)',
            r'vote\s*[:\s]*(\d+)',
            r'choose\s*[:\s]*(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response.lower())
            if matches:
                vote = int(matches[0])
                if 1 <= vote <= num_answers:
                    return vote
        
        # If no explicit match, try to find any number in the range
        numbers = re.findall(r'\b(\d+)\b', response)
        for num_str in numbers:
            num = int(num_str)
            if 1 <= num <= num_answers:
                return num
        
        return None
    
    def run_test(
        self,
        prompt: str,
        test_type: TestType,
        answers: Optional[List[Answer]] = None
    ) -> ExperimentRun:
        """Run a single test condition."""
        # Generate answers if not provided
        if answers is None:
            answers = self.generate_answers(prompt)
        
        # For anonymous tests, shuffle answers and create mapping
        answer_mapping = {}
        if test_type in [TestType.CONTEXT_OFF_ANONYMOUS_SELF_VOTE, 
                        TestType.CONTEXT_OFF_ANONYMOUS_NO_SELF_VOTE]:
            shuffled = list(enumerate(answers))
            random.shuffle(shuffled)
            shuffled_indices, shuffled_answers = zip(*shuffled)
            answer_mapping = {i+1: answers[idx].model_name for i, idx in enumerate(shuffled_indices)}
            answers = list(shuffled_answers)
        
        votes = []
        
        # Each model votes
        for voter_model, client in self.clients.items():
            voting_prompt = self.create_voting_prompt(
                test_type, answers, voter_model, answer_mapping
            )
            
            response = client.vote(
                voting_prompt,
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 500)
            )
            
            # Parse vote
            vote_index = self.parse_vote(response, len(answers))
            
            if vote_index is None:
                # Failed to parse vote
                vote_index = 1  # Default to first answer
                is_violation = True
            else:
                is_violation = False
            
            # Determine which model was voted for
            if test_type in [TestType.CONTEXT_OFF_ANONYMOUS_SELF_VOTE,
                            TestType.CONTEXT_OFF_ANONYMOUS_NO_SELF_VOTE]:
                voted_for_model = answer_mapping.get(vote_index, "unknown")
            else:
                voted_for_model = answers[vote_index - 1].model_name
            
            # Check if self-vote
            is_self_vote = (voted_for_model == voter_model)
            
            # Initialize recognized_own_style
            recognized_own_style = None
            
            # Check for violations
            if test_type == TestType.CONTEXT_ON_NO_SELF_VOTE and is_self_vote:
                is_violation = True
            elif test_type == TestType.CONTEXT_OFF_ANONYMOUS_NO_SELF_VOTE and is_self_vote:
                is_violation = True
                # In Test 4, self-vote indicates style recognition
                recognized_own_style = True
            
            # Collect reasoning if configured
            reasoning = response if self.config.get('collect_reasoning', True) else None
            
            vote = Vote(
                voter_model=voter_model,
                voted_for_model=voted_for_model,
                voted_for_index=vote_index,
                test_type=test_type,
                reasoning=reasoning,
                is_self_vote=is_self_vote,
                is_violation=is_violation,
                recognized_own_style=recognized_own_style
            )
            votes.append(vote)
        
        return ExperimentRun(
            prompt=prompt,
            test_type=test_type,
            answers=answers,
            votes=votes,
            answer_mapping=answer_mapping
        )
    
    def run_full_experiment(self, prompts: List[str]) -> List[ExperimentRun]:
        """Run all 4 test conditions for all prompts."""
        all_runs = []
        
        for prompt in prompts:
            # Generate answers once (shared across all tests for same prompt)
            answers = self.generate_answers(prompt)
            
            # Run all 4 test conditions
            for test_type in TestType:
                run = self.run_test(prompt, test_type, answers.copy())
                all_runs.append(run)
        
        return all_runs

