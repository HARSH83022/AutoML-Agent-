"""
Test script to demonstrate dataset selection logging
"""
import os
os.environ["LLM_MODE"] = "none"  # Disable LLM for quick test

from app.agents.data_agent import get_or_find_dataset

# Test problem statement
ps = {
    "raw_text": "Predict customer churn based on usage patterns",
    "task_type": "classification",
    "domain": "business",
    "keywords": ["customer", "churn", "retention"]
}

user = {}  # No user upload

print("\n" + "="*60)
print("TESTING DATASET ACQUISITION LOGGING")
print("="*60)

try:
    csv_path = get_or_find_dataset(
        run_id="test_logging",
        ps=ps,
        user=user
    )
    
    print(f"\n✅ Test completed successfully!")
    print(f"Final dataset path: {csv_path}")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
