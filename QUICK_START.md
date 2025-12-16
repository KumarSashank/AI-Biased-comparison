# Quick Start Guide: How to Run the Experiment

## 🚀 How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Keys
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API keys:
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...
# DEEPSEEK_API_KEY=...
# MISTRAL_API_KEY=...
```

### Step 3: Run the Experiment
```bash
python main.py
```

This will run the full experiment with all 4 test conditions for all prompts.

### Quick Test (Optional)
To test with a single prompt first:
```bash
python run_experiment.py
```

---

## 📋 What the Experiment Does

### Phase 1: Answer Generation
For each prompt in `config.yaml`:
- **Every LLM generates an answer** to the same prompt
- Example: "Explain quantum computing"
  - GPT-3.5 generates: "Quantum computing is..."
  - Gemini generates: "Quantum computing uses..."
  - DeepSeek generates: "Quantum computing..."
  - Mistral generates: "Quantum computing..."

### Phase 2: Voting (4 Different Tests)

#### **Test 1: Context ON + No Self-Vote**
- Each LLM sees **all answers with model names**
- Example prompt shown to GPT-3.5:
  ```
  Answer 1 (by gpt-3.5-turbo): [GPT's answer]
  Answer 2 (by gemini-pro): [Gemini's answer]
  Answer 3 (by deepseek-chat): [DeepSeek's answer]
  Answer 4 (by open-mistral-7b): [Mistral's answer]
  
  Rules:
  - You are gpt-3.5-turbo
  - You CANNOT vote for your own answer
  - Choose the best answer (1-4)
  ```
- **Purpose**: Measure fairness when self-voting is prohibited

#### **Test 2: Context ON + Self-Vote Allowed**
- Same as Test 1, but **self-voting is allowed**
- **Purpose**: Measure explicit self-bias (do they vote for themselves?)

#### **Test 3: Context OFF + Anonymous + Self-Vote Allowed**
- Each LLM sees **only the answer texts** (no names, shuffled order)
- Example:
  ```
  Answer 1: [Some answer text]
  Answer 2: [Some answer text]
  Answer 3: [Some answer text]
  Answer 4: [Some answer text]
  
  Rules:
  - The answers are anonymous
  - Choose the best answer (1-4)
  ```
- **Purpose**: Measure implicit stylistic bias (do they prefer answers that "sound like them"?)

#### **Test 4: Context OFF + Anonymous + No Self-Vote**
- Same as Test 3, but system **checks if they accidentally voted for their own text**
- **Purpose**: Test style recognition (can they recognize their own writing?)

---

## 🧪 What We're Testing

### 1. **Self-Bias**
- **Question**: Do models prefer their own answers?
- **How**: Compare self-vote rates in Test 2 vs Test 4
- **Metric**: Self-vote percentage

### 2. **Evaluator Bias**
- **Question**: Do models show preference based on model identity?
- **How**: Compare voting patterns when names are visible vs hidden
- **Metric**: Vote distribution changes

### 3. **Style-Recognition Bias**
- **Question**: Can models recognize their own writing style?
- **How**: In anonymous tests, do they vote for textually similar answers?
- **Metric**: Style similarity matching rate

### 4. **Context-Induced Bias**
- **Question**: Does knowing authorship change voting patterns?
- **How**: Compare Test 1 vs Test 3, Test 2 vs Test 4
- **Metric**: Vote change rate when context is removed

---

## 📊 How Results Appear

### During Execution
You'll see a progress bar:
```
Running experiments: 100%|████████| 12/12 [05:23<00:00]
```

### After Completion

#### 1. **Console Output**
A summary report is printed:
```
================================================================================
LLM VOTING EXPERIMENT - SUMMARY REPORT
================================================================================

1. SELF-BIAS ANALYSIS
--------------------------------------------------------------------------------
Test 2 (Context ON + Self-Vote Allowed):
  gpt-3.5-turbo: 25.0% self-vote rate
  gemini-pro: 33.3% self-vote rate
  ...

2. STYLE-RECOGNITION BIAS
--------------------------------------------------------------------------------
gpt-3.5-turbo:
  Voted for most similar answer: 50.0%
  Self-recognition attempts: 25.0%
...
```

#### 2. **Data Files** (`data/` directory)
- `experiment_runs_YYYYMMDD_HHMMSS.json` - Complete raw data
- `experiment_data_YYYYMMDD_HHMMSS.csv` - Tabular format for analysis

**CSV columns:**
- `prompt` - The question asked
- `test_type` - Which test (test_1, test_2, test_3, test_4)
- `voter_model` - Which model voted
- `voted_for_model` - Which model they voted for
- `is_self_vote` - True/False
- `is_violation` - Did they violate instructions?
- `recognized_own_style` - Did they recognize their style? (Test 4)

#### 3. **Metrics Files** (`results/` directory)
- `metrics_YYYYMMDD_HHMMSS.json` - Calculated bias metrics

**Contains:**
```json
{
  "self_bias_test2": {
    "gpt-3.5-turbo": 25.0,
    "gemini-pro": 33.3,
    ...
  },
  "self_bias_test4": {...},
  "style_recognition": {...},
  "contextual_influence": {...},
  "voting_distribution": {...}
}
```

#### 4. **Visualization Plots** (`plots/` directory)
- `self_bias_comparison.png` - Bar chart comparing self-bias across tests
- `voting_distribution.png` - 4-panel chart showing vote distribution per test
- `style_recognition.png` - Style recognition metrics

---

## 📈 Understanding the Results

### Example Analysis

**High Self-Bias (Bad):**
- Model votes for itself 80% of the time
- Indicates strong self-preference

**Low Self-Bias (Good):**
- Model votes for itself 20% of the time (random would be ~25% with 4 models)
- Indicates fair evaluation

**Style Recognition:**
- If a model votes for the most similar answer 70% of the time in anonymous tests
- Shows they can recognize stylistic patterns

**Context Influence:**
- If votes change 60% when context is removed
- Shows models are influenced by knowing who wrote what

---

## 🔍 Example Workflow

1. **Run experiment**: `python main.py`
2. **Check console** for summary
3. **Open CSV** in Excel/Python for detailed analysis
4. **View plots** in `plots/` directory
5. **Compare metrics** in `results/metrics_*.json`

---

## ⚙️ Customization

Edit `config.yaml` to:
- Change prompts
- Adjust temperature/max_tokens
- Add/remove models
- Modify test parameters

---

## 💡 Tips

- Start with `run_experiment.py` to test one prompt first
- Check API costs before running full experiment
- Results are saved automatically - you can analyze later
- CSV files are easy to import into analysis tools

