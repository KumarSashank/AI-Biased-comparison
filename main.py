#!/usr/bin/env python3
"""
Main script to run the LLM voting experiment.
"""
import yaml
import os
from dotenv import load_dotenv
from tqdm import tqdm

from src.experiment import Experiment
from src.data_manager import DataManager
from src.metrics import MetricsCalculator
from src.analysis import Analyzer


def load_config(config_path: str = "config.yaml"):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Run the full experiment."""
    import sys
    
    # Check if mock config is requested
    config_path = "config.yaml"
    if len(sys.argv) > 1 and sys.argv[1] == "--mock":
        config_path = "config.mock.yaml"
        print("💰 Running in FREE mock mode - no API costs!")
    elif len(sys.argv) > 1 and sys.argv[1].endswith(".yaml"):
        config_path = sys.argv[1]
    
    # Load environment variables (optional for mock mode)
    load_dotenv()
    
    # Load configuration
    print(f"Loading configuration from {config_path}...")
    config = load_config(config_path)
    
    # Check if using mock mode
    is_mock = any(model.get('provider', '').lower() == 'mock' for model in config['models'])
    if is_mock:
        print("🧪 Running in MOCK MODE (no API costs, simulated responses)")
        print("=" * 80)
    
    # Initialize components
    print("Initializing experiment...")
    experiment = Experiment(
        models=config['models'],
        config=config['experiment']
    )
    
    data_manager = DataManager(
        results_dir=config['output']['results_dir'],
        data_dir=config['output']['data_dir']
    )
    
    # Run experiment
    print(f"\nRunning experiment with {len(config['prompts'])} prompts...")
    print(f"Models: {len(config['models'])}")
    print(f"Test conditions: 4")
    print(f"Total runs: {len(config['prompts']) * 4}\n")
    
    all_runs = []
    total_runs = len(config['prompts']) * 4
    
    with tqdm(total=total_runs, desc="Running experiments") as pbar:
        for prompt in config['prompts']:
            # Generate answers once per prompt
            answers = experiment.generate_answers(prompt)
            
            # Run all 4 test conditions
            from src.models import TestType
            for test_type in TestType:
                run = experiment.run_test(prompt, test_type, answers.copy())
                all_runs.append(run)
                pbar.update(1)
    
    # Save data
    print("\nSaving experiment data...")
    data_manager.save_runs(all_runs)
    data_manager.export_to_csv(all_runs)
    
    # Calculate metrics
    print("Calculating metrics...")
    metrics_calc = MetricsCalculator(all_runs)
    metrics = metrics_calc.calculate_all_metrics()
    data_manager.save_metrics(metrics)
    
    # Generate analysis
    print("Generating analysis and visualizations...")
    analyzer = Analyzer(all_runs, plots_dir=config['output']['plots_dir'])
    analyzer.generate_all_plots()
    
    # Print summary
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)
    print(analyzer.generate_summary_report())
    
    print(f"\nResults saved to:")
    print(f"  - Data: {config['output']['data_dir']}")
    print(f"  - Metrics: {config['output']['results_dir']}")
    print(f"  - Plots: {config['output']['plots_dir']}")
    
    if is_mock:
        print("\n💡 Tip: To run with real APIs, use: python main.py (with your config.yaml)")


if __name__ == "__main__":
    main()

