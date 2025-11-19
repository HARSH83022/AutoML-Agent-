# # app/agents/prep_agent.py
# import pandas as pd
# import numpy as np
# import joblib
# import os
# import json
# from sklearn.model_selection import train_test_split
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import StandardScaler, OneHotEncoder
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# from imblearn.over_sampling import SMOTE
# from app.utils.llm_clients import llm_generate_json

# def guess_target(df, ps):
#     if ps.get("target") and ps["target"] in df.columns:
#         return ps["target"]
#     for c in df.columns[::-1]:
#         if c.lower() in ("target","label","y","default","churn"):
#             return c
#     return df.columns[-1]

# def _ask_llm_for_plan(run_id, df_preview, ps):
#     prompt = f"""
# You are a data preprocessing assistant. Given the columns: {list(df_preview.columns)}, propose a JSON with:
# strategies: missing (median|mode|mean), categorical_encoding (onehot|target), scaling (standard|none), imbalance (smote|none)
# leakage_checks: list of checks to run.
# Return JSON only.
# """
#     return llm_generate_json(prompt)

# def preprocess_dataset(run_id, dataset_path, ps):
#     df = pd.read_csv(dataset_path)
#     target = guess_target(df, ps)
#     if target not in df.columns:
#         raise ValueError("Target not found: " + str(target))
#     llm_plan = _ask_llm_for_plan(run_id, df.head(10), ps) or {}
#     strategies = llm_plan.get("strategies") or {"missing":"median","categorical_encoding":"onehot","scaling":"standard","imbalance":"smote"}
#     leakage_suggestions = llm_plan.get("leakage_checks", ["check_id_like_columns", "check_time_columns"])

#     # Drop likely ID columns (basic heuristic)
#     for c in list(df.columns):
#         if c.lower().endswith("id") or c.lower().startswith("id_"):
#             try:
#                 df = df.drop(columns=[c])
#             except Exception:
#                 pass

#     X = df.drop(columns=[target])
#     y = df[target]
#     numeric_cols = X.select_dtypes(include=['int64','float64']).columns.tolist()
#     cat_cols = X.select_dtypes(include=['object','category']).columns.tolist()

#     num_transformer = Pipeline([
#         ('imputer', SimpleImputer(strategy='median' if strategies.get("missing","median")=="median" else 'mean')),
#         ('scaler', StandardScaler() if strategies.get("scaling","standard")=="standard" else ('passthrough',))
#     ])
#     if cat_cols:
#         cat_transformer = Pipeline([('imputer', SimpleImputer(strategy='most_frequent')), ('onehot', OneHotEncoder(handle_unknown='ignore', sparse=False))])
#     else:
#         cat_transformer = None

#     transformers = []
#     if numeric_cols:
#         transformers.append(('num', num_transformer, numeric_cols))
#     if cat_cols and cat_transformer:
#         transformers.append(('cat', cat_transformer, cat_cols))

#     preprocessor = ColumnTransformer(transformers=transformers, remainder='drop')

#     X_train_raw, X_test_raw, y_train, y_test = train_test_split(df.drop(columns=[target]), y, test_size=0.2,
#                                                                 stratify=y if ps.get("task_type","classification")=="classification" else None,
#                                                                 random_state=42)
#     preprocessor.fit(X_train_raw, y_train)
#     X_train = preprocessor.transform(X_train_raw)
#     X_test = preprocessor.transform(X_test_raw)

#     if strategies.get("imbalance","smote") == "smote" and ps.get("task_type","classification")=="classification":
#         try:
#             sm = SMOTE(random_state=42)
#             X_train, y_train = sm.fit_resample(X_train, y_train)
#         except Exception:
#             pass

#     os.makedirs("artifacts", exist_ok=True)
#     transformer_path = f"artifacts/{run_id}_transformer.joblib"
#     joblib.dump(preprocessor, transformer_path)

#     np = __import__("numpy")
#     train_path = f"artifacts/{run_id}_train.npz"
#     test_path = f"artifacts/{run_id}_test.npz"
#     np.savez(train_path, X=X_train, y=y_train)
#     np.savez(test_path, X=X_test, y=y_test)

#     report = {"n_rows": len(df), "n_features": int(X.shape[1]) if hasattr(X,'shape') else (len(df.columns)-1), "target": target, "strategies": strategies, "leakage_checks": leakage_suggestions}
#     with open(f"artifacts/{run_id}_prep_report.json","w") as f:
#         json.dump(report, f, indent=2)

#     return {"train_path": train_path, "test_path": test_path, "transformer_path": transformer_path, "report": f"artifacts/{run_id}_prep_report.json", "summary": report}

# # app/agents/prep_agent.py
# import os
# import json
# import joblib
# import numpy as np
# import pandas as pd
# from typing import Dict, List, Tuple
# from sklearn.model_selection import train_test_split
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# from imblearn.over_sampling import SMOTE
# from app.utils.llm_clients import llm_generate_json

# ARTIFACT_DIR = "artifacts"
# os.makedirs(ARTIFACT_DIR, exist_ok=True)

# # ----- Helpers -----
# def guess_target(df: pd.DataFrame, ps: Dict) -> str:
#     if ps.get("target") and ps["target"] in df.columns:
#         return ps["target"]
#     for c in df.columns[::-1]:
#         if c.lower() in ("target", "label", "y", "default", "churn"):
#             return c
#     return df.columns[-1]

# def _ask_llm_for_plan(run_id: str, df_preview: pd.DataFrame, ps: Dict) -> Dict:
#     prompt = f"""
# You are a data preprocessing assistant. Given the columns: {list(df_preview.columns)}, propose a JSON with:
# strategies: missing (median|mode|mean), categorical_encoding (onehot|ordinal|target), scaling (standard|none), imbalance (smote|none)
# leakage_checks: list of checks to run.
# Return JSON only.
# """
#     try:
#         return llm_generate_json(prompt) or {}
#     except Exception:
#         return {}

# def _is_datetime_series(s: pd.Series) -> bool:
#     return pd.api.types.is_datetime64_any_dtype(s) or pd.api.types.is_object_dtype(s) and pd.to_datetime(s, errors='coerce').notna().any()

# def _extract_datetime_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
#     dt_cols = []
#     new_cols = {}
#     for c in df.columns:
#         if _is_datetime_series(df[c]):
#             try:
#                 ser = pd.to_datetime(df[c], errors='coerce')
#                 new_cols[f"{c}__year"] = ser.dt.year.fillna(0).astype(int)
#                 new_cols[f"{c}__month"] = ser.dt.month.fillna(0).astype(int)
#                 new_cols[f"{c}__day"] = ser.dt.day.fillna(0).astype(int)
#                 # optionally: hour, weekday
#                 dt_cols.append(c)
#             except Exception:
#                 continue
#     if new_cols:
#         df = pd.concat([df.drop(columns=dt_cols), pd.DataFrame(new_cols)], axis=1)
#     return df, dt_cols

# def _choose_cat_strategy(col: pd.Series, plan_choice: str, high_cardinality_threshold: int = 30) -> str:
#     """Return 'onehot' or 'ordinal' (or 'target' if implemented)."""
#     if plan_choice:
#         return plan_choice
#     if col.nunique() <= 10:
#         return "onehot"
#     if col.nunique() > high_cardinality_threshold:
#         return "ordinal"
#     return "onehot"

# # ----- Main preprocessing function -----
# def preprocess_dataset(run_id: str, dataset_path: str, ps: Dict) -> Dict:
#     """
#     Read CSV, detect target, preprocess features, save transformer and train/test npz.
#     Returns dict with train_path, test_path, transformer_path, report, summary.
#     """
#     df = pd.read_csv(dataset_path)
#     target = guess_target(df, ps)
#     if target not in df.columns:
#         raise ValueError(f"Target not found: {target}")

#     # Ask LLM for plan (non-blocking if LLM fails)
#     llm_plan = _ask_llm_for_plan(run_id, df.head(10), ps) or {}
#     strategies = llm_plan.get("strategies") or {"missing": "median", "categorical_encoding": "onehot", "scaling": "standard", "imbalance": "smote"}
#     leakage_suggestions = llm_plan.get("leakage_checks", ["check_id_like_columns", "check_time_columns"])

#     # Basic ID drop heuristic
#     drop_cols = []
#     for c in list(df.columns):
#         if c.lower().endswith("id") or c.lower().startswith("id_"):
#             drop_cols.append(c)
#     if drop_cols:
#         df = df.drop(columns=drop_cols, errors="ignore")

#     # Extract datetime features (if any)
#     df, dt_cols = _extract_datetime_columns(df)

#     # Separate X,y
#     X = df.drop(columns=[target])
#     y = df[target]

#     # Detect types
#     numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
#     # treat booleans as numeric if needed
#     cat_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
#     # After datetime extraction, some columns may be numeric now; recompute
#     numeric_cols = [c for c in numeric_cols if c in X.columns]
#     cat_cols = [c for c in cat_cols if c in X.columns and c not in numeric_cols]

#     # Build transformers
#     transformers = []
#     feature_name_lists = []

#     # Numeric transformer
#     if numeric_cols:
#         num_impute_strategy = "median" if strategies.get("missing", "median") == "median" else "mean"
#         num_steps = [("imputer", SimpleImputer(strategy=num_impute_strategy))]
#         if strategies.get("scaling", "standard") == "standard":
#             num_steps.append(("scaler", StandardScaler()))
#         num_transformer = Pipeline(num_steps)
#         transformers.append(("num", num_transformer, numeric_cols))
#         feature_name_lists.append(numeric_cols)

#     # Categorical transformer: handle per-column strategy (onehot vs ordinal) to avoid explosion
#     if cat_cols:
#         # Split categorical columns into low-card and high-card lists
#         low_card_cols = []
#         high_card_cols = []
#         for c in cat_cols:
#             strategy_choice = strategies.get("categorical_encoding") or None
#             chosen = _choose_cat_strategy(X[c], strategy_choice)
#             if chosen == "onehot":
#                 low_card_cols.append(c)
#             else:
#                 high_card_cols.append(c)

#         if low_card_cols:
#             cat_pipeline = Pipeline([
#                 ("imputer", SimpleImputer(strategy="most_frequent")),
#                 ("onehot", OneHotEncoder(handle_unknown="ignore", sparse=False))
#             ])
#             transformers.append(("cat_onehot", cat_pipeline, low_card_cols))
#             # feature names for onehot will be expanded later via get_feature_names_out

#         if high_card_cols:
#             # Use OrdinalEncoder (as a simple fallback for high cardinality)
#             ord_pipeline = Pipeline([
#                 ("imputer", SimpleImputer(strategy="most_frequent")),
#                 ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
#             ])
#             transformers.append(("cat_ord", ord_pipeline, high_card_cols))
#             feature_name_lists.append(high_card_cols)

#     # Create ColumnTransformer
#     preprocessor = ColumnTransformer(transformers=transformers, remainder="drop", sparse_threshold=0.0)

#     # Train/test split (stratify if classification)
#     stratify_arg = y if ps.get("task_type", "classification") == "classification" else None
#     X_train_raw, X_test_raw, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, stratify=stratify_arg, random_state=42
#     )

#     # Fit transformer on train and transform both
#     preprocessor.fit(X_train_raw, y_train)
#     X_train_t = preprocessor.transform(X_train_raw)
#     X_test_t = preprocessor.transform(X_test_raw)

#     # Ensure numpy arrays (dense) for SMOTE and saving
#     if hasattr(X_train_t, "toarray"):
#         X_train_t = X_train_t.toarray()
#     if hasattr(X_test_t, "toarray"):
#         X_test_t = X_test_t.toarray()

#     # Imbalance handling (SMOTE) - only for classification
#     if strategies.get("imbalance", "smote") == "smote" and ps.get("task_type", "classification") == "classification":
#         try:
#             sm = SMOTE(random_state=42)
#             X_train_t, y_train = sm.fit_resample(X_train_t, y_train)
#         except Exception:
#             # If SMOTE fails (e.g., non-numeric target), continue without oversampling
#             pass

#     # Save transformer and train/test arrays
#     transformer_path = os.path.join(ARTIFACT_DIR, f"{run_id}_transformer.joblib")
#     joblib.dump(preprocessor, transformer_path)

#     train_path = os.path.join(ARTIFACT_DIR, f"{run_id}_train.npz")
#     test_path = os.path.join(ARTIFACT_DIR, f"{run_id}_test.npz")
#     np.savez(train_path, X=X_train_t, y=y_train)
#     np.savez(test_path, X=X_test_t, y=y_test)

#     # Build report with derived info
#     try:
#         n_features_after = X_train_t.shape[1]
#     except Exception:
#         n_features_after = None

#     report = {
#         "n_rows": int(len(df)),
#         "n_features_raw": int(X.shape[1]) if hasattr(X, "shape") else None,
#         "n_features_transformed": int(n_features_after) if n_features_after is not None else None,
#         "target": str(target),
#         "dropped_columns": drop_cols,
#         "datetime_extracted": dt_cols,
#         "numeric_columns": numeric_cols,
#         "categorical_low_cardinality": low_card_cols if cat_cols else [],
#         "categorical_high_cardinality": high_card_cols if cat_cols else [],
#         "strategies": strategies,
#         "leakage_checks_suggested": leakage_suggestions,
#     }
#     report_path = os.path.join(ARTIFACT_DIR, f"{run_id}_prep_report.json")
#     with open(report_path, "w", encoding="utf-8") as f:
#         json.dump(report, f, indent=2)

#     return {
#         "train_path": train_path,
#         "test_path": test_path,
#         "transformer_path": transformer_path,
#         "report": report_path,
#         "summary": report,
#     }


import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE

from app.utils.llm_clients import llm_generate_json
from app.utils.run_logger import agent_log

ARTIFACT_DIR = "artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)


# -------------------------
# Compatibility helpers
# -------------------------
def safe_onehot():
    """Return OneHotEncoder compatible with sklearn versions (sparse vs sparse_output)."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


# -------------------------
# Dataset preview utilities
# -------------------------
def _df_preview_stats(df: pd.DataFrame, nrows: int = 40) -> Dict[str, Any]:
    """Return structured summary + small sample to send to LLM."""
    sample_df = df.head(nrows)
    preview = sample_df.to_dict(orient="list")
    col_stats = {}
    for c in df.columns:
        ser = df[c]
        dtype = str(ser.dtype)
        nuniq = int(ser.nunique(dropna=True))
        nnans = int(ser.isna().sum())
        pct_null = round(nnans / max(1, len(ser)), 4)
        sample_vals = ser.dropna().astype(str).unique()[:8].tolist()
        col_stats[c] = {
            "dtype": dtype,
            "nunique": nuniq,
            "nulls": nnans,
            "pct_null": pct_null,
            "sample_values": sample_vals
        }
    return {
        "n_rows": int(len(df)),
        "preview_rows": min(len(df), nrows),
        "columns": col_stats,
        "sample_preview": preview
    }


# -------------------------
# Prompt builder (Option B)
# -------------------------
def _build_llm_prompt_for_plan(run_id: str, df: pd.DataFrame, user_ps: Dict[str, Any]) -> str:
    """
    Build LLM prompt that includes both structured summary and a 40-row sample (Option B).
    The LLM is asked to return ONLY JSON with a strict schema.
    """
    stats = _df_preview_stats(df, nrows=40)
    pref = user_ps or {}
    prompt = f"""
You are an experienced data preprocessing engineer. I will give you a dataset preview and a problem statement/context.
Return ONLY valid JSON (no commentary). The JSON must follow this schema:

{{
  "columns": {{
    "<col_name>": {{
       "role": "numeric|categorical|datetime|text|id|ignore",
       "impute": "median|mean|most_frequent|null",
       "scale": true|false,
       "encode": "onehot|ordinal|none",
       "extract": ["year","month","day","hour","weekday"],    # for datetime
       "embed": true|false                                    # for text, optional
    }}
  }},
  "global": {{
    "target": "<column-name-or-null>",
    "task_type": "classification|regression",
    "imbalance_handling": "smote|none"
  }}
}}

Be conservative and practical. Use onehot for low-cardinality categoricals, ordinal for high-cardinality, median imputation for numerics with skew/outliers, mean for symmetric numerics, most_frequent for categoricals.

Dataset structured summary (JSON):
{json.dumps(stats, indent=2)}

Problem statement / preferences (JSON):
{json.dumps(pref, indent=2)}

Return JSON only. If unsure, set sensible defaults but supply a complete plan covering every column listed above.
"""
    return prompt


# -------------------------
# Map plan -> sklearn transformers
# -------------------------
def _map_plan_to_transformers(plan: Dict[str, Any], df_columns: List[str]) -> Tuple[ColumnTransformer, Dict[str, List[str]], List[str]]:
    """
    Translate LLM plan into a ColumnTransformer and helpers:
      - returns (preprocessor, datetime_map, drop_cols)
    """
    transformers = []
    numeric_cols = []
    onehot_cols = []
    ord_cols = []
    datetime_map = {}
    drop_cols = []

    columns_plan = plan.get("columns", {})

    # Only consider columns actually present in the DataFrame (defensive)
    for col in df_columns:
        spec = columns_plan.get(col, {})
        role = spec.get("role", "categorical")
        if role == "numeric":
            numeric_cols.append(col)
        elif role == "categorical":
            enc = spec.get("encode", "onehot")
            if enc == "onehot":
                onehot_cols.append(col)
            else:
                ord_cols.append(col)
        elif role == "datetime":
            datetime_map[col] = spec.get("extract", ["year", "month", "day"])
        elif role in ("id", "ignore"):
            drop_cols.append(col)
        elif role == "text":
            # for now treat text as categorical (embedding optional)
            # keep as drop or future embed: LLM may set embed true — not implemented here
            ord_cols.append(col)
        else:
            # default fallback
            onehot_cols.append(col)

    # numeric pipeline
    if numeric_cols:
        num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
        transformers.append(("num", num_pipe, numeric_cols))

    # onehot pipeline (safe encoder)
    if onehot_cols:
        cat_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", safe_onehot())])
        transformers.append(("cat_onehot", cat_pipe, onehot_cols))

    # ordinal pipeline
    if ord_cols:
        ord_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))])
        transformers.append(("cat_ord", ord_pipe, ord_cols))

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop", sparse_threshold=0.0)
    return preprocessor, datetime_map, drop_cols


# -------------------------
# Datetime extraction helper
# -------------------------
def _apply_datetime_extraction(df: pd.DataFrame, datetime_map: Dict[str, List[str]]) -> pd.DataFrame:
    new = df.copy()
    for col, parts in datetime_map.items():
        try:
            ser = pd.to_datetime(new[col], errors="coerce")
            for p in parts:
                if p == "year": new[f"{col}__year"] = ser.dt.year.fillna(0).astype(int)
                elif p == "month": new[f"{col}__month"] = ser.dt.month.fillna(0).astype(int)
                elif p == "day": new[f"{col}__day"] = ser.dt.day.fillna(0).astype(int)
                elif p == "hour": new[f"{col}__hour"] = ser.dt.hour.fillna(0).astype(int)
                elif p == "weekday": new[f"{col}__weekday"] = ser.dt.weekday.fillna(0).astype(int)
        except Exception:
            continue
        # drop original datetime column
        new.drop(columns=[col], inplace=True, errors="ignore")
    return new


# -------------------------
# Main preprocess function (LLM-driven)
# -------------------------
def preprocess_dataset(run_id: str, dataset_path: str, ps: Dict[str, Any]) -> Dict[str, Any]:
    """
    LLM-driven preprocessing (Option B: summary + sample).
    Returns dict with train/test paths, transformer path, report path, and summary.
    """
    agent_log(run_id, f"[prep_agent] start preprocessing {dataset_path}", agent="prep_agent")

    # load CSV
    df = pd.read_csv(dataset_path)

    # build prompt with summary + 40-row sample (Option B)
    prompt = _build_llm_prompt_for_plan(run_id, df, ps)

    # call LLM (must return JSON)
    plan = {}
    try:
        plan = llm_generate_json(prompt) or {}
    except Exception as e:
        agent_log(run_id, f"[prep_agent] LLM call failed: {e}", agent="prep_agent")

    # If plan invalid, fallback is still possible but we log it.
    if not plan or "columns" not in plan:
        agent_log(run_id, "[prep_agent] LLM did not return valid plan; using conservative fallback", agent="prep_agent")
        # conservative fallback: infer types from dtypes
        plan = {"columns": {}, "global": {"target": ps.get("target"), "task_type": ps.get("task_type", "classification"), "imbalance_handling": "smote"}}
        for c in df.columns:
            if c.lower().endswith("id") or c.lower().startswith("id_"):
                plan["columns"][c] = {"role": "id"}
            elif pd.api.types.is_numeric_dtype(df[c]):
                plan["columns"][c] = {"role": "numeric", "impute": "median", "scale": True}
            elif pd.api.types.is_datetime64_any_dtype(df[c]) or "date" in c.lower():
                plan["columns"][c] = {"role": "datetime", "extract": ["year","month","day"]}
            else:
                plan["columns"][c] = {"role": "categorical", "encode": "onehot"}

    # persist LLM plan for audit
    plan_path = os.path.join(ARTIFACT_DIR, f"{run_id}_llm_prep_plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)

    # datetime extraction (modify df)
    datetime_map = {c: spec.get("extract", ["year","month","day"]) for c, spec in plan.get("columns", {}).items() if spec.get("role") == "datetime"}
    if datetime_map:
        df = _apply_datetime_extraction(df, datetime_map)

    # drop id/ignore
    drop_cols = [c for c, spec in plan.get("columns", {}).items() if spec.get("role") in ("id", "ignore")]
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True, errors="ignore")

    # determine target (prefer LLM suggestion)
    target = plan.get("global", {}).get("target") or ps.get("target")
    if not target or target not in df.columns:
        # auto-detect common names else last column
        for cand in ["target", "label", "y", "class", "price"]:
            if cand in df.columns:
                target = cand
                break
        else:
            target = df.columns[-1]

    # Split features/target
    X = df.drop(columns=[target])
    y = df[target]

    # Build transformer using the plan (only for columns present in X)
    reduced_plan = {"columns": {c: plan.get("columns", {}).get(c, {}) for c in X.columns}, "global": plan.get("global", {})}
    preprocessor, _, _ = _map_plan_to_transformers(reduced_plan, list(X.columns))

    # train/test split (stratify if classification)
    stratify = y if plan.get("global", {}).get("task_type", ps.get("task_type", "classification")) == "classification" else None
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=stratify, random_state=42)

    # fit + transform
    try:
        preprocessor.fit(X_train_raw)
    except Exception as e:
        agent_log(run_id, f"[prep_agent] preprocessor.fit failed: {e}", agent="prep_agent")
        # Attempt fit with subset (fallback)
        preprocessor.fit(X_train_raw.fillna(""), y_train)

    X_train = preprocessor.transform(X_train_raw)
    X_test = preprocessor.transform(X_test_raw)

    # convert to dense if needed
    if hasattr(X_train, "toarray"):
        X_train = X_train.toarray()
        X_test = X_test.toarray()

    # imbalance handling
    if plan.get("global", {}).get("imbalance_handling", "smote") == "smote" and plan.get("global", {}).get("task_type", ps.get("task_type", "classification")) == "classification":
        try:
            sm = SMOTE(random_state=42)
            X_train, y_train = sm.fit_resample(X_train, y_train)
        except Exception as e:
            agent_log(run_id, f"[prep_agent] SMOTE failed: {e}", agent="prep_agent")

    # save transformer and arrays
    transformer_path = os.path.join(ARTIFACT_DIR, f"{run_id}_transformer.joblib")
    joblib.dump(preprocessor, transformer_path)

    train_path = os.path.join(ARTIFACT_DIR, f"{run_id}_train.npz")
    test_path = os.path.join(ARTIFACT_DIR, f"{run_id}_test.npz")
    np.savez(train_path, X=X_train, y=y_train)
    np.savez(test_path, X=X_test, y=y_test)

    # report for orchestration/dashboard
    report = {
        "n_rows": int(len(df)),
        "n_features_raw": int(X.shape[1]) if hasattr(X, "shape") else None,
        "n_features_transformed": int(X_train.shape[1]) if hasattr(X_train, "shape") else None,
        "target": str(target),
        "llm_plan_path": plan_path,
        "llm_plan": plan
    }
    report_path = os.path.join(ARTIFACT_DIR, f"{run_id}_prep_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    agent_log(run_id, f"[prep_agent] finished. train={train_path} test={test_path} transformer={transformer_path}", agent="prep_agent")

    return {
        "train_path": train_path,
        "test_path": test_path,
        "transformer_path": transformer_path,
        "report": report_path,
        "summary": report
    }
