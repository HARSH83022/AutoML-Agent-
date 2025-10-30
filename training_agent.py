from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
import uuid, os, joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

# Optional: XGBoost support
try:
    from xgboost import XGBClassifier
    xgb_available = True
except ImportError:
    xgb_available = False

router = APIRouter()

class ModelTrainRequest(BaseModel):
    processed_csv_path: str
    target_column: str
    model_name: str = "LogisticRegression"

@router.post("/model_training")
def run_model_training(req: ModelTrainRequest):

    try:
        print("✅ Loading processed dataset...")
        df = pd.read_csv(req.processed_csv_path)

        if req.target_column not in df.columns:
            raise Exception(f"Target column '{req.target_column}' not found in dataset")

        X = df.drop(columns=[req.target_column])
        y = df[req.target_column]

        print("✅ Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        print(f"✅ Initializing model: {req.model_name}")

        if req.model_name == "LogisticRegression":
            model = LogisticRegression(max_iter=500)
        elif req.model_name == "RandomForest":
            model = RandomForestClassifier(n_estimators=200, random_state=42)
        elif req.model_name == "XGBoost":
            if not xgb_available:
                raise Exception("XGBoost not installed. Run: pip install xgboost")
            model = XGBClassifier(eval_metric="logloss")
        else:
            raise Exception("Invalid model_name. Choose: LogisticRegression / RandomForest / XGBoost")

        print("✅ Training the model...")
        model.fit(X_train, y_train)

        print("✅ Predicting...")
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)

        # Save model
        model_id = str(uuid.uuid4())
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, f"{model_id}_model.pkl")
        joblib.dump(model, model_path)

        print(f"✅ Model saved at: {model_path}")
        print(f"✅ Accuracy: {accuracy}")

        return {
            "status": "success",
            "model_id": model_id,
            "model_path": model_path,
            "accuracy": accuracy,
            "classification_report": report
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in model training: {e}")
