#!/usr/bin/env python3
"""
Detailed Kaggle test with multiple search attempts
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 DETAILED KAGGLE TEST")
print("=" * 60)

# Setup
from kaggle.api.kaggle_api_extended import KaggleApi
import json
from pathlib import Path

kaggle_username = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")

# Create credentials file
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

print(f"✅ Credentials configured for: {kaggle_username}")

# Authenticate
api = KaggleApi()
api.authenticate()
print("✅ Authentication successful")

# Try multiple search queries
print("\n" + "=" * 60)
print("TESTING MULTIPLE SEARCHES")
print("=" * 60)

search_terms = [
    "iris",
    "titanic",
    "house prices",
    "classification",
    "diabetes"
]

for term in search_terms:
    print(f"\n🔍 Searching for: '{term}'")
    print("-" * 40)
    try:
        datasets = api.dataset_list(search=term, page=1, max_size=3)
        print(f"   Found: {len(datasets)} datasets")
        for i, ds in enumerate(datasets[:3]):
            print(f"   {i+1}. {ds.ref}")
            print(f"      Title: {ds.title}")
            print(f"      Size: {ds.size}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Try listing popular datasets without search
print("\n" + "=" * 60)
print("LISTING POPULAR DATASETS (no search filter)")
print("=" * 60)
try:
    print("Getting popular datasets...")
    datasets = api.dataset_list(page=1, max_size=5)
    print(f"✅ Found {len(datasets)} datasets:")
    for i, ds in enumerate(datasets[:5]):
        print(f"   {i+1}. {ds.ref} - {ds.title}")
except Exception as e:
    print(f"❌ Error: {e}")

# Try a specific known dataset
print("\n" + "=" * 60)
print("TESTING SPECIFIC DATASET ACCESS")
print("=" * 60)
known_datasets = [
    "uciml/iris",
    "heptapod/uciml-iris",
    "arshid/iris-flower-dataset"
]

for dataset_ref in known_datasets:
    print(f"\n🔍 Trying: {dataset_ref}")
    try:
        metadata = api.dataset_metadata(dataset_ref)
        print(f"   ✅ Found! Title: {metadata.title if hasattr(metadata, 'title') else 'N/A'}")
        
        # Try to download
        print(f"   📥 Attempting download...")
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            api.dataset_download_files(dataset_ref, path=temp_dir, unzip=True)
            files = os.listdir(temp_dir)
            print(f"   ✅ Downloaded! Files: {', '.join(files)}")
            break  # Success!
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
