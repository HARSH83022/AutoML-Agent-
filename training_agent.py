"""
Training Agent - Auto trains ML models on processed data.
Handles classification & regression + skips failing models.
"""

import pandas as pd
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, r2_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR

# ---------- Model Dictionary ----------
CLASSIFICATION_MODELS = {
    "logistic_regression": LogisticRegression(max_iter=200),
    "random_forest": RandomForestClassifier(),
    "gradient_boosting": GradientBoostingClassifier(),
    "knn": KNeighborsClassifier(),
    "svm": SVC()
}

REGRESSION_MODELS = {
    "linear_regression": LinearRegression(),
    "random_forest": RandomForestRegressor(),
    "gradient_boosting": GradientBoostingRegressor(),
    "knn": KNeighborsRegressor(),
    "svm": SVR()
}

# ---------- Detect Task ----------
def detect_task(y):
    if y.dtype == "object" or len(y.unique()) <= 20:
        return "classification"
    return "regression"

# ---------- Train Model Agent ----------
def train_model_agent(df: pd.DataFrame, target: str, model_type: str = "auto"):
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in dataset")

    X = df.drop(columns=[target])
    y = df[target]

    task = detect_task(y) if model_type == "auto" else model_type
    print(f"✅ Detected Task: {task}")

    models = CLASSIFICATION_MODELS if task == "classification" else REGRESSION_MODELS

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    best_model = None
    best_score = -999
    results = {}

    for name, model in models.items():
        try:
            # For KNN - prevent n_neighbors > samples error
            if "knn" in name and len(X_train) < 5:
                print(f"⚠️ Skipping {name} (not enough samples for KNN)")
                continue

            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            if task == "classification":
                score = f1_score(y_test, preds, average="weighted")
            else:
                score = r2_score(y_test, preds)

            results[name] = round(float(score), 4)
            print(f"✅ {name} Score: {score}")

            if score > best_score:
                best_model = model
                best_score = score
                best_model_name = name

        except Exception as e:
            print(f"❌ Skipping {name}: {e}")

    # Save best model
    os.makedirs("./models", exist_ok=True)
    model_path = f"./models/best_model_{best_model_name}.joblib"
    joblib.dump(best_model, model_path)

    print(f"🏆 Best Model: {best_model_name} | Score: {best_score}")

    return {
        "task": task,
        "best_model": best_model_name,
        "best_score": round(float(best_score), 4),
        "scores": results,
        "model_uri": model_path
    }


if __name__ == "__main__":
    print("⚙️ Training Agent Ready — Call train_model_agent(df, target)")
