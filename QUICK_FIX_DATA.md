# Quick Fix: Kaggle & HuggingFace Data Collection

## 🔍 Problem
System is not collecting datasets from Kaggle or HuggingFace - always using synthetic data.

## ⚡ Quick Fix (3 Steps)

### Step 1: Install Libraries
```bash
cd automl-agent
pip install -r requirements.txt
```

### Step 2: Setup Kaggle
```bash
python setup_kaggle.py
```

### Step 3: Test
```bash
python test_data_sources.py
```

## ✅ Expected Result

You should see:
```
✓ Kaggle library installed
✓ Kaggle authentication successful
✓ Kaggle search working - Found 3 datasets
✓ HuggingFace search working - Found 3 datasets
```

## 🎯 Verify It's Working

1. **Restart backend:**
   ```bash
   python start_server.py
   ```

2. **Start a new run** from the frontend

3. **Check backend logs** - you should see:
   ```
   [data_agent] Searching Kaggle: 'your query'
   [data_agent] Found X Kaggle datasets
   ✅ DATASET SELECTED: Kaggle
   ```

4. **Check Run Details page** - should show:
   - Source: "Kaggle" (not "Synthetic")
   - Dataset Name: actual dataset name
   - Link to dataset source

## 🚨 If Still Not Working

See detailed guide: **FIX_DATA_COLLECTION.md**

Or run diagnostics:
```bash
python test_data_sources.py
```

## 📝 Your Credentials

Already configured in `.env`:
```
KAGGLE_USERNAME=ramyasharma10
KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921
```

These should work! Just need to install libraries and run setup.
