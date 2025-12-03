#!/usr/bin/env python3
"""
Simple Kaggle test to verify credentials and search functionality
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("🔍 TESTING KAGGLE INTEGRATION")
print("=" * 60)

# Check credentials
print("\n1. CHECKING CREDENTIALS")
print("-" * 40)
kaggle_username = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")

print(f"KAGGLE_USERNAME: {kaggle_username if kaggle_username else '❌ NOT SET'}")
print(f"KAGGLE_KEY: {'✅ SET' if kaggle_key else '❌ NOT SET'}")

if not kaggle_username or not kaggle_key:
    print("\n❌ Kaggle credentials not found in environment!")
    print("Make sure .env file has:")
    print("KAGGLE_USERNAME=your_username")
    print("KAGGLE_KEY=your_key")
    sys.exit(1)

# Test Kaggle library
print("\n2. TESTING KAGGLE LIBRARY")
print("-" * 40)
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    print("✅ Kaggle library installed")
except ImportError as e:
    print(f"❌ Kaggle library not installed: {e}")
    print("Install with: pip install kaggle")
    sys.exit(1)

# Setup credentials
print("\n3. SETTING UP CREDENTIALS")
print("-" * 40)
import json
from pathlib import Path

kaggle_dir = Path.home() / ".kaggle"
kaggle_json_path = kaggle_dir / "kaggle.json"

if not kaggle_json_path.exists():
    print(f"Creating kaggle.json at: {kaggle_json_path}")
    kaggle_dir.mkdir(exist_ok=True)
    credentials = {
        "username": kaggle_username,
        "key": kaggle_key
    }
    with open(kaggle_json_path, 'w') as f:
        json.dump(credentials, f, indent=2)
    try:
        os.chmod(kaggle_json_path, 0o600)
    except:
        pass
    print("✅ Created kaggle.json")
else:
    print(f"✅ kaggle.json already exists at: {kaggle_json_path}")

# Test authentication
print("\n4. TESTING AUTHENTICATION")
print("-" * 40)
try:
    api = KaggleApi()
    api.authenticate()
    print("✅ Kaggle authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check credentials at: https://www.kaggle.com/settings/account")
    print("2. Make sure you've accepted Kaggle's terms")
    print("3. Verify your API key is correct")
    sys.exit(1)

# Test search
print("\n5. TESTING DATASET SEARCH")
print("-" * 40)
try:
    print("Searching for 'iris' datasets...")
    datasets = api.dataset_list(search="iris", page=1, max_size=5)
    print(f"✅ Found {len(datasets)} datasets:")
    for i, ds in enumerate(datasets[:5]):
        print(f"   {i+1}. {ds.ref} - {ds.title}")
    
    if len(datasets) == 0:
        print("⚠️ No datasets found - this might indicate an issue")
        sys.exit(1)
except Exception as e:
    print(f"❌ Search failed: {e}")
    sys.exit(1)

# Test download
print("\n6. TESTING DATASET DOWNLOAD")
print("-" * 40)
if datasets:
    test_dataset = datasets[0].ref
    print(f"Attempting to download: {test_dataset}")
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            api.dataset_download_files(test_dataset, path=temp_dir, unzip=True)
            
            # Check files
            import os
            files = []
            for root, dirs, filenames in os.walk(temp_dir):
                for filename in filenames:
                    files.append(filename)
            
            print(f"✅ Download successful!")
            print(f"   Files: {', '.join(files[:5])}")
            
            # Check for CSV
            csv_files = [f for f in files if f.lower().endswith('.csv')]
            if csv_files:
                print(f"✅ Found {len(csv_files)} CSV files: {', '.join(csv_files)}")
            else:
                print("⚠️ No CSV files found")
    except Exception as e:
        print(f"❌ Download failed: {e}")

print("\n" + "=" * 60)
print("✅ KAGGLE TEST COMPLETE!")
print("=" * 60)
print("\nKaggle is working! You can now use it in your AutoML runs.")
