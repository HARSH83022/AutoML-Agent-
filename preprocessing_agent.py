import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import joblib
import uuid
import os
from typing import List, Dict, Optional, Union

# =========================
# Preprocessing Function
# =========================
def preprocess(
    data: Union[List[Dict], pd.DataFrame],
    target: Optional[str] = None,
    split: bool = False,
    imbalance: bool = False,
    save_artifacts: bool = True,
    run_id: str = "uuid",
    base_path: str = "./outputs"
) -> Dict:
    """
    Fully automated preprocessing function.
    
    Args:
        data: List of dictionaries (JSON) or a DataFrame.
        target: Name of the target column (optional).
        split: Whether to perform train/test split.
        imbalance: Whether to apply SMOTE on training data.
        save_artifacts: Whether to save train/test/transformer/report.
        run_id: Custom run ID or 'uuid' to auto-generate.
        base_path: Directory to save outputs.

    Returns:
        Dictionary with processed data and optional artifact paths.
    """

    # Convert JSON to DataFrame if needed
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    # Separate features and target
    if target and target in df.columns:
        y = df[target]
        X = df.drop(columns=[target])
    else:
        y = None
        X = df

    # Detect numeric and categorical columns
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

    # Pipelines
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", MinMaxScaler())
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(sparse_output=False, handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipeline, numeric_cols),
        ("cat", categorical_pipeline, categorical_cols)
    ])

    # Apply preprocessing
    X_processed = preprocessor.fit_transform(X)

    # Get feature names
    cat_features = []
    if categorical_cols:
        cat_features = preprocessor.named_transformers_['cat']['onehot'].get_feature_names_out(categorical_cols).tolist()
    feature_names = numeric_cols + cat_features
    X_processed_df = pd.DataFrame(X_processed, columns=feature_names)

    # Train/test split if requested
    if split and y is not None:
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed_df, y, test_size=0.2, stratify=y, random_state=42
        )

        # Handle imbalance with SMOTE
        if imbalance:
            smote = SMOTE(random_state=42)
            X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        else:
            X_train_res, y_train_res = X_train, y_train
    else:
        X_train_res, y_train_res = X_processed_df, y
        X_test, y_test = None, None  # no split

    # Save artifacts
    artifacts = {}
    if save_artifacts:
        os.makedirs(base_path, exist_ok=True)
        run_id_final = str(uuid.uuid4()) if run_id == "uuid" else run_id

        # Save CSV instead of Parquet
        if split and y is not None:
            train_uri = os.path.join(base_path, f"{run_id_final}_train.csv")
            test_uri = os.path.join(base_path, f"{run_id_final}_test.csv")
            pd.DataFrame(X_train_res).assign(target=y_train_res.values).to_csv(train_uri, index=False)
            pd.DataFrame(X_test).assign(target=y_test.values).to_csv(test_uri, index=False)
            artifacts.update({"train_uri": train_uri, "test_uri": test_uri})
        else:
            full_uri = os.path.join(base_path, f"{run_id_final}_full.csv")
            X_processed_df.to_csv(full_uri, index=False)
            artifacts.update({"processed_uri": full_uri})

        # Save the preprocessor
        transformer_uri = os.path.join(base_path, f"{run_id_final}_transformer.joblib")
        joblib.dump(preprocessor, transformer_uri)
        artifacts["transformer_uri"] = transformer_uri

        # Simple HTML report
        report_uri = os.path.join(base_path, f"{run_id_final}_prep_report.html")
        with open(report_uri, "w") as f:
            f.write("<h1>Preprocessing Report</h1>")
            f.write(f"<p>Rows: {X_processed_df.shape[0]}</p>")
            f.write(f"<p>Features: {X_processed_df.shape[1]}</p>")
            if y is not None:
                f.write(f"<p>Target: {target}</p>")
        artifacts["report_uri"] = report_uri

    # Return processed data + artifacts
    result = {
        "processed_data": X_processed_df.to_dict(orient="records"),
        "artifacts": artifacts
    }

    return result
