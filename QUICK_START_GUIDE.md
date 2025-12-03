# 🚀 Quick Start Guide - AutoML Platform

## Complete Setup in 5 Minutes

### Prerequisites

1. **Python 3.8+** installed
2. **Node.js 16+** installed (for frontend)
3. **API Keys** configured in `.env` file

---

## Option 1: Automated Start (Recommended)

### Windows:

#### Terminal 1 - Start Backend:
```bash
cd automl-agent
run.bat
```

#### Terminal 2 - Start Frontend:
```bash
cd automl-agent\frontend
start.bat
```

### Mac/Linux:

#### Terminal 1 - Start Backend:
```bash
cd automl-agent
chmod +x run.sh
./run.sh
```

#### Terminal 2 - Start Frontend:
```bash
cd automl-agent/frontend
npm install  # First time only
npm run dev
```

---

## Option 2: Manual Start

### Step 1: Start Backend

```bash
# Navigate to project
cd automl-agent

# Activate virtual environment
venv\Scripts\activate          # Windows
# OR
source venv/bin/activate       # Mac/Linux

# Install dependencies (first time only)
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --port 8000
```

**Backend will be available at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:8000/dashboard

### Step 2: Start Frontend (New Terminal)

```bash
# Navigate to frontend
cd automl-agent/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Frontend will be available at:**
- http://localhost:3000

---

## ✅ Verify Everything is Working

### 1. Check Backend Health

Open browser: http://localhost:8000/checkllm

Should see:
```json
{
  "ok": true,
  "LLM_MODE": "openai",
  "response": "OK"
}
```

### 2. Check Frontend

Open browser: http://localhost:3000

Should see:
- Homepage with "AutoML No-Code Platform" title
- "Start New Run" button
- Navigation menu

### 3. Test Complete Flow

1. Click **"Start New Run"**
2. Enter problem statement: `"Predict customer churn"`
3. Set training budget: `5 minutes`
4. Click **"Start Run"**
5. Watch real-time progress!

---

## 🎯 What Happens Next?

The system will automatically:

1. ✅ **Parse Problem** (5-10 seconds)
   - Understands your ML task
   - Identifies task type (classification/regression)

2. ✅ **Find Dataset** (10-30 seconds)
   - Searches Kaggle/HuggingFace
   - Downloads relevant dataset
   - Or uses your uploaded file

3. ✅ **Preprocess Data** (10-20 seconds)
   - Cleans missing values
   - Encodes categorical features
   - Splits train/test sets

4. ✅ **Train Models** (2-5 minutes)
   - Trains 5-10 different algorithms:
     - XGBoost
     - LightGBM
     - Random Forest
     - Logistic Regression
     - Neural Networks
     - etc.

5. ✅ **Evaluate & Display** (5-10 seconds)
   - Calculates metrics (F1, Precision, Recall, ROC AUC)
   - Generates confusion matrix
   - Creates ROC curve
   - Produces model card

---

## 📊 What You'll See in Frontend

### During Run:
- ⏳ Status: "Running"
- 📍 Current Phase: "Training models..."
- 📝 Live Logs: Real-time updates
- 🔄 Auto-refresh every 2 seconds

### After Completion:
- ✅ Status: "Completed"
- 📈 **Metrics Table:**
  ```
  F1 Score:    0.9234
  Precision:   0.9345
  Recall:      0.8967
  ROC AUC:     0.9456
  Accuracy:    0.9234
  ```

- 📊 **Visualizations:**
  - Confusion Matrix (image)
  - ROC Curve (image)
  - Feature Importance (if available)

- 📥 **Download Buttons:**
  - Trained Model (.pkl)
  - Predictions (.csv)
  - Evaluation Report (.json)
  - All Plots (.png)

---

## 🔧 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError`
```bash
pip install -r requirements.txt
```

**Problem:** `LLM API Error`
- Check `.env` file has correct API keys
- Verify `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

**Problem:** Port 8000 already in use
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Frontend Issues

**Problem:** `npm: command not found`
- Install Node.js from https://nodejs.org/

**Problem:** Dependencies not installing
```bash
cd automl-agent/frontend
npm cache clean --force
npm install
```

**Problem:** Can't connect to backend
- Ensure backend is running on port 8000
- Check `vite.config.js` proxy settings

**Problem:** Port 3000 already in use
```bash
npm run dev -- --port 3001
```

---

## 🎨 Advanced Usage

### Custom Dataset

1. Place CSV file in `automl-agent/data/` folder
2. In frontend, upload the file when starting a run
3. System will use your data instead of searching

### Adjust Training Time

- Increase `training_budget_minutes` for better models
- Decrease for faster results
- Recommended: 5-10 minutes for good results

### Choose Different Metrics

Available metrics:
- **Classification:** F1, Accuracy, ROC AUC, Precision, Recall
- **Regression:** R², MSE, MAE, RMSE

---

## 📱 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main UI |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API docs |
| **Dashboard** | http://localhost:8000/dashboard | Built-in HTML dashboard |
| **Health Check** | http://localhost:8000/checkllm | Verify LLM connection |

---

## 🎉 Example Problem Statements

Try these to get started:

1. **Classification:**
   - "Predict customer churn based on usage patterns"
   - "Classify emails as spam or not spam"
   - "Detect fraudulent credit card transactions"
   - "Predict loan default risk"

2. **Regression:**
   - "Predict house prices based on location and features"
   - "Forecast sales for next quarter"
   - "Estimate delivery time for orders"
   - "Predict energy consumption"

---

## 🆘 Still Having Issues?

1. **Check Logs:**
   - Backend: Terminal running `uvicorn`
   - Frontend: Browser console (F12)
   - Run logs: `automl-agent/artifacts/`

2. **Verify Setup:**
   ```bash
   # Backend
   python --version  # Should be 3.8+
   pip list | grep fastapi
   
   # Frontend
   node --version    # Should be 16+
   npm --version
   ```

3. **Test Individual Components:**
   ```bash
   # Test backend only
   python automl-agent/test_system.py
   
   # Test LLM connection
   python automl-agent/test_llm_client.py
   ```

---

## 🚀 You're All Set!

**Backend Running:** ✅ http://localhost:8000  
**Frontend Running:** ✅ http://localhost:3000

**Now go build some ML models!** 🎯

The entire pipeline is automated - just describe your problem and let the AI agents handle the rest! 🤖✨
