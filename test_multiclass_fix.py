"""
Test script to verify multiclass classification fix
"""
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
import os

# Create test data
print("Loading Iris dataset (multiclass)...")
iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Save as npz
os.makedirs("artifacts", exist_ok=True)
np.savez("artifacts/test_train.npz", X=X_train, y=y_train)
np.savez("artifacts/test_test.npz", X=X_test, y=y_test)

print(f"Train shape: {X_train.shape}, Classes: {np.unique(y_train)}")
print(f"Test shape: {X_test.shape}, Classes: {np.unique(y_test)}")

# Test the automl agent
from app.agents.automl_agent import run_automl

ps = {
    "raw_text": "Classify iris flowers into 3 species based on measurements",
    "task_type": "classification"
}

preferences = {
    "training_budget_minutes": 1,
    "primary_metric": "f1"  # This should auto-convert to macro_f1 for multiclass
}

print("\nRunning AutoML...")
try:
    result = run_automl(
        run_id="test_multiclass",
        train_npz_path="artifacts/test_train.npz",
        ps=ps,
        preferences=preferences
    )
    print("\n✅ SUCCESS!")
    print(f"Model saved to: {result['model_path']}")
    print(f"Settings used: {result['automl_settings']}")
    print(f"Task type: {result['task_type']}")
    
    # Test prediction
    import joblib
    model = joblib.load(result['model_path'])
    test_data = np.load("artifacts/test_test.npz")
    predictions = model.predict(test_data['X'])
    print(f"\n✅ Model can predict! Sample predictions: {predictions[:5]}")
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
