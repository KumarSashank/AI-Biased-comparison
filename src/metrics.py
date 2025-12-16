"""
Metrics calculation for bias analysis.
"""
from typing import List, Dict, Any
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from .models import ExperimentRun, TestType, Vote


class MetricsCalculator:
    """Calculate bias metrics from experiment results."""
    
    def __init__(self, runs: List[ExperimentRun]):
        self.runs = runs
    
    def calculate_self_bias_rate(self, test_type: TestType) -> Dict[str, float]:
        """
        Calculate self-bias rate for each model.
        Returns percentage of times each model voted for itself.
        """
        self_votes = defaultdict(int)
        total_votes = defaultdict(int)
        
        for run in self.runs:
            if run.test_type != test_type:
                continue
            
            for vote in run.votes:
                total_votes[vote.voter_model] += 1
                if vote.is_self_vote:
                    self_votes[vote.voter_model] += 1
        
        rates = {}
        for model in total_votes:
            rates[model] = (self_votes[model] / total_votes[model]) * 100 if total_votes[model] > 0 else 0
        
        return rates
    
    def calculate_style_recognition_bias(self) -> Dict[str, Dict[str, Any]]:
        """
        Calculate style-recognition bias for Test 4.
        Measures if models vote for answers most similar to their own.
        """
        results = {}
        
        # Only analyze Test 4
        test4_runs = [run for run in self.runs if run.test_type == TestType.CONTEXT_OFF_ANONYMOUS_NO_SELF_VOTE]
        
        for run in test4_runs:
            # Calculate text similarity between each model's answer and all answers
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            # Get all answer texts
            answer_texts = [answer.text for answer in run.answers]
            model_names = [answer.model_name for answer in run.answers]
            
            # Vectorize
            try:
                vectors = vectorizer.fit_transform(answer_texts)
                similarity_matrix = cosine_similarity(vectors)
            except:
                # Fallback if vectorization fails
                continue
            
            for vote in run.votes:
                voter_idx = model_names.index(vote.voter_model)
                voted_idx = vote.voted_for_index - 1
                
                # Find most similar answer to voter's own answer
                voter_similarities = similarity_matrix[voter_idx]
                most_similar_idx = np.argmax([sim for i, sim in enumerate(voter_similarities) if i != voter_idx])
                
                # Check if they voted for the most similar one
                voted_for_most_similar = (most_similar_idx == voted_idx)
                
                if vote.voter_model not in results:
                    results[vote.voter_model] = {
                        'total': 0,
                        'voted_for_most_similar': 0,
                        'self_vote_attempts': 0
                    }
                
                results[vote.voter_model]['total'] += 1
                if voted_for_most_similar:
                    results[vote.voter_model]['voted_for_most_similar'] += 1
                if vote.is_self_vote:
                    results[vote.voter_model]['self_vote_attempts'] += 1
        
        # Calculate percentages
        for model in results:
            total = results[model]['total']
            if total > 0:
                results[model]['style_recognition_rate'] = (
                    results[model]['voted_for_most_similar'] / total * 100
                )
                results[model]['self_recognition_rate'] = (
                    results[model]['self_vote_attempts'] / total * 100
                )
        
        return results
    
    def calculate_contextual_influence(self) -> Dict[str, Any]:
        """
        Compare voting patterns with and without context.
        Returns differences between Test 1 vs Test 3 and Test 2 vs Test 4.
        """
        # Group runs by prompt
        runs_by_prompt = defaultdict(list)
        for run in self.runs:
            runs_by_prompt[run.prompt].append(run)
        
        results = {
            'test1_vs_test3': {},  # Context ON vs OFF (no self-vote)
            'test2_vs_test4': {}   # Context ON vs OFF (self-vote allowed)
        }
        
        for prompt, prompt_runs in runs_by_prompt.items():
            test1 = next((r for r in prompt_runs if r.test_type == TestType.CONTEXT_ON_NO_SELF_VOTE), None)
            test3 = next((r for r in prompt_runs if r.test_type == TestType.CONTEXT_OFF_ANONYMOUS_SELF_VOTE), None)
            test2 = next((r for r in prompt_runs if r.test_type == TestType.CONTEXT_ON_SELF_VOTE), None)
            test4 = next((r for r in prompt_runs if r.test_type == TestType.CONTEXT_OFF_ANONYMOUS_NO_SELF_VOTE), None)
            
            # Compare Test 1 vs Test 3
            if test1 and test3:
                vote_changes = {}
                for vote1, vote3 in zip(test1.votes, test3.votes):
                    if vote1.voter_model == vote3.voter_model:
                        changed = (vote1.voted_for_model != vote3.voted_for_model)
                        vote_changes[vote1.voter_model] = changed
                results['test1_vs_test3'][prompt] = vote_changes
            
            # Compare Test 2 vs Test 4
            if test2 and test4:
                vote_changes = {}
                for vote2, vote4 in zip(test2.votes, test4.votes):
                    if vote2.voter_model == vote4.voter_model:
                        changed = (vote2.voted_for_model != vote4.voted_for_model)
                        vote_changes[vote2.voter_model] = changed
                results['test2_vs_test4'][prompt] = vote_changes
        
        return results
    
    def calculate_voting_distribution(self) -> Dict[str, Dict[str, int]]:
        """Calculate overall voting distribution - which models get the most votes."""
        distribution = defaultdict(lambda: defaultdict(int))
        
        for run in self.runs:
            for vote in run.votes:
                distribution[run.test_type.value][vote.voted_for_model] += 1
        
        return dict(distribution)
    
    def calculate_all_metrics(self) -> Dict[str, Any]:
        """Calculate all metrics."""
        return {
            'self_bias_test2': self.calculate_self_bias_rate(TestType.CONTEXT_ON_SELF_VOTE),
            'self_bias_test4': self.calculate_self_bias_rate(TestType.CONTEXT_OFF_ANONYMOUS_NO_SELF_VOTE),
            'style_recognition': self.calculate_style_recognition_bias(),
            'contextual_influence': self.calculate_contextual_influence(),
            'voting_distribution': self.calculate_voting_distribution(),
            'violation_rates': self._calculate_violation_rates()
        }
    
    def _calculate_violation_rates(self) -> Dict[str, Dict[str, float]]:
        """Calculate how often models violate instructions."""
        violations = defaultdict(lambda: defaultdict(int))
        total = defaultdict(lambda: defaultdict(int))
        
        for run in self.runs:
            for vote in run.votes:
                total[run.test_type.value][vote.voter_model] += 1
                if vote.is_violation:
                    violations[run.test_type.value][vote.voter_model] += 1
        
        rates = {}
        for test_type in total:
            rates[test_type] = {}
            for model in total[test_type]:
                rates[test_type][model] = (
                    violations[test_type][model] / total[test_type][model] * 100
                    if total[test_type][model] > 0 else 0
                )
        
        return rates

