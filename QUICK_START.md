# AutoML Platform - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (2 min)
```bash
cd automl-agent
pip install -r requirements.txt
```

### Step 2: Start the Server (30 sec)
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Step 3: Open Dashboard (10 sec)
Open browser to: **http://localhost:8000/dashboard**

### Step 4: Run Your First ML Pipeline (2 min)
1. Enter problem statement: "Predict loan default"
2. Click "Start Run"
3. Watch the magic happen!

## 📊 What Happens Automatically

1. **Problem Understanding** - Parses your natural language description
2. **Data Acquisition** - Finds or generates appropriate dataset
3. **Data Preprocessing** - Cleans, encodes, and engineers features
4. **Model Training** - Trains multiple ML models (XGBoost, LightGBM, RF, etc.)
5. **Evaluation** - Computes metrics and generates leaderboard
6. **Deployment** - Creates deployment artifacts

## 🎯 Example Problem Statements

Try these:
- "Predict customer churn based on usage patterns"
- "Forecast house prices using property features"
- "Classify loan default risk from applicant data"
- "Predict employee attrition from HR data"
- "Estimate insurance claims from customer profiles"

## 🔧 Optional: Configure LLM (Better Results)

Edit `.env` file:
```bash
LLM_MODE=openai  # or anthropic, gemini
OPENAI_API_KEY=your_key_here
```

**Note**: System works without LLM using rule-based fallbacks!

## 📁 Where Are My Results?

All artifacts saved to `artifacts/` directory:
- `{run_id}_best_model.pkl` - Trained model
- `{run_id}_train.npz` - Training data
- `{run_id}_test.npz` - Test data
- `{run_id}_transformer.joblib` - Preprocessing pipeline
- `{run_id}_evaluation.json` - Metrics and results
- `{run_id}_log.txt` - Execution logs

## 🐛 Troubleshooting

**Server won't start?**
```bash
# Check if port is in use
netstat -ano | findstr :8000

# Use different port
python -m uvicorn app.main:app --port 8001
```

**Dependencies failing?**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -v -r requirements.txt
```

**Training fails?**
- Check logs in `artifacts/{run_id}_log.txt`
- Verify dataset format (CSV with headers)
- Ensure target column exists

## 🎓 Next Steps

1. **Read Full Documentation**: See [README.md](README.md)
2. **Check Implementation Status**: See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
3. **Run Tests**: `python test_system.py`
4. **Explore API**: Visit http://localhost:8000/docs

## 💡 Pro Tips

- Start with small datasets (<10k rows) for faster results
- Use `training_budget_minutes: 1` for quick tests
- Check `/status/{run_id}` endpoint for real-time progress
- Download artifacts from `/artifacts/{filename}` endpoint

## 🎉 You're Ready!

The system is now running. Start building ML models with natural language!

---

**Need Help?** Check the full [README.md](README.md) or open an issue.
