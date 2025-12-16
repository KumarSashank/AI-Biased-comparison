"""
Data management for saving and loading experiment results.
"""
import json
import os
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .models import ExperimentRun, Answer, Vote, TestType


class DataManager:
    """Handle saving and loading experiment data."""
    
    def __init__(self, results_dir: str = "results", data_dir: str = "data"):
        self.results_dir = Path(results_dir)
        self.data_dir = Path(data_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
    
    def save_run(self, run: ExperimentRun, filename: Optional[str] = None):
        """Save a single experiment run to JSON."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"run_{run.test_type.value}_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        data = {
            'prompt': run.prompt,
            'test_type': run.test_type.value,
            'timestamp': run.timestamp.isoformat(),
            'answers': [
                {
                    'model_name': a.model_name,
                    'text': a.text,
                    'timestamp': a.timestamp.isoformat()
                }
                for a in run.answers
            ],
            'votes': [
                {
                    'voter_model': v.voter_model,
                    'voted_for_model': v.voted_for_model,
                    'voted_for_index': v.voted_for_index,
                    'is_self_vote': v.is_self_vote,
                    'is_violation': v.is_violation,
                    'recognized_own_style': v.recognized_own_style,
                    'reasoning': v.reasoning,
                    'timestamp': v.timestamp.isoformat()
                }
                for v in run.votes
            ],
            'answer_mapping': run.answer_mapping
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_runs(self, runs: List[ExperimentRun], filename: Optional[str] = None):
        """Save multiple runs to a single JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"experiment_runs_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        data = {
            'runs': [
                {
                    'prompt': run.prompt,
                    'test_type': run.test_type.value,
                    'timestamp': run.timestamp.isoformat(),
                    'answers': [
                        {
                            'model_name': a.model_name,
                            'text': a.text,
                            'timestamp': a.timestamp.isoformat()
                        }
                        for a in run.answers
                    ],
                    'votes': [
                        {
                            'voter_model': v.voter_model,
                            'voted_for_model': v.voted_for_model,
                            'voted_for_index': v.voted_for_index,
                            'is_self_vote': v.is_self_vote,
                            'is_violation': v.is_violation,
                            'recognized_own_style': v.recognized_own_style,
                            'reasoning': v.reasoning,
                            'timestamp': v.timestamp.isoformat()
                        }
                        for v in run.votes
                    ],
                    'answer_mapping': run.answer_mapping
                }
                for run in runs
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_metrics(self, metrics: Dict[str, Any], filename: Optional[str] = None):
        """Save calculated metrics to JSON."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            else:
                return obj
        
        serializable_metrics = convert_to_serializable(metrics)
        
        with open(filepath, 'w') as f:
            json.dump(serializable_metrics, f, indent=2)
    
    def export_to_csv(self, runs: List[ExperimentRun], filename: Optional[str] = None):
        """Export experiment data to CSV for easy analysis."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"experiment_data_{timestamp}.csv"
        
        filepath = self.data_dir / filename
        
        rows = []
        for run in runs:
            for vote in run.votes:
                rows.append({
                    'prompt': run.prompt,
                    'test_type': run.test_type.value,
                    'voter_model': vote.voter_model,
                    'voted_for_model': vote.voted_for_model,
                    'voted_for_index': vote.voted_for_index,
                    'is_self_vote': vote.is_self_vote,
                    'is_violation': vote.is_violation,
                    'recognized_own_style': vote.recognized_own_style,
                    'timestamp': vote.timestamp.isoformat()
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        return filepath

