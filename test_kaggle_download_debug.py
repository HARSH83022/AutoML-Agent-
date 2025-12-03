#!/usr/bin/env python3
"""
Debug Kaggle download issues
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
print("🔍 DEBUG KAGGLE DOWNLOAD")
print("=" * 60)

api = KaggleApi()
api.authenticate()
print("✅ Authenticated")

# Try to download a known simple dataset
test_datasets = [
    "saragadamsaiprasad/diabetes",
    "asmaashawkey/titanic",
]

for dataset_ref in test_datasets:
    print(f"\n{'='*60}")
    print(f"Testing: {dataset_ref}")
    print("=" * 60)
    
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Download directory: {temp_dir}")
            print(f"Downloading...")
            
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
                    df = pd.read_csv(csv_path, nrows=5)
                    print(f"✅ CSV is valid!")
                    print(f"   Shape: {df.shape}")
                    print(f"   Columns: {list(df.columns)}")
                    
                    print("\n" + "=" * 60)
                    print("✅ SUCCESS! Kaggle download works!")
                    print("=" * 60)
                    sys.exit(0)
            else:
                print(f"⚠️ No CSV files found")
                print(f"Files: {[f for f, s in files]}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\nFull traceback:")
        traceback.print_exc()
        print()

print("\n" + "=" * 60)
print("❌ All downloads failed")
print("=" * 60)
