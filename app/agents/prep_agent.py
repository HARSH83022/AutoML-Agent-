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

# app/agents/prep_agent.py
# import os, json
# from typing import Dict, Any, List
# import numpy as np
# import pandas as pd
# import joblib
# from sklearn.model_selection import train_test_split
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# from imblearn.over_sampling import SMOTE
# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log

# ARTIFACT_DIR = "artifacts"
# os.makedirs(ARTIFACT_DIR, exist_ok=True)

# def _df_preview_stats(df: pd.DataFrame, nrows: int = 50) -> Dict[str, Any]:
#     preview = df.head(nrows).to_dict(orient="list")
#     col_stats = {}
#     for c in df.columns:
#         ser = df[c]
#         dtype = str(ser.dtype)
#         nuniq = int(ser.nunique(dropna=True))
#         nnans = int(ser.isna().sum())
#         pct_null = float(nnans) / max(1, len(ser))
#         sample = ser.dropna().astype(str).unique()[:5].tolist()
#         col_stats[c] = {"dtype": dtype, "nunique": nuniq, "nulls": nnans, "pct_null": round(pct_null,4), "sample_values": sample}
#     return {"preview_rows": min(len(df), nrows), "columns": col_stats, "sample_preview": preview}

# def _build_llm_prompt_for_plan(run_id: str, df: pd.DataFrame, user_ps: Dict) -> str:
#     stats = _df_preview_stats(df, nrows=40)
#     pref = user_ps or {}
#     return f"""
# You are a data preprocessing expert. I will give you a dataset column summary and a problem statement context.
# Return ONLY a JSON object (no explanation), with keys:
# - columns: mapping column_name -> {{ "role":"numeric|categorical|datetime|text|id|ignore", "impute":"median|mean|most_frequent|null", "scale":true|false, "encode":"onehot|ordinal|target|none", "extract":[list datetime parts], "embed":true|false }}
# - global: {{ "target": <column-name or null>, "task_type": "classification|regression", "imbalance_handling":"smote|none" }}

# Dataset summary:
# {json.dumps(stats, indent=2)}

# Problem statement / preferences:
# {json.dumps(pref, indent=2)}
# """

# def _map_plan_to_transformers(plan: Dict[str, Any], df: pd.DataFrame):
#     transformers=[]
#     onehot_cols=[]
#     ord_cols=[]
#     num_cols=[]
#     drop_cols=[]
#     datetime_map={}
#     text_cols=[]
#     for col,spec in plan.get("columns",{}).items():
#         role = spec.get("role")
#         if role=="numeric":
#             num_cols.append(col)
#         elif role=="categorical":
#             enc = spec.get("encode","onehot")
#             if enc=="onehot":
#                 onehot_cols.append(col)
#             else:
#                 ord_cols.append(col)
#         elif role=="datetime":
#             datetime_map[col]=spec.get("extract",["year","month","day"])
#         elif role=="text":
#             text_cols.append(col)
#         elif role in ("id","ignore"):
#             drop_cols.append(col)
#         else:
#             onehot_cols.append(col)
#     if num_cols:
#         num_pipe = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
#         transformers.append(("num", num_pipe, num_cols))
#     if onehot_cols:
#         # sklearn OneHotEncoder in older versions doesn't accept sparse=False in some installations -> be conservative
#         try:
#             ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)
#         except TypeError:
#             ohe = OneHotEncoder(handle_unknown="ignore")
#         cat_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", ohe)])
#         transformers.append(("cat_onehot", cat_pipe, onehot_cols))
#     if ord_cols:
#         ord_pipe = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))])
#         transformers.append(("cat_ord", ord_pipe, ord_cols))
#     preprocessor = ColumnTransformer(transformers=transformers, remainder="drop", sparse_threshold=0.0)
#     return preprocessor, datetime_map, drop_cols, text_cols

# def _apply_datetime_extraction(df: pd.DataFrame, datetime_map: Dict[str, List[str]]):
#     new = df.copy()
#     for col,parts in datetime_map.items():
#         try:
#             ser = pd.to_datetime(new[col], errors="coerce")
#             for p in parts:
#                 if p=="year": new[f"{col}__year"] = ser.dt.year.fillna(0).astype(int)
#                 if p=="month": new[f"{col}__month"] = ser.dt.month.fillna(0).astype(int)
#                 if p=="day": new[f"{col}__day"] = ser.dt.day.fillna(0).astype(int)
#                 if p=="hour": new[f"{col}__hour"] = ser.dt.hour.fillna(0).astype(int)
#                 if p=="weekday": new[f"{col}__weekday"] = ser.dt.weekday.fillna(0).astype(int)
#         except Exception:
#             continue
#         if col in new.columns:
#             new = new.drop(columns=[col], errors="ignore")
#     return new

# def preprocess_dataset(run_id: str, dataset_path: str, ps: Dict) -> Dict:
#     agent_log(run_id, f"[prep_agent] starting on {dataset_path}", agent="prep_agent")
#     df = pd.read_csv(dataset_path)
#     prompt = _build_llm_prompt_for_plan(run_id, df, ps)
#     plan = llm_generate_json(prompt) or {}
#     if not plan or "columns" not in plan:
#         # fallback plan
#         cols={}
#         for c in df.columns:
#             if c.lower().endswith("id") or c.lower().startswith("id_"):
#                 cols[c] = {"role":"id"}
#             elif pd.api.types.is_numeric_dtype(df[c]):
#                 cols[c] = {"role":"numeric","impute":"median","scale":True}
#             elif pd.api.types.is_datetime64_any_dtype(df[c]) or "date" in c.lower():
#                 cols[c] = {"role":"datetime","extract":["year","month","day"]}
#             else:
#                 cols[c] = {"role":"categorical","encode":"onehot"}
#         plan = {"columns": cols, "global":{"target": ps.get("target"), "task_type": ps.get("task_type","classification"), "imbalance_handling":"smote"}}
#         agent_log(run_id, "[prep_agent] using fallback plan", agent="prep_agent")
#     plan_path = os.path.join(ARTIFACT_DIR, f"{run_id}_llm_prep_plan.json")
#     with open(plan_path, "w", encoding="utf-8") as f:
#         json.dump(plan, f, indent=2)
#     datetime_map = {c:spec.get("extract",["year","month","day"]) for c,spec in plan.get("columns",{}).items() if spec.get("role")=="datetime"}
#     if datetime_map:
#         df = _apply_datetime_extraction(df, datetime_map)
#     drop_cols = [c for c,spec in plan.get("columns",{}).items() if spec.get("role") in ("id","ignore")]
#     if drop_cols:
#         df = df.drop(columns=drop_cols, errors="ignore")
#     target = plan.get("global",{}).get("target") or ps.get("target")
#     if not target or target not in df.columns:
#         candidate=None
#         for c in df.columns[::-1]:
#             if c.lower() in ("target","label","y","default","churn","price"):
#                 candidate = c; break
#         target = candidate or df.columns[-1]
#     X = df.drop(columns=[target])
#     y = df[target]
#     reduced_plan = {"columns":{c:plan.get("columns",{}).get(c,{}) for c in df.columns if c in plan.get("columns",{})}, "global": plan.get("global",{})}
#     preprocessor, datetime_map2, drop_after, text_cols = _map_plan_to_transformers(reduced_plan, X)
#     X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.2,
#                                                                 stratify=y if plan.get("global",{}).get("task_type", ps.get("task_type","classification"))=="classification" else None,
#                                                                 random_state=42)
#     preprocessor.fit(X_train_raw, y_train)
#     X_train = preprocessor.transform(X_train_raw)
#     X_test = preprocessor.transform(X_test_raw)
#     if hasattr(X_train, "toarray"): X_train = X_train.toarray()
#     if hasattr(X_test, "toarray"): X_test = X_test.toarray()
#     if plan.get("global",{}).get("imbalance_handling","smote")=="smote" and plan.get("global",{}).get("task_type", ps.get("task_type","classification"))=="classification":
#         try:
#             sm = SMOTE(random_state=42)
#             X_train, y_train = sm.fit_resample(X_train, y_train)
#         except Exception:
#             pass
#     transformer_path = os.path.join(ARTIFACT_DIR, f"{run_id}_transformer.joblib")
#     joblib.dump(preprocessor, transformer_path)
#     train_path = os.path.join(ARTIFACT_DIR, f"{run_id}_train.npz")
#     test_path = os.path.join(ARTIFACT_DIR, f"{run_id}_test.npz")
#     np.savez(train_path, X=X_train, y=y_train)
#     np.savez(test_path, X=X_test, y=y_test)
#     report = {
#         "n_rows": int(len(df)),
#         "n_features_raw": int(X.shape[1]) if hasattr(X, "shape") else None,
#         "target": str(target),
#         "llm_plan_path": plan_path,
#         "llm_plan": plan
#     }
#     report_path = os.path.join(ARTIFACT_DIR, f"{run_id}_prep_report.json")
#     with open(report_path, "w", encoding="utf-8") as f:
#         json.dump(report, f, indent=2)
#     return {"train_path": train_path, "test_path": test_path, "transformer_path": transformer_path, "report": report_path, "summary": report}


# # app/agents/prep_agent.py
# import os
# import json
# import joblib
# import numpy as np
# import pandas as pd
# from typing import Dict, Any, List

# from sklearn.model_selection import train_test_split
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder
# from sklearn.pipeline import Pipeline
# from sklearn.compose import ColumnTransformer
# from imblearn.over_sampling import SMOTE

# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log

# ARTIFACT_DIR = "artifacts"
# os.makedirs(ARTIFACT_DIR, exist_ok=True)


# # ---------------------------------------------------------------------
# # Utility: preview + stats
# # ---------------------------------------------------------------------
# def _df_preview_stats(df: pd.DataFrame, nrows: int = 40):
#     preview = df.head(nrows).to_dict(orient="list")
#     stats = {}
#     for c in df.columns:
#         s = df[c]
#         stats[c] = {
#             "dtype": str(s.dtype),
#             "nunique": int(s.nunique()),
#             "nulls": int(s.isna().sum()),
#             "pct_null": float(s.isna().mean()),
#             "sample_values": s.dropna().astype(str).unique()[:5].tolist()
#         }
#     return {"preview": preview, "columns": stats}


# # ---------------------------------------------------------------------
# # Build LLM Prompt
# # ---------------------------------------------------------------------
# def _build_llm_prompt(run_id: str, df: pd.DataFrame, ps: dict):
#     stats = _df_preview_stats(df)
#     return f"""
# You are an AutoML preprocessing expert.

# Generate a JSON plan with:
# - columns: {{ column_name: {{
#         role: "numeric | categorical | text | datetime | id | ignore",
#         impute: "median | mean | most_frequent",
#         scale: true/false,
#         encode: "onehot | ordinal | none"
# }}}}
# - global: {{
#     target: guessed target,
#     task_type: "classification | regression",
#     imbalance: "smote | none"
# }}

# Dataset preview:
# {json.dumps(stats, indent=2)}

# Problem statement:
# {json.dumps(ps, indent=2)}

# Return ONLY valid JSON.
# """


# # ---------------------------------------------------------------------
# # Map JSON Plan → ColumnTransformer
# # ---------------------------------------------------------------------
# def _build_transformer(plan: dict, df: pd.DataFrame):

#     num_cols = []
#     cat_onehot = []
#     cat_ord = []
#     drop_cols = []

#     for col, conf in plan["columns"].items():
#         role = conf.get("role")

#         if role == "numeric":
#             num_cols.append(col)

#         elif role == "categorical":
#             enc = conf.get("encode", "onehot")
#             if enc == "onehot":
#                 cat_onehot.append(col)
#             else:
#                 cat_ord.append(col)

#         elif role in ("id", "ignore"):
#             drop_cols.append(col)

#         # fallback — treat unknown as categorical one-hot
#         else:
#             cat_onehot.append(col)

#     transformers = []

#     if num_cols:
#         num_pipe = Pipeline([
#             ("imputer", SimpleImputer(strategy="median")),
#             ("scaler", StandardScaler())
#         ])
#         transformers.append(("num", num_pipe, num_cols))

#     if cat_onehot:
#         cat_pipe = Pipeline([
#             ("imputer", SimpleImputer(strategy="most_frequent")),
#             # ⭐ FIXED: new parameter name = sparse_output
#             ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
#         ])
#         transformers.append(("cat_onehot", cat_pipe, cat_onehot))

#     if cat_ord:
#         ord_pipe = Pipeline([
#             ("imputer", SimpleImputer(strategy="most_frequent")),
#             ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))
#         ])
#         transformers.append(("cat_ord", ord_pipe, cat_ord))

#     pre = ColumnTransformer(transformers=transformers, remainder="drop")
#     return pre


# # ---------------------------------------------------------------------
# # MAIN FUNCTION — PREPROCESSING
# # ---------------------------------------------------------------------
# def preprocess_dataset(run_id: str, dataset_path: str, ps: dict):

#     agent_log(run_id, f"[prep_agent] starting on {dataset_path}", agent="prep_agent")

#     df = pd.read_csv(dataset_path)

#     # --- Ask LLM for preprocessing plan ---
#     prompt = _build_llm_prompt(run_id, df, ps)
#     plan = llm_generate_json(prompt)

#     if not plan or "columns" not in plan:
#         # fallback automatic plan
#         agent_log(run_id, "[prep_agent] using fallback plan", agent="prep_agent")
#         plan = {"columns": {}, "global": {}}
#         for c in df.columns:
#             if pd.api.types.is_numeric_dtype(df[c]):
#                 plan["columns"][c] = {"role": "numeric"}
#             else:
#                 plan["columns"][c] = {"role": "categorical"}

#     # -----------------------------------------------------
#     # Determine target column
#     # -----------------------------------------------------
#     target = plan.get("global", {}).get("target")

#     if not target or target not in df.columns:
#         # guess
#         cand = [c for c in df.columns if c.lower() in ["target", "label", "y", "price"]]
#         target = cand[0] if cand else df.columns[-1]

#     plan["global"]["target"] = target

#     X = df.drop(columns=[target])
#     y = df[target]

#     # -----------------------------------------------------
#     # Build transformer
#     # -----------------------------------------------------
#     transformer = _build_transformer(plan, X)

#     X_train_raw, X_test_raw, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42
#     )

#     transformer.fit(X_train_raw)
#     X_train = transformer.transform(X_train_raw)
#     X_test = transformer.transform(X_test_raw)

#     # Drop sparse
#     if hasattr(X_train, "toarray"):
#         X_train = X_train.toarray()
#     if hasattr(X_test, "toarray"):
#         X_test = X_test.toarray()

#     # -----------------------------------------------------
#     # SMOTE (classification)
#     # -----------------------------------------------------
#     task = plan["global"].get("task_type", "classification")
#     imb = plan["global"].get("imbalance", "smote")

#     if task == "classification" and imb == "smote":
#         try:
#             sm = SMOTE()
#             X_train, y_train = sm.fit_resample(X_train, y_train)
#         except Exception as e:
#             agent_log(run_id, f"[prep_agent] SMOTE skipped: {e}", agent="prep_agent")

#     # -----------------------------------------------------
#     # Save artifacts
#     # -----------------------------------------------------
#     transformer_path = os.path.join(ARTIFACT_DIR, f"{run_id}_transformer.joblib")
#     joblib.dump(transformer, transformer_path)

#     train_path = os.path.join(ARTIFACT_DIR, f"{run_id}_train.npz")
#     test_path = os.path.join(ARTIFACT_DIR, f"{run_id}_test.npz")

#     np.savez(train_path, X=X_train, y=y_train)
#     np.savez(test_path, X=X_test, y=y_test)

#     plan_path = os.path.join(ARTIFACT_DIR, f"{run_id}_llm_prep_plan.json")
#     with open(plan_path, "w") as f:
#         json.dump(plan, f, indent=2)

#     return {
#         "train_path": train_path,
#         "test_path": test_path,
#         "transformer_path": transformer_path,
#         "report": plan_path,
#         "summary": {"target": target, "rows": len(df)}
#     }




# # app/agents/prep_agent.py
# import os, json, joblib
# import numpy as np
# import pandas as pd
# from typing import Dict, Any
# from sklearn.model_selection import train_test_split
# from sklearn.impute import SimpleImputer
# from sklearn.preprocessing import OneHotEncoder, StandardScaler
# from sklearn.compose import ColumnTransformer
# from sklearn.pipeline import Pipeline
# from imblearn.over_sampling import SMOTE
# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log

# ARTIFACT_DIR = "artifacts"
# os.makedirs(ARTIFACT_DIR, exist_ok=True)


# def safe_detect_target(df: pd.DataFrame):
#     """Smart target detection."""
#     candidates = ["target", "label", "Outcome", "class", "HeartDisease"]
#     for c in df.columns:
#         if c.lower() in [x.lower() for x in candidates]:
#             return c
#     # fallback → last column
#     return df.columns[-1]


# def safe_build_plan(df: pd.DataFrame):
#     """Build a guaranteed working preprocessing plan."""
#     plan = {"columns": {}, "global": {}}

#     for col in df.columns:
#         if pd.api.types.is_numeric_dtype(df[col]):
#             plan["columns"][col] = {"role": "numeric", "impute": "median"}
#         else:
#             plan["columns"][col] = {"role": "categorical", "impute": "most_frequent"}

#     plan["global"]["imbalance_handling"] = "smote"
#     return plan


# def preprocess_dataset(run_id: str, dataset_path: str, ps: Dict):
#     agent_log(run_id, f"[prep_agent] starting on {dataset_path}", agent="prep_agent")

#     df = pd.read_csv(dataset_path)
#     df = df.dropna(axis=1, how="all")  # drop empty columns

#     # Try LLM plan
#     prompt = f"Create preprocessing plan for columns: {list(df.columns)}"
#     plan = llm_generate_json(prompt)

#     if not plan or "columns" not in plan:
#         agent_log(run_id, "[prep_agent] using fallback plan", agent="prep_agent")
#         plan = safe_build_plan(df)

#     # Detect or override target
#     target = ps.get("target") or safe_detect_target(df)
#     if target not in df.columns:
#         target = safe_detect_target(df)

#     X = df.drop(columns=[target], errors="ignore")
#     y = df[target]

#     # ==== SAFE COLUMN LISTS ====
#     num_cols = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
#     cat_cols = [c for c in X.columns if c not in num_cols]

#     # ==== PIPELINES ====
#     num_pipe = Pipeline([
#         ("imputer", SimpleImputer(strategy="median")),
#         ("scaler", StandardScaler())
#     ])

#     cat_pipe = Pipeline([
#         ("imputer", SimpleImputer(strategy="most_frequent")),
#         ("onehot", OneHotEncoder(handle_unknown="ignore"))
#     ])

#     preprocessor = ColumnTransformer([
#         ("num", num_pipe, num_cols),
#         ("cat", cat_pipe, cat_cols)
#     ])

#     X_train_raw, X_test_raw, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() < 10 else None
#     )

#     preprocessor.fit(X_train_raw)
#     X_train = preprocessor.transform(X_train_raw)
#     X_test = preprocessor.transform(X_test_raw)

#     # SMOTE
#     try:
#         if y_train.nunique() < 10:
#             sm = SMOTE()
#             X_train, y_train = sm.fit_resample(X_train, y_train)
#     except:
#         pass

#     # SAVE
#     transformer_path = f"{ARTIFACT_DIR}/{run_id}_transformer.joblib"
#     train_path = f"{ARTIFACT_DIR}/{run_id}_train.npz"
#     test_path = f"{ARTIFACT_DIR}/{run_id}_test.npz"

#     joblib.dump(preprocessor, transformer_path)
#     np.savez(train_path, X=X_train, y=y_train)
#     np.savez(test_path, X=X_test, y=y_test)

#     return {
#         "train_path": train_path,
#         "test_path": test_path,
#         "transformer_path": transformer_path
#     }




# # app/agents/prep_agent.py
# import os
# import pandas as pd
# import numpy as np
# from sklearn.model_selection import train_test_split
# from sklearn.compose import ColumnTransformer
# from sklearn.preprocessing import OneHotEncoder, StandardScaler
# import joblib
# from app.utils.run_logger import agent_log

# DATA_DIR = "data"

# def safe_load_csv(path):
#     """Load CSV with robust encoding fallbacks."""
#     try:
#         return pd.read_csv(path, encoding="utf-8")
#     except Exception:
#         try:
#             return pd.read_csv(path, encoding="latin1")
#         except Exception:
#             return pd.read_csv(path, encoding_errors="ignore")

# def clean_dataframe(df):
#     """Remove invalid values, inf, weird characters, duplicate cols."""
#     df = df.copy()

#     # Drop duplicate column names
#     df = df.loc[:, ~df.columns.duplicated()]

#     # Remove any rows with infinite values
#     df.replace([np.inf, -np.inf], np.nan, inplace=True)

#     # Drop rows that are entirely NaN
#     df.dropna(how="all", inplace=True)

#     # Fill missing numeric with median
#     for col in df.select_dtypes(include=[np.number]).columns:
#         df[col] = df[col].fillna(df[col].median())

#     # Fill missing categorical with mode
#     for col in df.select_dtypes(include=["object"]).columns:
#         df[col] = df[col].fillna(df[col].mode()[0] if len(df[col].mode()) else "")

#     return df

# def detect_target_column(df):
#     """Try to detect a good target column."""
#     candidates = ["target", "label", "Outcome", "Class", "Price", "y"]
#     for c in candidates:
#         if c in df.columns:
#             return c

#     # If nothing special, last column is assumed target
#     return df.columns[-1]

# def preprocess_dataset(run_id: str, dataset_path: str, ps: dict):
#     agent_log(run_id, f"[prep_agent] starting on {dataset_path}", agent="prep_agent")

#     # ---------------------
#     # LOAD & CLEAN
#     try:
#         df = safe_load_csv(dataset_path)
#     except Exception as e:
#         raise RuntimeError(f"Failed to load CSV: {e}")

#     df = clean_dataframe(df)

#     # ---------------------
#     # TARGET COLUMN DETECTION
#     target = detect_target_column(df)
#     if target not in df.columns:
#         raise RuntimeError(f"Target column '{target}' not found in dataframe.")

#     agent_log(run_id, f"[prep_agent] detected target: {target}", agent="prep_agent")

#     y = df[target]
#     X = df.drop(columns=[target])

#     # ---------------------
#     # HANDLE CATEGORICAL & NUMERIC
#     categorical = X.select_dtypes(include=["object", "category"]).columns.tolist()
#     numeric = X.select_dtypes(include=[np.number]).columns.tolist()

#     agent_log(run_id, f"[prep_agent] numeric={numeric}", agent="prep_agent")
#     agent_log(run_id, f"[prep_agent] categorical={categorical}", agent="prep_agent")

#     # ---------------------
#     # COLUMN TRANSFORMER
#     preprocessor = ColumnTransformer(
#         transformers=[
#             ("num", StandardScaler(), numeric),
#             ("cat", OneHotEncoder(handle_unknown="ignore"), categorical)
#         ]
#     )

#     # try:
#     #     X_processed = preprocessor.fit_transform(X)
#     # except Exception as e:
#     #     raise RuntimeError(f"Preprocessing failed: {e}")
#         # Apply preprocessing
#     try:
#         X_processed = preprocessor.fit_transform(X)
#     except Exception as e:
#         raise RuntimeError(f"Preprocessing failed: {e}")

#     # ---------------------
#     # FINAL SAFETY CLEANING
#     # ---------------------
#     # Convert to dense if sparse
#     if hasattr(X_processed, "toarray"):
#         X_processed = X_processed.toarray()

#     # Convert to float where possible
#     X_processed = np.array(X_processed, dtype="float64", copy=False)

#     # Replace any NaN, inf, weird values with 0
#     X_processed = np.nan_to_num(X_processed, nan=0.0, posinf=1e6, neginf=-1e6)


#     # ---------------------
#     # TRAIN-TEST SPLIT
#     X_train, X_test, y_train, y_test = train_test_split(
#         X_processed, y.to_numpy(), test_size=0.2, random_state=42
#     )

#     # ---------------------
#     # SAVE OUTPUTS
#     os.makedirs("artifacts", exist_ok=True)

#     train_path = f"artifacts/{run_id}_train.npz"
#     test_path = f"artifacts/{run_id}_test.npz"
#     transformer_path = f"artifacts/{run_id}_transformer.joblib"

#     np.savez(train_path, X=X_train, y=y_train)
#     np.savez(test_path, X=X_test, y=y_test)
#     joblib.dump(preprocessor, transformer_path)

#     agent_log(run_id, f"[prep_agent] finished preprocessing", agent="prep_agent")

#     return {
#         "train_path": train_path,
#         "test_path": test_path,
#         "transformer_path": transformer_path
#     }




# # ============================
# #   UNIVERSAL PREP AGENT
# # ============================

# import os
# import json
# import numpy as np
# import pandas as pd
# import joblib
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import OrdinalEncoder
# from sklearn.impute import SimpleImputer
# from app.utils.run_logger import agent_log


# def clean_column(col):
#     """Fix columns containing lists / dicts / objects."""
#     # Convert lists → their lengths
#     if col.apply(lambda x: isinstance(x, list)).any():
#         return col.apply(lambda x: len(x) if isinstance(x, list) else 0)

#     # Convert dicts → their lengths
#     if col.apply(lambda x: isinstance(x, dict)).any():
#         return col.apply(lambda x: len(x) if isinstance(x, dict) else 0)

#     # Convert everything else to string, then numeric where possible
#     return pd.to_numeric(col.astype(str), errors="ignore")


# def preprocess_dataframe(df):
#     """Cleans dataframe, separates X and y, encodes text & categorical."""

#     # Remove unnamed columns (common in CSVs)
#     df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

#     # Clean object columns
#     for c in df.columns:
#         df[c] = clean_column(df[c])

#     # Separate target (LAST column)
#     target_col = df.columns[-1]
#     y = df[target_col]
#     X = df.drop(columns=[target_col])

#     # Identify column types
#     categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
#     numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()

#     # Encode categorical columns
#     if categorical_cols:
#         enc = OrdinalEncoder(handle_unknown="use_encoded_value",
#                              unknown_value=-1)
#         X[categorical_cols] = enc.fit_transform(X[categorical_cols])
#     else:
#         enc = None

#     # Convert text columns to length
#     for c in X.columns:
#         if X[c].dtype == object:
#             X[c] = X[c].astype(str).apply(len)

#     # Ensure numeric only
#     X = X.apply(pd.to_numeric, errors="coerce")

#     # Impute missing values
#     imputer = SimpleImputer(strategy="median")
#     X = imputer.fit_transform(X)

#     # Convert to float32 (safe for FLAML)
#     X = X.astype("float32")

#     # Encode y if categorical
#     if y.dtype == object:
#         y = y.astype(str)
#         y_map = {val: i for i, val in enumerate(sorted(y.unique()))}
#         y = y.map(y_map)
#         y = y.fillna(-1).astype("int32")

#     return X, y, enc, imputer


# def preprocess_dataset(run_id: str, dataset_path: str, ps: dict):
#     """Main entrypoint for orchestrator."""

#     agent_log(run_id, f"[prep_agent] starting: {dataset_path}", agent="prep_agent")

#     try:
#         df = pd.read_csv(dataset_path, encoding="utf-8", engine="python")
#     except:
#         df = pd.read_csv(dataset_path, encoding="ISO-8859-1", engine="python")

#     # Clean & prepare dataset
#     X, y, enc, imputer = preprocess_dataframe(df)

#     # Train/test split
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y, test_size=0.2, random_state=42, shuffle=True
#     )

#     # Save npz files
#     train_path = f"artifacts/{run_id}_train.npz"
#     test_path = f"artifacts/{run_id}_test.npz"
#     transformer_path = f"artifacts/{run_id}_transformer.joblib"

#     np.savez_compressed(train_path, X=X_train, y=y_train)
#     np.savez_compressed(test_path, X=X_test, y=y_test)

#     # Save encoders
#     joblib.dump({"encoder": enc, "imputer": imputer}, transformer_path)

#     agent_log(run_id,
#               f"[prep_agent] COMPLETE — train={train_path}, test={test_path}",
#               agent="prep_agent")

#     return {
#         "train_path": train_path,
#         "test_path": test_path,
#         "transformer_path": transformer_path,
#         "target": df.columns[-1],
#     }



# ============================
#   UNIVERSAL PREP AGENT — FINAL
# ============================

import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder
from sklearn.impute import SimpleImputer
from app.utils.run_logger import agent_log


# ---------------------------------------
#  FIX ALL NON-NUMERIC COLUMN PROBLEMS
# ---------------------------------------
def clean_column(col):
    """Fix columns containing lists, dicts, objects, emojis, mixed types."""

    # Lists → length
    if col.apply(lambda x: isinstance(x, list)).any():
        return col.apply(lambda x: len(x) if isinstance(x, list) else 0)

    # Dicts → length
    if col.apply(lambda x: isinstance(x, dict)).any():
        return col.apply(lambda x: len(x) if isinstance(x, dict) else 0)

    # Convert all to string (safe), then numeric where possible
    col = col.astype(str)

    # Replace emojis / special chars with length
    col = col.apply(lambda x: len(x) if not x.replace('.', '', 1).isdigit() else x)

    # Finally try numeric conversion
    return pd.to_numeric(col, errors="coerce")


def preprocess_dataframe(df):
    """Cleans dataframe, makes ALL columns numeric, and splits X, y."""

    # Drop unnamed cols
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # Clean each column
    for c in df.columns:
        df[c] = clean_column(df[c])

    # Target = last column
    target_col = df.columns[-1]
    y = df[target_col]

    # Drop target from X
    X = df.drop(columns=[target_col])

    # Force numeric only
    X = X.apply(pd.to_numeric, errors="coerce")

    # Impute missing values
    imputer = SimpleImputer(strategy="median")
    X = imputer.fit_transform(X)

    # Convert to float32 (FLAML safe)
    X = X.astype("float32")

    # Encode y
    if y.dtype == object:
        y = y.astype(str)

    # Convert y to numeric safely
    try:
        y = pd.to_numeric(y, errors="coerce")
    except:
        y = y.astype(str).apply(lambda x: len(x))

    # Still NaN? Fill them
    y = y.fillna(-1).astype("float32")

    return X, y, imputer


def preprocess_dataset(run_id: str, dataset_path: str, ps: dict):
    agent_log(run_id, f"[prep_agent] starting: {dataset_path}", agent="prep_agent")

    # Read CSV with fallback encodings
    try:
        df = pd.read_csv(dataset_path, encoding="utf-8", engine="python")
    except:
        df = pd.read_csv(dataset_path, encoding="ISO-8859-1", engine="python")

    # Clean & prepare dataset
    X, y, imputer = preprocess_dataframe(df)

    # FINAL safety cleanup (important!)
    X = np.nan_to_num(X, nan=0, posinf=0, neginf=0)
    y = np.nan_to_num(y, nan=0, posinf=0, neginf=0)

    # Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    # Save artifacts
    train_path = f"artifacts/{run_id}_train.npz"
    test_path = f"artifacts/{run_id}_test.npz"
    transformer_path = f"artifacts/{run_id}_transformer.joblib"

    np.savez_compressed(train_path, X=X_train, y=y_train)
    np.savez_compressed(test_path, X=X_test, y=y_test)

    joblib.dump({"imputer": imputer}, transformer_path)

    agent_log(
        run_id,
        f"[prep_agent] COMPLETE — train={train_path}, test={test_path}",
        agent="prep_agent",
    )

    return {
        "train_path": train_path,
        "test_path": test_path,
        "transformer_path": transformer_path,
        "target": df.columns[-1],
    }
