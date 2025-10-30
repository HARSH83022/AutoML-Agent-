# # model_selection_agent.py
# import pandas as pd
# import joblib
# import os
# import uuid
# from sklearn.model_selection import train_test_split
# from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score

# def model_selection(data):
#     """
#     Model Selection Agent
#     - Takes in dictionary containing processed CSV path and target column
#     - Loads preprocessed data
#     - Selects best model based on simple evaluation
#     - Returns model performance summary and saved model path
#     """
#     try:
#         csv_path = data.get("processed_csv_path")
#         target_col = data.get("target_column")

#         if not csv_path or not os.path.exists(csv_path):
#             raise FileNotFoundError(f"Processed CSV not found at {csv_path}")

#         df = pd.read_csv(csv_path)
#         if target_col not in df.columns:
#             raise ValueError(f"Target column '{target_col}' not found in data")

#         X = df.drop(columns=[target_col])
#         y = df[target_col]

#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=0.2, random_state=42
#         )

#         # Candidate models
#         models = {
#             "LogisticRegression": LogisticRegression(max_iter=1000),
#             "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42)
#         }

#         results = []
#         best_model = None
#         best_acc = 0
#         model_dir = "./outputs"
#         os.makedirs(model_dir, exist_ok=True)

#         for name, model in models.items():
#             model.fit(X_train, y_train)
#             y_pred = model.predict(X_test)
#             acc = accuracy_score(y_test, y_pred)
#             results.append({"model": name, "accuracy": acc})

#             if acc > best_acc:
#                 best_acc = acc
#                 best_model = model

#         # Save best model
#         model_path = os.path.join(model_dir, f"{uuid.uuid4()}_best_model.joblib")
#         joblib.dump(best_model, model_path)

#         return {
#             "status": "✅ Model Selection Successful",
#             "best_model": type(best_model).__name__,
#             "best_accuracy": best_acc,
#             "all_results": results,
#             "model_uri": model_path
#         }

#     except Exception as e:
#         return {"status": "❌ Error during model selection", "error": str(e)}

# model_selection_agent.py
import pandas as pd
import joblib
import os
import uuid
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def model_selection(df, target_col):
    """
    Model Selection Agent - Now accepts DataFrame and target column
    ✅ df: preprocessed dataframe
    ✅ target_col: string name of target column
    """

    try:
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in data")

        # Split
        X = df.drop(columns=[target_col])
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Models to try
        models = {
            "LogisticRegression": LogisticRegression(max_iter=1000),
            "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42)
        }

        results = []
        best_model = None
        best_acc = 0
        model_dir = "./outputs"
        os.makedirs(model_dir, exist_ok=True)

        # Train and evaluate models
        for name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)

            results.append({"model": name, "accuracy": acc})

            if acc > best_acc:
                best_acc = acc
                best_model = model

        # Save best model
        model_path = os.path.join(model_dir, f"{uuid.uuid4()}_best_model.joblib")
        joblib.dump(best_model, model_path)

        return {
            "status": "✅ Model Selection Successful",
            "best_model": type(best_model).__name__,
            "best_accuracy": best_acc,
            "all_results": results,
            "model_uri": model_path
        }

    except Exception as e:
        return {
            "status": "❌ Error during model selection",
            "error": str(e)
        }
