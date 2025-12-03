#!/usr/bin/env python3
"""
Test Kaggle integration with the data agent
"""
import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add app to path
sys.path.insert(0, 'app')

print("=" * 60)
print("🧪 TESTING KAGGLE INTEGRATION WITH DATA AGENT")
print("=" * 60)

# Import data agent functions
from app.agents.data_agent import _search_kaggle, _download_kaggle_dataset, _validate_dataset

# Test 1: Search
print("\n1. TESTING KAGGLE SEARCH")
print("-" * 40)

test_queries = ["titanic", "diabetes", "classification"]

for query in test_queries:
    print(f"\n🔍 Searching for: '{query}'")
    results = _search_kaggle("test_run", query, max_results=3)
    
    if results:
        print(f"✅ Found {len(results)} datasets:")
        for i, result in enumerate(results):
            print(f"   {i+1}. {result['ref']}")
            print(f"      Title: {result['title']}")
            print(f"      URL: {result['url']}")
        
        # Test 2: Download first result
        print(f"\n2. TESTING DOWNLOAD")
        print("-" * 40)
        first_dataset = results[0]
        print(f"📥 Downloading: {first_dataset['ref']}")
        
        csv_path = _download_kaggle_dataset("test_run", first_dataset['ref'])
        
        if csv_path:
            print(f"✅ Download successful: {csv_path}")
            
            # Test 3: Validate
            print(f"\n3. TESTING VALIDATION")
            print("-" * 40)
            is_valid, summary = _validate_dataset("test_run", csv_path)
            
            if is_valid:
                print(f"✅ Dataset is valid!")
                print(f"   Rows: {summary.get('n_rows')}")
                print(f"   Columns: {summary.get('n_cols')}")
                print(f"   Column names: {', '.join(summary.get('columns', [])[:5])}")
                
                # Clean up
                try:
                    import shutil
                    import os
                    # Remove the downloaded directory
                    download_dir = os.path.dirname(csv_path)
                    if "test_run_kaggle" in download_dir:
                        shutil.rmtree(download_dir)
                        print(f"\n✅ Cleaned up test files")
                except:
                    pass
                
                print("\n" + "=" * 60)
                print("✅ ALL TESTS PASSED!")
                print("=" * 60)
                print("\nKaggle integration is working correctly!")
                print("Your AutoML runs will now fetch real datasets from Kaggle.")
                sys.exit(0)
            else:
                print(f"❌ Dataset validation failed")
        else:
            print(f"❌ Download failed")
    else:
        print(f"⚠️ No results for '{query}'")

print("\n" + "=" * 60)
print("⚠️ TESTS INCOMPLETE")
print("=" * 60)
print("Could not complete all tests. Check the errors above.")
