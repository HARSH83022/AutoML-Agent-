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

def preprocess(
    data: Union[List[Dict], pd.DataFrame],
    target: Optional[str] = None,
    split: bool = False,
    imbalance: bool = False,
    save_artifacts: bool = True,  # Maps to save_csv in API
    run_id: str = "uuid",
    base_path: str = "./outputs"
) -> Dict:
    """
    Universal preprocessing agent.
    Handles CSV, Excel, JSON, Parquet data automatically.
    Returns processed data and optional artifacts (CSV, transformer, report).
    """

    # Convert list of dicts to DataFrame
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data.copy()

    # Drop completely empty columns
    df = df.dropna(axis=1, how='all')

    # Convert datetime columns to numeric features
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]) or "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[f"{col}_year"] = df[col].dt.year.fillna(0).astype(int)
                df[f"{col}_month"] = df[col].dt.month.fillna(0).astype(int)
                df[f"{col}_day"] = df[col].dt.day.fillna(0).astype(int)
                df.drop(columns=[col], inplace=True)
            except Exception:
                continue

    # Separate target
    if target and target in df.columns:
        y = df[target]
        X = df.drop(columns=[target])
    else:
        y = None
        X = df

    # Detect column types
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    # Pipelines
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", MinMaxScaler())
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(sparse_output=False, handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipeline, numeric_cols),
        ("cat", categorical_pipeline, categorical_cols)
    ])

    # Apply preprocessing
    X_processed = preprocessor.fit_transform(X)

    # Feature names
    cat_features = []
    if categorical_cols:
        cat_features = preprocessor.named_transformers_['cat']['encoder'].get_feature_names_out(categorical_cols).tolist()
    feature_names = numeric_cols + cat_features
    X_processed_df = pd.DataFrame(X_processed, columns=feature_names)

    # Replace NaN/Inf for JSON safety
    X_processed_df.replace([np.inf, -np.inf], 0, inplace=True)
    X_processed_df.fillna(0, inplace=True)
    X_processed_df = X_processed_df.round(6)

    # Train/test split
    if split and y is not None:
        from sklearn.model_selection import train_test_split
        stratify_col = y if imbalance else None
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed_df, y, test_size=0.2, stratify=stratify_col, random_state=42
        )
        if imbalance:
            smote = SMOTE(random_state=42)
            X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        else:
            X_train_res, y_train_res = X_train, y_train
        X_processed_df = pd.concat([X_train_res, X_test], axis=0)

    # Save artifacts
    artifacts = {}
    if save_artifacts:
        os.makedirs(base_path, exist_ok=True)
        run_id_final = str(uuid.uuid4()) if run_id == "uuid" else run_id

        # Save processed CSV
        processed_file = os.path.join(base_path, f"{run_id_final}_processed.csv")
        X_processed_df.to_csv(processed_file, index=False)
        artifacts["processed_uri"] = processed_file

        # Save transformer
        transformer_file = os.path.join(base_path, f"{run_id_final}_transformer.joblib")
        joblib.dump(preprocessor, transformer_file)
        artifacts["transformer_uri"] = transformer_file

        # Save simple HTML report
        report_file = os.path.join(base_path, f"{run_id_final}_report.html")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("<h1>🧠 Preprocessing Report</h1>")
            f.write(f"<p>Rows: {X_processed_df.shape[0]}</p>")
            f.write(f"<p>Features after preprocessing: {X_processed_df.shape[1]}</p>")
            f.write(f"<p>Numeric features: {len(numeric_cols)}</p>")
            f.write(f"<p>Categorical features: {len(categorical_cols)}</p>")
        artifacts["report_uri"] = report_file

    return {
        "processed_data": X_processed_df.to_dict(orient="records"),
        "artifacts": artifacts
    }
