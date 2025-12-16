# 🆓 Run the Experiment for FREE (No API Costs)

## Quick Start - Mock Mode

Run the experiment **without spending any money** using simulated responses:

```bash
python main.py --mock
```

Or use the mock config directly:
```bash
python main.py config.mock.yaml
```

## What is Mock Mode?

Mock mode uses **simulated responses** instead of real API calls. This allows you to:
- ✅ Test the entire framework
- ✅ See how results are generated
- ✅ Understand the experiment flow
- ✅ **Spend $0.00**

## Mock Models

The mock config includes 4 simulated models:
- `mock-model-a` - Detailed, comprehensive responses
- `mock-model-b` - Concise, practical responses  
- `mock-model-c` - Analytical, nuanced responses
- `mock-model-d` - Clear, example-based responses

Each model has different "personalities" and voting patterns, so you can see how bias metrics work!

## Example Output

```bash
💰 Running in FREE mock mode - no API costs!
Loading configuration from config.mock.yaml...
🧪 Running in MOCK MODE (no API costs, simulated responses)
================================================================================
Initializing experiment...

Running experiment with 3 prompts...
Models: 4
Test conditions: 4
Total runs: 12

Running experiments: 100%|████████| 12/12 [00:01<00:00]

[Results saved...]
```

## Switching to Real APIs

When you're ready to use real APIs:

1. Update `config.yaml` with your models
2. Add API keys to `.env`
3. Run: `python main.py`

## Benefits of Mock Mode

1. **Learn the framework** - Understand how everything works
2. **Test your analysis** - Practice analyzing results
3. **No costs** - Perfect for development and learning
4. **Fast** - Instant responses (no API wait times)

---

**Note**: Mock responses are deterministic (same input = same output) but varied enough to demonstrate bias detection in action!

