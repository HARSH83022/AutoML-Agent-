#!/usr/bin/env python3
"""
Test with known public Kaggle datasets
"""
import os
import sys
from dotenv import load_dotenv
import traceback

load_dotenv()

from kaggle.api.kaggle_api_extended import KaggleApi
import json
from pathlib import Path

# Setup credentials
kaggle_username = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")

kaggle_dir = Path.home() / ".kaggle"
kaggle_json_path = kaggle_dir / "kaggle.json"
kaggle_dir.mkdir(exist_ok=True)
credentials = {"username": kaggle_username, "key": kaggle_key}
with open(kaggle_json_path, 'w') as f:
    json.dump(credentials, f, indent=2)
try:
    os.chmod(kaggle_json_path, 0o600)
except:
    pass

print("=" * 60)
print("🔍 TESTING WITH KNOWN PUBLIC DATASETS")
print("=" * 60)

api = KaggleApi()
api.authenticate()
print("✅ Authenticated")

# Try well-known competition datasets (these are usually accessible)
test_datasets = [
    "uciml/iris",  # Classic dataset
    "uciml/pima-indians-diabetes-database",  # Another classic
    "uciml/breast-cancer-wisconsin-data",  # Well-known dataset
]

for dataset_ref in test_datasets:
    print(f"\n{'='*60}")
    print(f"Testing: {dataset_ref}")
    print("=" * 60)
    
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Downloading to: {temp_dir}")
            
            # Try download
            api.dataset_download_files(dataset_ref, path=temp_dir, unzip=True)
            
            print(f"✅ Download completed!")
            
            # List files
            files = []
            for root, dirs, filenames in os.walk(temp_dir):
                for filename in filenames:
                    full_path = os.path.join(root, filename)
                    size = os.path.getsize(full_path)
                    files.append((filename, size))
                    print(f"   - {filename} ({size} bytes)")
            
            # Check for CSV
            csv_files = [f for f, s in files if f.lower().endswith('.csv')]
            if csv_files:
                print(f"\n✅ Found CSV files: {', '.join(csv_files)}")
                
                # Try to read first CSV
                first_csv = csv_files[0]
                csv_path = None
                for root, dirs, filenames in os.walk(temp_dir):
                    for filename in filenames:
                        if filename == first_csv:
                            csv_path = os.path.join(root, filename)
                            break
                
                if csv_path:
                    print(f"\nReading: {csv_path}")
                    import pandas as pd
                    df = pd.read_csv(csv_path)
                    print(f"✅ CSV is valid!")
                    print(f"   Shape: {df.shape}")
                    print(f"   Columns: {list(df.columns)}")
                    print(f"   First few rows:")
                    print(df.head())
                    
                    print("\n" + "=" * 60)
                    print("✅ SUCCESS! Kaggle download works!")
                    print("=" * 60)
                    print(f"\nDataset '{dataset_ref}' downloaded successfully!")
                    print("Kaggle integration is working.")
                    sys.exit(0)
            else:
                print(f"⚠️ No CSV files found")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        if "404" in str(e):
            print("   This dataset might not exist or requires special access")
        elif "403" in str(e):
            print("   This dataset requires accepting terms or competition rules")
        print()

print("\n" + "=" * 60)
print("⚠️ All test datasets failed")
print("=" * 60)
print("\nThis might mean:")
print("1. Your Kaggle account needs to accept terms of service")
print("2. You need to join competitions to access their datasets")
print("3. There might be API rate limiting")
print("\nVisit https://www.kaggle.com and make sure you're logged in")
print("and have accepted all terms of service.")
