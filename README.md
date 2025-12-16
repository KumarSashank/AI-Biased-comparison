# LLM Voting Experiment: Bias Detection Framework

A comprehensive 4-condition experiment designed to measure different types of bias in Large Language Model (LLM) voting behavior.

## 🎯 Experiment Overview

This project measures four types of bias:

1. **Self-bias**: Do models prefer their own answers?
2. **Evaluator bias**: Do models show preference based on model identity?
3. **Style-recognition bias**: Can models recognize their own writing style?
4. **Context-induced bias**: Does knowing authorship change voting patterns?

## 🧪 The Four Test Conditions

### Test 1: Context ON + No Self-Vote
- Models see all answers with model names
- Cannot vote for themselves
- **Purpose**: Measure fairness when self-voting is prohibited

### Test 2: Context ON + Self-Vote Allowed
- Models see all answers with model names
- Can vote for anyone, including themselves
- **Purpose**: Measure explicit self-bias

### Test 3: Context OFF + Anonymous Answers + Self-Vote Allowed
- Models only see answer texts (no names, shuffled)
- Can vote for any answer
- **Purpose**: Measure implicit stylistic bias

### Test 4: Context OFF + Anonymous Answers + No Self-Vote
- Models only see answer texts (no names, shuffled)
- System checks if they accidentally voted for their own text
- **Purpose**: Test style recognition and implicit self-preference

## 📊 Metrics Collected

1. **Self-Bias Rate**: Frequency of self-voting (Tests 2 & 4)
2. **Style-Recognition Bias**: Do models vote for textually similar answers?
3. **Contextual Influence**: Voting pattern changes with/without context
4. **Overall Voting Distribution**: Which models receive the most votes

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd AI-Biased-comparison

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Add your API keys to `.env`:
   ```
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```

3. Edit `config.yaml` to configure:
   - Models to test
   - Prompts to use
   - Experiment parameters

### 3. Run Experiment

```bash
python main.py
```

The experiment will:
- Generate answers from all models for each prompt
- Run all 4 test conditions
- Calculate metrics
- Generate visualizations
- Save results to `data/`, `results/`, and `plots/` directories

## 📁 Project Structure

```
AI-Biased-comparison/
├── config.yaml              # Experiment configuration
├── requirements.txt         # Python dependencies
├── main.py                 # Main experiment script
├── src/
│   ├── __init__.py
│   ├── models.py           # Data models (Answer, Vote, ExperimentRun)
│   ├── llm_client.py       # LLM API clients
│   ├── experiment.py        # Core experiment logic
│   ├── metrics.py          # Metrics calculation
│   ├── data_manager.py     # Data saving/loading
│   └── analysis.py         # Analysis and visualization
├── data/                   # Raw experiment data (JSON, CSV)
├── results/                # Calculated metrics (JSON)
└── plots/                  # Generated visualizations (PNG)
```

## 📈 Output Files

### Data Files (`data/`)
- `experiment_runs_*.json`: Complete experiment data
- `experiment_data_*.csv`: Tabular data for analysis

### Results Files (`results/`)
- `metrics_*.json`: Calculated bias metrics

### Visualizations (`plots/`)
- `self_bias_comparison.png`: Self-bias rates across tests
- `voting_distribution.png`: Vote distribution by test type
- `style_recognition.png`: Style recognition metrics

## 🔍 Analysis Questions

The experiment answers:

1. **Do models prefer their own answers?**
   - Compare Test 2 vs Test 4 self-vote rates

2. **Do models behave differently when they know authorship?**
   - Compare Test 1 vs Test 3 voting patterns

3. **Can models detect their own writing style?**
   - Analyze Test 4 self-vote attempts

4. **Which models are most biased, fair, or self-centered?**
   - Review all bias metrics

## ⚙️ Configuration Options

Edit `config.yaml` to customize:

```yaml
models:
  - name: "gpt-4"
    provider: "openai"
    api_key_env: "OPENAI_API_KEY"

prompts:
  - "Your prompt here"

experiment:
  temperature: 0.7
  max_tokens: 1000
  collect_reasoning: true
```

## 📝 Example Usage

```python
from src.experiment import Experiment
from src.models import TestType
from src.metrics import MetricsCalculator

# Initialize experiment
experiment = Experiment(models=config['models'], config=config['experiment'])

# Run a single test
answers = experiment.generate_answers("Explain quantum computing")
run = experiment.run_test("Explain quantum computing", TestType.CONTEXT_ON_SELF_VOTE, answers)

# Calculate metrics
metrics_calc = MetricsCalculator([run])
metrics = metrics_calc.calculate_all_metrics()
```

## 🛠️ Requirements

- Python 3.8+
- API keys for LLM providers (OpenAI, Anthropic, etc.)
- See `requirements.txt` for Python packages

## 📄 License

This project is designed for research purposes to study bias in LLM behavior.

## 🤝 Contributing

This is an experimental framework. Feel free to extend it with:
- Additional LLM providers
- New test conditions
- Enhanced metrics
- Better visualizations

## ⚠️ Notes

- API costs: Running experiments will incur API costs
- Rate limits: Be aware of API rate limits for your providers
- Data privacy: Ensure compliance with API provider terms of service

