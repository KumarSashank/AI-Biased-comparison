#!/usr/bin/env python3
"""
Simplified script to run a quick test experiment.
Use this for testing before running the full experiment.
"""
import yaml
import os
from dotenv import load_dotenv

from src.experiment import Experiment
from src.models import TestType
from src.data_manager import DataManager
from src.metrics import MetricsCalculator
from src.analysis import Analyzer


def quick_test():
    """Run a quick test with a single prompt."""
    load_dotenv()
    
    # Minimal config for testing
    config = {
        'models': [
            {
                'name': 'gpt-3.5-turbo',
                'provider': 'openai',
                'api_key_env': 'OPENAI_API_KEY'
            }
        ],
        'experiment': {
            'temperature': 0.7,
            'max_tokens': 500,
            'collect_reasoning': True
        },
        'output': {
            'results_dir': 'results',
            'data_dir': 'data',
            'plots_dir': 'plots'
        }
    }
    
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY'):
        print("ERROR: OPENAI_API_KEY not found in environment.")
        print("Please set it in your .env file or environment.")
        return
    
    print("Running quick test experiment...")
    print("=" * 60)
    
    # Initialize
    experiment = Experiment(
        models=config['models'],
        config=config['experiment']
    )
    
    # Test with a simple prompt
    test_prompt = "Explain what machine learning is in one paragraph."
    print(f"\nPrompt: {test_prompt}\n")
    
    # Generate answers
    print("Generating answers...")
    answers = experiment.generate_answers(test_prompt)
    print(f"Generated {len(answers)} answers\n")
    
    # Run one test condition
    print("Running Test 2 (Context ON + Self-Vote Allowed)...")
    run = experiment.run_test(test_prompt, TestType.CONTEXT_ON_SELF_VOTE, answers.copy())
    
    # Display results
    print("\nVoting Results:")
    print("-" * 60)
    for vote in run.votes:
        self_vote_marker = " [SELF-VOTE]" if vote.is_self_vote else ""
        print(f"{vote.voter_model} → {vote.voted_for_model}{self_vote_marker}")
    
    print("\nTest completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    quick_test()

