#!/usr/bin/env python3
"""
Test the full Kaggle flow as it would happen in a real ML run
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, 'app')

print("=" * 60)
print("🧪 TESTING FULL KAGGLE FLOW")
print("=" * 60)

from app.agents.data_agent import get_or_find_dataset

# Simulate different problem statements
test_cases = [
    {
        "name": "Iris Classification",
        "ps": {
            "raw_text": "Classify iris flowers based on sepal and petal measurements",
            "task_type": "classification",
            "domain": "iris flower",
            "keywords": ["iris", "flower", "classification"]
        }
    },
    {
        "name": "Diabetes Prediction",
        "ps": {
            "raw_text": "Predict diabetes in patients based on medical measurements",
            "task_type": "classification",
            "domain": "diabetes health",
            "keywords": ["diabetes", "health", "prediction"]
        }
    },
    {
        "name": "General Classification",
        "ps": {
            "raw_text": "Build a classification model for tabular data",
            "task_type": "classification",
            "domain": "general",
            "keywords": ["classification", "tabular"]
        }
    }
]

for i, test_case in enumerate(test_cases):
    print(f"\n{'='*60}")
    print(f"TEST CASE {i+1}: {test_case['name']}")
    print("=" * 60)
    print(f"Problem: {test_case['ps']['raw_text']}")
    print(f"Domain: {test_case['ps']['domain']}")
    print()
    
    try:
        result = get_or_find_dataset(
            run_id=f"test_run_{i+1}",
            ps=test_case['ps'],
            user={}
        )
        
        if result:
            print(f"\n{'='*60}")
            print(f"✅ SUCCESS!")
            print("=" * 60)
            print(f"Source: {result.get('source')}")
            print(f"Dataset: {result.get('source_name')}")
            print(f"Path: {result.get('dataset_path')}")
            if result.get('source_url'):
                print(f"URL: {result.get('source_url')}")
            
            # Verify file exists
            if os.path.exists(result['dataset_path']):
                import pandas as pd
                df = pd.read_csv(result['dataset_path'], nrows=5)
                print(f"\nDataset Preview:")
                print(f"  Shape: {df.shape}")
                print(f"  Columns: {list(df.columns)[:5]}")
                
                # Clean up test file
                try:
                    import shutil
                    download_dir = os.path.dirname(result['dataset_path'])
                    if f"test_run_{i+1}" in download_dir:
                        shutil.rmtree(download_dir)
                        print(f"\n✅ Cleaned up test files")
                except:
                    pass
                
                if result.get('source') == 'Kaggle':
                    print("\n" + "=" * 60)
                    print("🎉 KAGGLE INTEGRATION WORKING!")
                    print("=" * 60)
                    print("\nYour AutoML platform will now use real Kaggle datasets!")
                    print("Test completed successfully.")
                    sys.exit(0)
            else:
                print(f"⚠️ File not found: {result['dataset_path']}")
        else:
            print(f"❌ No dataset found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("⚠️ TESTS COMPLETED")
print("=" * 60)
print("\nIf you see 'Kaggle' as the source above, integration is working!")
print("If you see 'Synthetic', check the logs for errors.")
