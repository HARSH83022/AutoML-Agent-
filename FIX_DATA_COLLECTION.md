# Fix Kaggle & HuggingFace Data Collection

## Problem
The system is not collecting datasets from Kaggle or HuggingFace - it's falling back to synthetic data generation.

## Quick Diagnosis

Run this test script to see what's wrong:

```bash
cd automl-agent
python test_data_sources.py
```

This will show you which data sources are working and which aren't.

---

## Solution 1: Install Required Libraries

### Step 1: Install all dependencies

```bash
cd automl-agent
pip install -r requirements.txt
```

### Step 2: Verify installation

```bash
pip list | findstr kaggle        # Windows
pip list | grep kaggle           # Mac/Linux

pip list | findstr huggingface   # Windows
pip list | grep huggingface      # Mac/Linux
```

You should see:
- `kaggle`
- `huggingface-hub`
- `datasets`

---

## Solution 2: Configure Kaggle Credentials

### Option A: Automatic Setup (Recommended)

Run this script to automatically configure Kaggle:

```bash
cd automl-agent
python setup_kaggle.py
```

This will:
1. Read credentials from your `.env` file
2. Create `~/.kaggle/kaggle.json`
3. Test the connection

### Option B: Manual Setup

#### Step 1: Get your Kaggle API credentials

1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New Token"
4. Download `kaggle.json`

#### Step 2: Configure credentials

**Method 1: Using .env file (Current)**

Your `.env` file already has:
```bash
KAGGLE_USERNAME=ramyasharma10
KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921
```

**Method 2: Using kaggle.json file**

Create `~/.kaggle/kaggle.json`:

**Windows:**
```bash
mkdir %USERPROFILE%\.kaggle
echo {"username":"ramyasharma10","key":"820ef1deeb71e11c4494e16cd071e921"} > %USERPROFILE%\.kaggle\kaggle.json
```

**Mac/Linux:**
```bash
mkdir -p ~/.kaggle
echo '{"username":"ramyasharma10","key":"820ef1deeb71e11c4494e16cd071e921"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

#### Step 3: Test Kaggle connection

```bash
cd automl-agent
python -c "from kaggle.api.kaggle_api_extended import KaggleApi; api = KaggleApi(); api.authenticate(); print('✓ Kaggle works!')"
```

---

## Solution 3: Configure HuggingFace (Optional)

HuggingFace works without authentication for public datasets, but you can add a token for better access:

### Step 1: Get HuggingFace token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token (read access is enough)
3. Copy the token

### Step 2: Add to .env file

```bash
HF_TOKEN=hf_your_token_here
```

### Step 3: Test HuggingFace

```bash
python -c "from huggingface_hub import list_datasets; print(list(list_datasets(search='iris', limit=1))); print('✓ HuggingFace works!')"
```

---

## Solution 4: Fix Data Agent Code

If the libraries are installed but still not working, the data agent might need updates.

### Check data_agent.py

The data agent should have these imports:

```python
from kaggle.api.kaggle_api_extended import KaggleApi
from huggingface_hub import list_datasets
from datasets import load_dataset
```

If you see `ImportError` in the logs, the libraries aren't installed properly.

---

## Verification Steps

### Test 1: Run diagnostic script

```bash
cd automl-agent
python test_data_sources.py
```

**Expected output:**
```
1. CHECKING ENVIRONMENT VARIABLES
✓ KAGGLE_USERNAME: Set
✓ KAGGLE_KEY: Set

2. CHECKING KAGGLE LIBRARY
✓ Kaggle library installed
✓ Kaggle authentication successful
✓ Kaggle search working - Found 3 datasets

3. CHECKING HUGGINGFACE LIBRARY
✓ HuggingFace Hub library installed
✓ HuggingFace search working - Found 3 datasets

4. CHECKING DATASETS LIBRARY
✓ Datasets library installed
✓ Dataset loading works

5. CHECKING UCI ML REPOSITORY ACCESS
✓ UCI repository accessible
```

### Test 2: Start a run and check logs

1. Start backend: `python start_server.py`
2. Start a new ML run from the frontend
3. Watch the backend terminal for:

```
🔍 SEARCHING FOR DATASETS
   Search Order:
   1. User Upload
   2. Kaggle
   3. HuggingFace
   4. UCI ML Repository
   5. Synthetic (fallback)

[data_agent] Searching Kaggle: 'your search query'
[data_agent] Found 3 Kaggle datasets
[data_agent] Downloading Kaggle dataset: username/dataset-name
✅ DATASET SELECTED: Kaggle
```

### Test 3: Check run details page

After a run completes, the Run Details page should show:
- **Dataset Information** card
- **Source:** "Kaggle" or "HuggingFace" (not "Synthetic")
- **Dataset Name:** The actual dataset name
- **Link:** Clickable link to the dataset source

---

## Common Issues & Solutions

### Issue 1: "Kaggle library not installed"

**Solution:**
```bash
pip install kaggle
```

### Issue 2: "401 Unauthorized" from Kaggle

**Causes:**
- Wrong credentials
- Haven't accepted Kaggle terms of service
- API key expired

**Solutions:**
1. Verify credentials at https://www.kaggle.com/settings/account
2. Accept Kaggle's terms: https://www.kaggle.com/terms
3. Generate a new API token
4. Update `.env` file with new credentials
5. Run `python setup_kaggle.py` again

### Issue 3: "HuggingFace Hub not installed"

**Solution:**
```bash
pip install huggingface-hub datasets
```

### Issue 4: "Connection timeout" errors

**Causes:**
- Firewall blocking connections
- Network issues
- Proxy settings

**Solutions:**
1. Check internet connection
2. Try with VPN if behind corporate firewall
3. Set proxy in environment:
   ```bash
   set HTTP_PROXY=http://proxy:port    # Windows
   export HTTP_PROXY=http://proxy:port # Mac/Linux
   ```

### Issue 5: Always falls back to synthetic data

**Causes:**
- Libraries not installed
- Credentials not configured
- Search queries not matching any datasets
- All external sources failing

**Debug steps:**
1. Run `python test_data_sources.py`
2. Check backend logs for error messages
3. Look for lines like:
   ```
   [data_agent] Kaggle attempt failed: ...
   [data_agent] HuggingFace attempt failed: ...
   [data_agent] UCI attempt failed: ...
   [data_agent] ⚠️ All external sources failed, generating synthetic dataset
   ```
4. Fix the specific errors shown

### Issue 6: "No CSV files found" after Kaggle download

**Cause:** Some Kaggle datasets don't have CSV files

**Solution:** The system will automatically try the next dataset or source

---

## Testing Individual Data Sources

### Test Kaggle Only

```python
from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()

# Search for datasets
datasets = api.dataset_list(search="iris", page=1, max_size=5)
for ds in datasets:
    print(f"{ds.ref}: {ds.title}")

# Download a dataset
api.dataset_download_files("uciml/iris", path="./test_data", unzip=True)
print("Downloaded to ./test_data")
```

### Test HuggingFace Only

```python
from huggingface_hub import list_datasets
from datasets import load_dataset

# Search for datasets
datasets = list(list_datasets(search="iris", limit=5))
for ds in datasets:
    print(ds.id if hasattr(ds, 'id') else str(ds))

# Load a dataset
ds = load_dataset("scikit-learn/iris", split="train")
print(f"Loaded {len(ds)} rows")
```

### Test UCI Only

```python
import requests
import pandas as pd
from io import StringIO

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
response = requests.get(url, timeout=30)

if response.status_code == 200:
    df = pd.read_csv(StringIO(response.text), header=None)
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
```

---

## Environment Variables Reference

Add these to your `.env` file:

```bash
# Kaggle (Required for Kaggle datasets)
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# HuggingFace (Optional - for better access)
HF_TOKEN=hf_your_token_here

# Data directory
DATA_DIR=data

# Synthetic data settings (fallback)
SYNTHETIC_DEFAULT_ROWS=2000
```

---

## Success Checklist

- [ ] `pip install -r requirements.txt` completed
- [ ] `python test_data_sources.py` shows all ✓ marks
- [ ] `python setup_kaggle.py` completed successfully
- [ ] Backend starts without errors
- [ ] New run shows "Searching Kaggle" in logs
- [ ] Run details page shows "Kaggle" or "HuggingFace" as source
- [ ] No "Synthetic (Generated)" datasets (unless intentional)

---

## Still Not Working?

### Collect debug information:

1. **Run diagnostic:**
   ```bash
   python test_data_sources.py > debug_output.txt
   ```

2. **Check backend logs:**
   - Look for `[data_agent]` lines
   - Copy any error messages

3. **Check installed packages:**
   ```bash
   pip list > installed_packages.txt
   ```

4. **Check environment:**
   ```bash
   # Windows
   echo %KAGGLE_USERNAME%
   echo %KAGGLE_KEY%
   
   # Mac/Linux
   echo $KAGGLE_USERNAME
   echo $KAGGLE_KEY
   ```

### Quick Reset:

If nothing works, try a complete reset:

```bash
# Reinstall Python packages
pip uninstall kaggle huggingface-hub datasets -y
pip install kaggle huggingface-hub datasets

# Reconfigure Kaggle
python setup_kaggle.py

# Test again
python test_data_sources.py
```

---

## Next Steps

Once data collection is working:

1. Start a new ML run
2. Watch the backend logs
3. Verify the dataset source in Run Details page
4. Check that the dataset is appropriate for your problem

The system will automatically:
- Search Kaggle first
- Fall back to HuggingFace if Kaggle fails
- Try UCI repository if both fail
- Generate synthetic data only as last resort

---

## Additional Resources

- **Kaggle API Docs:** https://github.com/Kaggle/kaggle-api
- **HuggingFace Datasets:** https://huggingface.co/docs/datasets
- **UCI ML Repository:** https://archive.ics.uci.edu/ml/index.php
