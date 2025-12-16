"""
LLM client for interacting with different LLM providers.
"""
import os
import random
import hashlib
from typing import Optional, Dict, Any
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
import cohere


class LLMClient:
    """Unified client for multiple LLM providers."""
    
    def __init__(self, model_name: str, provider: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.provider = provider.lower()
        self.api_key = api_key or self._get_api_key()
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=self.api_key)
        elif self.provider == "google" or self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
        elif self.provider == "deepseek":
            # DeepSeek uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
        elif self.provider == "mistral":
            # Mistral uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.mistral.ai/v1"
            )
        elif self.provider == "cohere":
            self.client = cohere.Client(api_key=self.api_key)
        elif self.provider == "mock":
            # Mock provider for testing without API costs
            self.client = None
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _get_api_key(self) -> str:
        """Get API key from environment variable."""
        if self.provider == "mock":
            return "mock_key"  # Dummy key for mock mode
        elif self.provider == "openai":
            key = os.getenv("OPENAI_API_KEY")
        elif self.provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "google" or self.provider == "gemini":
            key = os.getenv("GEMINI_API_KEY")
        elif self.provider == "deepseek":
            key = os.getenv("DEEPSEEK_API_KEY")
        elif self.provider == "mistral":
            key = os.getenv("MISTRAL_API_KEY")
        elif self.provider == "cohere":
            key = os.getenv("COHERE_API_KEY")
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
        
        if not key:
            raise ValueError(f"API key not found for provider: {self.provider}")
        return key
    
    def _generate_mock_response(self, prompt: str, model_name: str, max_tokens: int = 1000) -> str:
        """Generate a mock response for testing without API calls."""
        # Create deterministic but varied responses based on prompt + model name
        seed = int(hashlib.md5((prompt + model_name).encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Different model "personalities"
        model_templates = {
            "mock-model-a": [
                "This is a comprehensive response that addresses the key aspects of your question.",
                "I'll provide a detailed explanation covering the main points.",
                "Let me break this down systematically for better understanding."
            ],
            "mock-model-b": [
                "Here's a concise answer to your question with practical insights.",
                "I'd like to offer a focused perspective on this topic.",
                "From my analysis, here are the essential points to consider."
            ],
            "mock-model-c": [
                "This topic is complex and requires nuanced consideration of multiple factors.",
                "I'll approach this from a structured analytical framework.",
                "Let me explore the various dimensions of this question."
            ],
            "mock-model-d": [
                "A straightforward answer: the core concept involves several key principles.",
                "This can be understood through examining the fundamental mechanisms at play.",
                "I'll explain this using clear examples and concrete applications."
            ]
        }
        
        # Select template based on model name (deterministic)
        model_hash = int(hashlib.md5(model_name.encode()).hexdigest()[:8], 16)
        model_key = list(model_templates.keys())[model_hash % len(model_templates)]
        templates = model_templates[model_key]
        template = templates[seed % len(templates)]
        
        # Generate response based on prompt length and max_tokens
        words = prompt.split()[:20]  # Use first 20 words from prompt
        response = f"{template} {' '.join(words)}. This response demonstrates how different models might approach the same question. The answer varies based on the model's training and perspective. "
        
        # Add some model-specific characteristics
        if "a" in model_name.lower():
            response += "Model A tends to be more detailed and comprehensive."
        elif "b" in model_name.lower():
            response += "Model B prefers concise and actionable responses."
        elif "c" in model_name.lower():
            response += "Model C emphasizes analytical depth and nuance."
        else:
            response += "This model focuses on clarity and practical examples."
        
        # Truncate to approximate max_tokens (rough estimate: 1 token ≈ 0.75 words)
        max_words = int(max_tokens * 0.75)
        response_words = response.split()
        if len(response_words) > max_words:
            response = ' '.join(response_words[:max_words]) + "..."
        
        return response
    
    def _generate_mock_vote(self, voting_prompt: str, model_name: str) -> str:
        """Generate a mock vote response for testing."""
        # Extract number of answers from prompt
        import re
        num_matches = re.findall(r'(\d+)', voting_prompt)
        if num_matches:
            num_answers = int(num_matches[-1])  # Last number is usually the answer count
        else:
            num_answers = 2
        
        # Deterministic but varied voting based on prompt + model
        seed = int(hashlib.md5((voting_prompt + model_name).encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        # Different models have different voting patterns (some more self-biased)
        vote = random.randint(1, num_answers)
        
        # Some models are more likely to vote for themselves
        if "a" in model_name.lower() and random.random() < 0.4:
            # Try to find their own answer in the prompt
            if model_name in voting_prompt:
                vote = 1  # Self-bias for model-a
        
        reasoning_templates = [
            f"I choose Answer {vote} because it provides the most comprehensive response.",
            f"Answer {vote} stands out for its clarity and depth of analysis.",
            f"After careful consideration, Answer {vote} best addresses the question.",
            f"I select Answer {vote} as it demonstrates superior reasoning and examples."
        ]
        
        response = f"I vote for Answer {vote}. {random.choice(reasoning_templates)}"
        return response
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """Generate a response to a prompt."""
        if self.provider == "mock":
            return self._generate_mock_response(prompt, self.model_name, max_tokens)
        elif self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        elif self.provider == "google" or self.provider == "gemini":
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            return response.text
        elif self.provider == "deepseek" or self.provider == "mistral":
            # Both use OpenAI-compatible API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        elif self.provider == "cohere":
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.generations[0].text
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def vote(self, voting_prompt: str, temperature: float = 0.3, max_tokens: int = 500) -> str:
        """Get a vote/response to a voting prompt."""
        if self.provider == "mock":
            return self._generate_mock_vote(voting_prompt, self.model_name)
        return self.generate(voting_prompt, temperature=temperature, max_tokens=max_tokens)

