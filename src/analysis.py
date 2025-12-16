"""
Analysis and visualization tools for experiment results.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

from .models import ExperimentRun, TestType
from .metrics import MetricsCalculator


class Analyzer:
    """Analysis and visualization tools."""
    
    def __init__(self, runs: List[ExperimentRun], plots_dir: str = "plots"):
        self.runs = runs
        self.plots_dir = Path(plots_dir)
        self.plots_dir.mkdir(exist_ok=True)
        self.metrics_calc = MetricsCalculator(runs)
    
    def generate_summary_report(self) -> str:
        """Generate a text summary report of findings."""
        metrics = self.metrics_calc.calculate_all_metrics()
        
        report = []
        report.append("=" * 80)
        report.append("LLM VOTING EXPERIMENT - SUMMARY REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Self-Bias Analysis
        report.append("1. SELF-BIAS ANALYSIS")
        report.append("-" * 80)
        report.append("\nTest 2 (Context ON + Self-Vote Allowed):")
        for model, rate in metrics['self_bias_test2'].items():
            report.append(f"  {model}: {rate:.1f}% self-vote rate")
        
        report.append("\nTest 4 (Context OFF + Anonymous + No Self-Vote):")
        for model, rate in metrics['self_bias_test4'].items():
            report.append(f"  {model}: {rate:.1f}% self-vote rate (violations)")
        
        # Style Recognition
        report.append("\n\n2. STYLE-RECOGNITION BIAS")
        report.append("-" * 80)
        for model, data in metrics['style_recognition'].items():
            if 'style_recognition_rate' in data:
                report.append(f"\n{model}:")
                report.append(f"  Voted for most similar answer: {data['style_recognition_rate']:.1f}%")
                report.append(f"  Self-recognition attempts: {data.get('self_recognition_rate', 0):.1f}%")
        
        # Contextual Influence
        report.append("\n\n3. CONTEXTUAL INFLUENCE")
        report.append("-" * 80)
        report.append("\nVote changes when context is removed:")
        test1_vs_test3 = metrics['contextual_influence']['test1_vs_test3']
        test2_vs_test4 = metrics['contextual_influence']['test2_vs_test4']
        
        if test1_vs_test3:
            report.append("\nTest 1 vs Test 3 (No Self-Vote):")
            for prompt, changes in test1_vs_test3.items():
                changed_count = sum(1 for v in changes.values() if v)
                total = len(changes)
                report.append(f"  {prompt[:50]}...: {changed_count}/{total} models changed vote")
        
        if test2_vs_test4:
            report.append("\nTest 2 vs Test 4 (Self-Vote Allowed):")
            for prompt, changes in test2_vs_test4.items():
                changed_count = sum(1 for v in changes.values() if v)
                total = len(changes)
                report.append(f"  {prompt[:50]}...: {changed_count}/{total} models changed vote")
        
        # Voting Distribution
        report.append("\n\n4. OVERALL VOTING DISTRIBUTION")
        report.append("-" * 80)
        for test_type, distribution in metrics['voting_distribution'].items():
            report.append(f"\n{test_type}:")
            sorted_models = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
            for model, votes in sorted_models:
                report.append(f"  {model}: {votes} votes")
        
        # Violation Rates
        report.append("\n\n5. INSTRUCTION VIOLATION RATES")
        report.append("-" * 80)
        for test_type, violations in metrics['violation_rates'].items():
            report.append(f"\n{test_type}:")
            for model, rate in violations.items():
                report.append(f"  {model}: {rate:.1f}% violation rate")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def plot_self_bias_comparison(self, filename: str = "self_bias_comparison.png"):
        """Plot self-bias rates across Test 2 and Test 4."""
        metrics = self.metrics_calc.calculate_all_metrics()
        
        models = list(metrics['self_bias_test2'].keys())
        test2_rates = [metrics['self_bias_test2'][m] for m in models]
        test4_rates = [metrics['self_bias_test4'][m] for m in models]
        
        x = np.arange(len(models))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, test2_rates, width, label='Test 2 (Context ON)', alpha=0.8)
        bars2 = ax.bar(x + width/2, test4_rates, width, label='Test 4 (Context OFF)', alpha=0.8)
        
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Self-Vote Rate (%)', fontsize=12)
        ax.set_title('Self-Bias Comparison: Test 2 vs Test 4', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.plots_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_voting_distribution(self, filename: str = "voting_distribution.png"):
        """Plot voting distribution across all test types."""
        metrics = self.metrics_calc.calculate_all_metrics()
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        test_types = ['test_1', 'test_2', 'test_3', 'test_4']
        test_names = [
            'Test 1: Context ON + No Self-Vote',
            'Test 2: Context ON + Self-Vote',
            'Test 3: Context OFF + Anonymous + Self-Vote',
            'Test 4: Context OFF + Anonymous + No Self-Vote'
        ]
        
        for idx, (test_type, test_name) in enumerate(zip(test_types, test_names)):
            if test_type in metrics['voting_distribution']:
                distribution = metrics['voting_distribution'][test_type]
                models = list(distribution.keys())
                votes = list(distribution.values())
                
                axes[idx].barh(models, votes, alpha=0.7)
                axes[idx].set_xlabel('Number of Votes', fontsize=10)
                axes[idx].set_title(test_name, fontsize=11, fontweight='bold')
                axes[idx].grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.plots_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_style_recognition(self, filename: str = "style_recognition.png"):
        """Plot style recognition metrics."""
        metrics = self.metrics_calc.calculate_all_metrics()
        
        style_data = metrics['style_recognition']
        if not style_data:
            return
        
        models = list(style_data.keys())
        recognition_rates = [
            style_data[m].get('style_recognition_rate', 0) for m in models
        ]
        self_recognition_rates = [
            style_data[m].get('self_recognition_rate', 0) for m in models
        ]
        
        x = np.arange(len(models))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width/2, recognition_rates, width, 
                      label='Voted for Most Similar Answer', alpha=0.8)
        bars2 = ax.bar(x + width/2, self_recognition_rates, width,
                      label='Self-Recognition Attempts', alpha=0.8)
        
        ax.set_xlabel('Model', fontsize=12)
        ax.set_ylabel('Rate (%)', fontsize=12)
        ax.set_title('Style Recognition Bias (Test 4)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.plots_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_all_plots(self):
        """Generate all visualization plots."""
        self.plot_self_bias_comparison()
        self.plot_voting_distribution()
        self.plot_style_recognition()
        print(f"All plots saved to {self.plots_dir}")

