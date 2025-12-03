"""
Test script to diagnose Kaggle and HuggingFace data collection issues
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("DATA SOURCE DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Check environment variables
print("\n1. CHECKING ENVIRONMENT VARIABLES")
print("-" * 60)
kaggle_user = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")
hf_token = os.getenv("HF_TOKEN")

print(f"KAGGLE_USERNAME: {'✓ Set' if kaggle_user else '✗ Not set'}")
print(f"KAGGLE_KEY: {'✓ Set' if kaggle_key else '✗ Not set'}")
print(f"HF_TOKEN: {'✓ Set' if hf_token else '✗ Not set (optional)'}")

# Test 2: Check if Kaggle library is installed
print("\n2. CHECKING KAGGLE LIBRARY")
print("-" * 60)
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    print("✓ Kaggle library installed")
    
    # Try to authenticate
    try:
        api = KaggleApi()
        api.authenticate()
        print("✓ Kaggle authentication successful")
        
        # Try a simple search
        try:
            datasets = api.dataset_list(search="iris", page=1, max_size=3)
            print(f"✓ Kaggle search working - Found {len(datasets)} datasets")
            for ds in datasets[:3]:
                print(f"  - {ds.ref}")
        except Exception as e:
            print(f"✗ Kaggle search failed: {e}")
            
    except Exception as e:
        print(f"✗ Kaggle authentication failed: {e}")
        print("\nPossible solutions:")
        print("1. Check KAGGLE_USERNAME and KAGGLE_KEY in .env file")
        print("2. Or create ~/.kaggle/kaggle.json with:")
        print('   {"username":"your_username","key":"your_key"}')
        
except ImportError as e:
    print(f"✗ Kaggle library not installed: {e}")
    print("\nInstall with: pip install kaggle")

# Test 3: Check if HuggingFace library is installed
print("\n3. CHECKING HUGGINGFACE LIBRARY")
print("-" * 60)
try:
    from huggingface_hub import list_datasets
    print("✓ HuggingFace Hub library installed")
    
    # Try a simple search
    try:
        datasets = list(list_datasets(search="iris", limit=3))
        print(f"✓ HuggingFace search working - Found {len(datasets)} datasets")
        for ds in datasets[:3]:
            dataset_id = ds.id if hasattr(ds, 'id') else str(ds)
            print(f"  - {dataset_id}")
    except Exception as e:
        print(f"✗ HuggingFace search failed: {e}")
        
except ImportError as e:
    print(f"✗ HuggingFace Hub library not installed: {e}")
    print("\nInstall with: pip install huggingface-hub")

# Test 4: Check if datasets library is installed
print("\n4. CHECKING DATASETS LIBRARY")
print("-" * 60)
try:
    from datasets import load_dataset
    print("✓ Datasets library installed")
    
    # Try loading a small dataset
    try:
        print("  Testing dataset load (this may take a moment)...")
        ds = load_dataset("scikit-learn/iris", split="train")
        print(f"✓ Dataset loading works - Loaded {len(ds)} rows")
    except Exception as e:
        print(f"✗ Dataset loading failed: {e}")
        
except ImportError as e:
    print(f"✗ Datasets library not installed: {e}")
    print("\nInstall with: pip install datasets")

# Test 5: Check UCI access
print("\n5. CHECKING UCI ML REPOSITORY ACCESS")
print("-" * 60)
try:
    import requests
    print("✓ Requests library installed")
    
    # Try accessing UCI
    try:
        url = "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✓ UCI repository accessible - Got {len(response.text)} bytes")
        else:
            print(f"✗ UCI repository returned status {response.status_code}")
    except Exception as e:
        print(f"✗ UCI repository access failed: {e}")
        
except ImportError:
    print("✗ Requests library not installed")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("\nIf you see ✗ marks above, those data sources won't work.")
print("Follow the suggested solutions to fix them.")
print("\nTo install all required libraries:")
print("  pip install -r requirements.txt")
print("\nTo configure Kaggle:")
print("  1. Set KAGGLE_USERNAME and KAGGLE_KEY in .env file")
print("  2. Or create ~/.kaggle/kaggle.json")
print("\n" + "=" * 60)
