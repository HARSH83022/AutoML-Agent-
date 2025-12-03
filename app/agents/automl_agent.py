# # # app/agents/automl_agent.py
# # import numpy as np
# # import joblib
# # import json
# # from flaml import AutoML
# # from app.utils.llm_clients import llm_generate_json

# # def _ask_llm_for_model_plan(ps):
# #     prompt = f"""
# # You are an ML system designer. Given: {ps.get('raw_text') or ps}, suggest a JSON:
# # {{ "candidate_models": ["xgboost","lightgbm"], "hpo_suggestion": {{ "time_minutes": 10 }} }}
# # Return JSON only.
# # """
# #     return llm_generate_json(prompt)

# # def run_automl(run_id, train_npz_path, ps, preferences):
# #     data = np.load(train_npz_path)
# #     X_train = data["X"]
# #     y_train = data["y"]
# #     plan = _ask_llm_for_model_plan(ps) or {}
# #     candidate_models = plan.get("candidate_models", ["xgboost","random_forest","logistic_regression"])
# #     time_budget = int(preferences.get("training_budget_minutes", 5)) * 60
# #     metric = preferences.get("primary_metric", "f1")
# #     automl = AutoML()
# #     automl_settings = {
# #         "time_budget": max(30, time_budget),
# #         "metric": metric,
# #         "task": "classification" if ps.get("task_type","classification")=="classification" else "regression",
# #         "log_file_name": f"artifacts/{run_id}_flaml.log"
# #     }
# #     estimator_map = {"xgboost":"xgboost","lightgbm":"lgbm","random_forest":"rf","logistic_regression":"lr","catboost":"catboost"}
# #     est_list = []
# #     for m in candidate_models:
# #         if m in estimator_map:
# #             est_list.append(estimator_map[m])
# #     if est_list:
# #         automl_settings["estimator_list"] = est_list
# #     automl.fit(X_train=X_train, y_train=y_train, **automl_settings)
# #     model_path = f"artifacts/{run_id}_best_model.pkl"
# #     joblib.dump(automl.model, model_path)
# #     try:
# #         lb = automl.leaderboard()
# #         lb_json = lb.to_dict()
# #     except Exception:
# #         lb_json = {}
# #     return {"artifact_uri": model_path, "leaderboard": lb_json, "model_path": model_path, "automl_settings": automl_settings}


# # app/agents/automl_agent.py
# """
# Universal AutoML Agent
# - Supports tabular (FLAML), text (sentence-transformers -> FLAML), images (resnet18 features -> FLAML)
# - Data-aware model selection, safe fallbacks and clear artifacts
# """
# import os
# import json
# import time
# import joblib
# import numpy as np
# from typing import Dict, Any
# from flaml import AutoML

# # reduce FLAML logging noise
# import logging
# logging.getLogger("flaml").setLevel(logging.WARNING)
# logging.getLogger("flaml.automl.logger").setLevel(logging.WARNING)


# ARTIFACT_DIR = "artifacts"
# os.makedirs(ARTIFACT_DIR, exist_ok=True)

# # Optional imports (may not be installed). We import lazily where used.
# try:
#     from sentence_transformers import SentenceTransformer
#     _HAS_SENTENCE = True
# except Exception:
#     _HAS_SENTENCE = False

# try:
#     import torch
#     import torchvision
#     from torchvision import transforms
#     from PIL import Image
#     _HAS_TORCH = True
# except Exception:
#     _HAS_TORCH = False

# from app.utils.llm_clients import llm_generate_json

# # ---------------------------
# # Helpers
# # ---------------------------
# def _ask_llm_for_model_plan(ps: Dict[str, Any]) -> Dict[str, Any]:
#     prompt = f"""
# You are an ML architect. Given problem statement: {ps.get('raw_text') or ps}.
# Return JSON with keys: candidate_models (list), hpo_suggestion (e.g. time_minutes).
# If you cannot, return empty JSON.
# """
#     try:
#         return llm_generate_json(prompt) or {}
#     except Exception:
#         return {}

# def _safe_save_json(path, obj):
#     with open(path, "w", encoding="utf-8") as f:
#         json.dump(obj, f, indent=2)

# def _map_models_to_flaml(candidates):
#     """Map human model names to FLAML estimator_list names (best-effort)."""
#     mapper = {
#         "xgboost": "xgboost",
#         "lightgbm": "lgbm",
#         "lgbm": "lgbm",
#         "random_forest": "rf",
#         "rf": "rf",
#         "catboost": "catboost",
#         "logistic_regression": "lrl2",
#         "logreg": "lrl2",
#         "lrl2": "lrl2",
#         "lrl1": "lrl1",
#         "sgd": "sgd",
#         "svc": "svc",
#         "extra_tree": "extra_tree",
#         "kneighbor": "kneighbor",
#         "histgb": "histgb",
#         "enet": "enet",
#     }
#     out = []
#     for c in (candidates or []):
#         if not isinstance(c, str):
#             continue
#         k = c.strip().lower()
#         if k in mapper:
#             out.append(mapper[k])
#         else:
#             # accept if looks like a flaml name
#             out.append(k)
#     # dedupe and filter
#     seen = set(); res = []
#     for e in out:
#         if e not in seen:
#             res.append(e); seen.add(e)
#     return res

# def _detect_tabular_from_npz(path):
#     try:
#         data = np.load(path)
#         return ("X" in data) and ("y" in data)
#     except Exception:
#         return False

# def _dataset_summary(X: np.ndarray, y: np.ndarray):
#     summary = {
#         "n_rows": int(X.shape[0]) if hasattr(X, "shape") else None,
#         "n_features": int(X.shape[1]) if hasattr(X, "shape") and len(X.shape) > 1 else 1,
#     }
#     try:
#         # imbalance
#         unique, counts = np.unique(y, return_counts=True)
#         if len(counts) > 0:
#             ratios = (counts / counts.sum()).tolist()
#             summary["class_balance"] = dict(zip([str(u) for u in unique.tolist()], ratios))
#     except Exception:
#         pass
#     return summary

# # ---------------------------
# # Modality specific helpers
# # ---------------------------
# def _tabular_automl(X_train, y_train, run_id, ps, preferences, estimator_list=None):
#     """Run FLAML on numeric arrays"""
#     time_budget = int(preferences.get("training_budget_minutes", 5)) * 60
#     time_budget = max(30, time_budget)
#     metric = preferences.get("primary_metric", "f1")
#     task = "classification" if ps.get("task_type", "classification") == "classification" else "regression"

#     automl = AutoML()
#     settings = {
#         "time_budget": time_budget,
#         "metric": metric,
#         "task": task,
#         "log_file_name": f"{ARTIFACT_DIR}/{run_id}_flaml.log",
#     }
#     if estimator_list:
#         settings["estimator_list"] = estimator_list

#     # Try fit with exception handling
#     try:
#         automl.fit(X_train=X_train, y_train=y_train, **settings)
#     except ValueError as e:
#         # save error and retry with conservative default
#         err_path = os.path.join(ARTIFACT_DIR, f"{run_id}_flaml_error.txt")
#         with open(err_path, "a", encoding="utf-8") as f:
#             f.write(str(e) + "\n")
#         settings["estimator_list"] = ["xgboost", "lgbm", "rf"]
#         automl = AutoML()
#         automl.fit(X_train=X_train, y_train=y_train, **settings)
#     # Save model
#     model_path = os.path.join(ARTIFACT_DIR, f"{run_id}_best_model.pkl")
#     try:
#         joblib.dump(automl.model, model_path)
#     except Exception:
#         joblib.dump(automl, model_path)
#     # Leaderboard
#     try:
#         lb = automl.leaderboard()
#         lb_json = lb.to_dict()
#     except Exception:
#         lb_json = {}
#     meta = {
#         "artifact_uri": model_path,
#         "leaderboard": lb_json,
#         "model_path": model_path,
#         "automl_settings": settings,
#     }
#     return meta

# def _text_to_embeddings(csv_path, text_column="text", max_samples=None):
#     if not _HAS_SENTENCE:
#         raise RuntimeError("sentence-transformers not installed. Install 'sentence-transformers' to handle text modality.")
#     df = None
#     try:
#         df = __import__("pandas").read_csv(csv_path)
#     except Exception:
#         raise
#     if text_column not in df.columns:
#         # Try find a probable text column
#         candidates = [c for c in df.columns if "text" in c.lower() or "review" in c.lower() or "comment" in c.lower()]
#         if candidates:
#             text_column = candidates[0]
#         else:
#             # use first object dtype column
#             obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
#             if not obj_cols:
#                 raise RuntimeError("No text column found for text modality.")
#             text_column = obj_cols[0]
#     texts = df[text_column].astype(str).tolist()
#     if max_samples and len(texts) > max_samples:
#         texts = texts[:max_samples]
#     model = SentenceTransformer("all-MiniLM-L6-v2")
#     embeddings = model.encode(texts, show_progress_bar=False)
#     # try to find labels if present
#     label = None
#     for c in ["label", "target", "y"]:
#         if c in df.columns:
#             label = df[c].values
#             break
#     return np.asarray(embeddings), label

# def _image_paths_to_features(paths, max_samples=None):
#     if not _HAS_TORCH:
#         raise RuntimeError("torch/torchvision not installed. Install torch to handle image modality.")
#     if isinstance(paths, str):
#         # assume it's a CSV with image paths
#         try:
#             import pandas as pd
#             df = pd.read_csv(paths)
#             # look for column with path-like values
#             candidates = [c for c in df.columns if any(ext in str(df[c].dropna().astype(str).iloc[0]).lower() for ext in [".jpg", ".png", ".jpeg", ".bmp"])]
#             if candidates:
#                 img_col = candidates[0]
#                 paths_list = df[img_col].tolist()
#             else:
#                 # if the CSV itself is a single column of paths
#                 paths_list = df.iloc[:,0].astype(str).tolist()
#         except Exception as e:
#             raise RuntimeError(f"Unable to read image paths CSV: {e}")
#     elif isinstance(paths, list):
#         paths_list = paths
#     else:
#         raise RuntimeError("Unsupported type for image paths input.")

#     if max_samples:
#         paths_list = paths_list[:max_samples]

#     # feature extractor: resnet18 pretrained, remove last layer
#     device = "cuda" if (torch.cuda.is_available()) else "cpu"
#     resnet = torchvision.models.resnet18(pretrained=True)
#     resnet = torch.nn.Sequential(*list(resnet.children())[:-1]).to(device)
#     resnet.eval()
#     preprocess = transforms.Compose([
#         transforms.Resize(256),
#         transforms.CenterCrop(224),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
#     ])
#     feats = []
#     for p in paths_list:
#         try:
#             img = Image.open(p).convert("RGB")
#             t = preprocess(img).unsqueeze(0).to(device)
#             with torch.no_grad():
#                 out = resnet(t).cpu().numpy().reshape(-1)
#             feats.append(out)
#         except Exception:
#             # skip unreadable images
#             continue
#     if not feats:
#         raise RuntimeError("No image features could be extracted.")
#     return np.vstack(feats), None

# # ---------------------------
# # Main entrypoint
# # ---------------------------
# def run_automl(run_id: str, train_path: str, ps: Dict[str, Any], preferences: Dict[str, Any]):
#     """
#     Universal orchestrator entry.
#     train_path: for tabular, a .npz with X/y; for text: path to CSV; for image: CSV of paths or list
#     ps: problem statement dict (may include required_modalities)
#     preferences: includes training_budget_minutes, primary_metric, etc.
#     """
#     start = time.time()
#     modality = None
#     # 1) Determine modality from PS if present
#     plan = ps.get("plan") or {}
#     required = plan.get("required_modalities") or ps.get("required_modalities")
#     if required:
#         modality = required[0].lower()

#     # 2) Fallback: detect tabular npz
#     if modality is None:
#         if train_path and isinstance(train_path, str) and train_path.endswith(".npz") and _detect_tabular_from_npz(train_path):
#             modality = "tabular"
#         elif train_path and isinstance(train_path, str) and train_path.endswith(".csv"):
#             # could be text or tabular; choose tabular by default but let LLM suggest
#             modality = "tabular"
#         else:
#             modality = "tabular"

#     # Ask LLM for candidate models (text-only suggestion)
#     llm_plan = _ask_llm_for_model_plan(ps)
#     candidate_models = llm_plan.get("candidate_models") or preferences.get("candidate_models") or []
#     est_list = _map_models_to_flaml(candidate_models) if modality == "tabular" else None

#     meta = {"run_id": run_id, "modality": modality, "candidate_models": candidate_models, "est_list": est_list}

#     try:
#         if modality == "tabular":
#             if not train_path or not train_path.endswith(".npz"):
#                 raise RuntimeError("Tabular modality expects a .npz file with X and y created by preprocess agent.")
#             data = np.load(train_path)
#             X = data["X"]
#             y = data["y"]
#             summary = _dataset_summary(X, y)
#             meta["data_summary"] = summary
#             # data-aware model selection: adjust estimator list based on dataset
#             if not est_list:
#                 # pick based on rows/features/imbalance
#                 n = summary.get("n_rows", 0) or 0
#                 f = summary.get("n_features", 0) or 0
#                 cb = summary.get("class_balance", {})
#                 # heuristics
#                 if n > 50000 or f > 1000:
#                     est_list = ["lgbm", "xgboost"]
#                 elif f > 200:
#                     est_list = ["lgbm", "rf"]
#                 elif any(v < 0.05 for v in (cb.values() if cb else [1])):
#                     est_list = ["xgboost", "catboost"]
#                 else:
#                     est_list = ["xgboost", "lgbm", "rf"]
#             res = _tabular_automl(X, y, run_id, ps, preferences, estimator_list=est_list)
#             meta.update(res)
#         elif modality == "text":
#             # train_path expected as CSV with text column and optional label
#             emb, label = _text_to_embeddings(train_path)
#             if label is None:
#                 raise RuntimeError("No label column found in text CSV; supervised training requires labels.")
#             summary = _dataset_summary(emb, label)
#             meta["data_summary"] = summary
#             # map models (we will use simple linear models or xgboost on embeddings)
#             if not est_list:
#                 est_list = ["lrl2", "xgboost"]
#             res = _tabular_automl(emb, label, run_id, ps, preferences, estimator_list=est_list)
#             meta.update(res)
#         elif modality == "image":
#             feats, label = _image_paths_to_features(train_path)
#             if label is not None:
#                 # ensure alignment; else user can pass labels separately
#                 pass
#             summary = _dataset_summary(feats, label if label is not None else np.zeros(feats.shape[0]))
#             meta["data_summary"] = summary
#             if not est_list:
#                 est_list = ["xgboost", "rf"]
#             res = _tabular_automl(feats, label if label is not None else np.zeros(feats.shape[0]), run_id, ps, preferences, estimator_list=est_list)
#             meta.update(res)
#         else:
#             raise RuntimeError(f"Unsupported modality: {modality}")

#         # Save meta and return
#         meta_path = os.path.join(ARTIFACT_DIR, f"{run_id}_train_meta.json")
#         _safe_save_json(meta_path, meta)
#         meta["meta_path"] = meta_path
#         return meta

#     except Exception as e:
#         # Write error artifact
#         err_path = os.path.join(ARTIFACT_DIR, f"{run_id}_automl_error.txt")
#         with open(err_path, "w", encoding="utf-8") as f:
#             f.write(str(e) + "\n")
#         raise





# # app/agents/automl_agent.py

# import numpy as np
# import joblib
# import json
# import logging
# import traceback
# from flaml import AutoML
# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log

# # reduce FLAML logging noise
# logging.getLogger("flaml").setLevel(logging.WARNING)
# logging.getLogger("flaml.automl.logger").setLevel(logging.WARNING)


# # ---------------------------------------------------------------------
# # FLAML Supported Estimators (clean, task-separated)
# # ---------------------------------------------------------------------
# FLAML_SUPPORTED = {
#     "classification": {
#         "xgboost", "xgb_limitdepth", "rf", "lgbm", "catboost",
#         "extra_tree", "kneighbor", "svc", "sgd", "histgb"
#     },
#     "regression": {
#         "xgboost", "rf", "lgbm", "extra_tree", "histgb", "sgd"
#     }
# }

# # Friendly → FLAML name mapping
# ESTIMATOR_MAP = {
#     "xgboost": "xgboost",
#     "lightgbm": "lgbm",
#     "lgbm": "lgbm",
#     "random_forest": "rf",
#     "rf": "rf",
#     "catboost": "catboost",
#     "logistic_regression": "lrl1",
#     "logreg": "lrl1",
#     "lr": "lrl1",
#     "sgd": "sgd",
#     "svc": "svc",
#     "kneighbor": "kneighbor",
#     "extra_tree": "extra_tree"
# }


# # ---------------------------------------------------------------------
# # LLM decides model list & task type
# # ---------------------------------------------------------------------
# def _ask_llm_plan(ps, X_train, y_train):
#     """
#     LLM decides:
#       - task_type: classification or regression
#       - candidate_models: ["xgboost", "lgbm"]
#       - time budget hint (optional)
#     """
#     prompt = f"""
# You are an expert ML system designer.

# Given this problem statement and dataset:
# Problem Statement: {ps}
# y (target) preview (dtype={str(y_train.dtype)}): {y_train[:10]}

# Decide the correct ML task type based on the nature of y:
# - "classification" → discrete labels, categories, small number of unique values.
# - "regression" → continuous numeric values.

# Return STRICT JSON:
# {{
#   "task_type": "classification" or "regression",
#   "candidate_models": ["xgboost","lightgbm","random_forest"],
#   "hpo_suggestion": {{"time_minutes": 10}}
# }}
# Only return JSON.
# """

#     try:
#         return llm_generate_json(prompt) or {}
#     except Exception:
#         return {}


# # ---------------------------------------------------------------------
# # Clean estimator sanitation (no if/else on task)
# # ---------------------------------------------------------------------
# def _sanitize_candidate_models(candidate_models, task):
#     task = task if task in ("classification", "regression") else "classification"

#     out = []
#     for m in candidate_models:
#         m_low = (m or "").lower()

#         mapped = ESTIMATOR_MAP.get(m_low, None)

#         # if not mapped but already valid FLAML name
#         if not mapped and m_low in FLAML_SUPPORTED[task]:
#             mapped = m_low

#         # keep only valid models for the task
#         if mapped and mapped in FLAML_SUPPORTED[task]:
#             out.append(mapped)

#     # fallback
#     if not out:
#         out = ["xgboost", "lgbm", "rf"]

#     # dedupe
#     seen = set()
#     res = []
#     for e in out:
#         if e not in seen:
#             seen.add(e)
#             res.append(e)
#     return res


# # ---------------------------------------------------------------------
# # Main AutoML Runner
# # ---------------------------------------------------------------------
# def run_automl(run_id, train_npz_path, ps, preferences):

#     # Load data
#     try:
#         data = np.load(train_npz_path)
#         X_train = data["X"]
#         y_train = data["y"]
#     except Exception as e:
#         agent_log(run_id, f"[automl_agent] failed loading {train_npz_path}: {e}")
#         raise

#     y_train = np.asarray(y_train).ravel()
#     if y_train is None:
#         raise ValueError("y_train is None")

#     # LLM decides everything
#     llm_plan = _ask_llm_plan(ps, X_train, y_train)

#     task_type = llm_plan.get("task_type", "classification")
#     candidate_models = llm_plan.get(
#         "candidate_models",
#         ["xgboost", "lightgbm", "random_forest"]
#     )

#     est_list = _sanitize_candidate_models(candidate_models, task_type)

#     # Time & metric
#     time_budget = int(preferences.get("training_budget_minutes", 5)) * 60
#     metric = preferences.get("primary_metric", "f1")

#     # AutoML setup
#     automl = AutoML()
#     settings = {
#         "time_budget": max(30, time_budget),
#         "metric": metric,
#         "task": task_type,
#         "estimator_list": est_list,
#         "log_file_name": f"artifacts/{run_id}_flaml.log"
#     }

#     agent_log(run_id,
#               f"[automl_agent] AutoML Starting | task={task_type} | "
#               f"metric={metric} | time={settings['time_budget']}s | "
#               f"models={est_list}")

#     # Run AutoML
#     try:
#         automl.fit(X_train=X_train, y_train=y_train, **settings)
#     except Exception as e:
#         tb = traceback.format_exc()
#         agent_log(run_id, f"[automl_agent] AutoML fit failed: {e}\n{tb}")
#         raise

#     # Save best model
#     model_path = f"artifacts/{run_id}_best_model.pkl"
#     try:
#         joblib.dump(automl.model, model_path)
#     except Exception:
#         try:
#             joblib.dump(automl, model_path)
#             agent_log(run_id,
#                       "[automl_agent] Pickled entire AutoML object as fallback")
#         except Exception as e:
#             agent_log(run_id, f"[automl_agent] model save failed: {e}")

#     # Leaderboard extraction
#     try:
#         lb = automl.leaderboard()
#         lb_json = lb.to_dict()
#     except Exception:
#         lb_json = {}

#     res = {
#         "artifact_uri": model_path,
#         "leaderboard": lb_json,
#         "model_path": model_path,
#         "automl_settings": settings
#     }
#     agent_log(run_id, "[automl_agent] Finished AutoML run successfully.")

#     return res




# # app/agents/automl_agent.py
# import os, json, traceback
# import numpy as np
# import joblib
# from flaml import AutoML
# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log

# FLAML_SUPPORTED = {
#     "classification": {"xgboost","xgb_limitdepth","rf","lgbm","catboost","extra_tree","kneighbor","svc","sgd","histgb"},
#     "regression": {"xgboost","rf","lgbm","extra_tree","histgb","sgd"}
# }
# ESTIMATOR_MAP = {"xgboost":"xgboost","lightgbm":"lgbm","lgbm":"lgbm","random_forest":"rf","rf":"rf","catboost":"catboost","logistic_regression":"lrl1","logreg":"lrl1","lr":"lrl1","sgd":"sgd","svc":"svc","kneighbor":"kneighbor","extra_tree":"extra_tree"}

# def _ask_llm_plan(ps, X_train, y_train):
#     prompt = f"""
# You are an ML system designer.
# Problem Statement: {ps.get('raw_text') or ps}
# y (preview): {list(y_train[:10])}
# Decide task_type and candidate_models. Return JSON:
# {{ "task_type": "classification" or "regression", "candidate_models":["xgboost","lgbm"], "hpo_suggestion":{{"time_minutes": 10}} }}
# Only return JSON.
# """
#     try:
#         return llm_generate_json(prompt) or {}
#     except Exception:
#         return {}

# def _sanitize_candidate_models(candidate_models, task):
#     task = task if task in ("classification","regression") else "classification"
#     out=[]
#     for m in candidate_models:
#         m_low = (m or "").lower()
#         mapped = ESTIMATOR_MAP.get(m_low, None)
#         if not mapped and m_low in FLAML_SUPPORTED[task]:
#             mapped = m_low
#         if mapped and mapped in FLAML_SUPPORTED[task]:
#             out.append(mapped)
#     if not out:
#         out = ["xgboost","lgbm","rf"]
#     # dedupe
#     seen=set(); res=[]
#     for e in out:
#         if e not in seen:
#             seen.add(e); res.append(e)
#     return res

# def run_automl(run_id: str, train_npz_path: str, ps: dict, preferences: dict):
#     agent_log(run_id, f"[automl_agent] starting with train {train_npz_path}", agent="automl_agent")
#     try:
#         data = np.load(train_npz_path, allow_pickle=True)
#         X_train = data["X"]
#         y_train = data["y"]
#     except Exception as e:
#         raise RuntimeError(f"Failed to load train npz: {e}")
#     y_train = np.asarray(y_train).ravel()
#     llm_plan = _ask_llm_plan(ps, X_train, y_train)
#     task_type = llm_plan.get("task_type", ps.get("task_type", "classification"))
#     candidate_models = llm_plan.get("candidate_models", ["xgboost","lgbm","rf"])
#     est_list = _sanitize_candidate_models(candidate_models, task_type)
#     time_budget = int(preferences.get("training_budget_minutes", 5)) * 60
#     metric = preferences.get("primary_metric", "f1")
#     automl = AutoML()
#     settings = {
#         "time_budget": max(30, time_budget),
#         "metric": metric,
#         "task": task_type,
#         "estimator_list": est_list,
#         "log_file_name": f"artifacts/{run_id}_flaml.log"
#     }
#     agent_log(run_id, f"[automl_agent] settings: {settings}", agent="automl_agent")
#     try:
#         automl.fit(X_train=X_train, y_train=y_train, **settings)
#     except Exception as e:
#         tb = traceback.format_exc()
#         agent_log(run_id, f"[automl_agent] AutoML fit failed: {e}\n{tb}", agent="automl_agent")
#         raise
#     model_path = f"artifacts/{run_id}_best_model.pkl"
#     try:
#         joblib.dump(automl.model, model_path)
#     except Exception:
#         try:
#             joblib.dump(automl, model_path)
#         except Exception as e:
#             agent_log(run_id, f"[automl_agent] model save failed: {e}", agent="automl_agent")
#     try:
#         lb = automl.leaderboard()
#         lb_json = lb.to_dict()
#     except Exception:
#         lb_json = {}
#     res = {"artifact_uri": model_path, "leaderboard": lb_json, "model_path": model_path, "automl_settings": settings, "task_type": task_type}
#     agent_log(run_id, "[automl_agent] finished", agent="automl_agent")
#     return res



# # app/agents/automl_agent.py
# import os, json, traceback
# import numpy as np
# import joblib
# from flaml import AutoML

# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log

# # FLAML-supported estimators
# FLAML_SUPPORTED = {
#     "classification": {
#         "xgboost", "xgb_limitdepth", "rf", "lgbm", "catboost",
#         "extra_tree", "kneighbor", "svc", "sgd", "histgb"
#     },
#     "regression": {
#         "xgboost", "rf", "lgbm", "extra_tree", "histgb", "sgd"
#     }
# }

# # Allow flexible user inputs → mapped to FLAML names
# ESTIMATOR_MAP = {
#     "xgboost": "xgboost",
#     "xgb": "xgboost",
#     "lightgbm": "lgbm",
#     "lgbm": "lgbm",
#     "rf": "rf",
#     "random_forest": "rf",
#     "catboost": "catboost",
#     "extra_tree": "extra_tree",
#     "kneighbor": "kneighbor",
#     "knn": "kneighbor",
#     "svc": "svc",
#     "svm": "svc",
#     "sgd": "sgd",
#     "logistic_regression": "lrl1",
#     "logreg": "lrl1",
#     "lr": "lrl1"
# }

# def _ask_llm_plan(ps: dict, X_train, y_train):
#     """
#     Ask LLM to determine task type + model shortlist.
#     """
#     prompt = f"""
# You are an AutoML planning expert.
# Given this problem statement:

# {ps.get("raw_text")}

# Preview of y values: {list(np.unique(y_train)[:10])}

# Return ONLY JSON:
# {{
#   "task_type": "classification" or "regression",
#   "candidate_models": ["xgboost","lgbm","rf"],
#   "hpo_suggestion": {{ "time_minutes": 5 }}
# }}
# """

#     try:
#         j = llm_generate_json(prompt)
#         return j or {}
#     except:
#         return {}

# # def _sanitize_candidate_models(models, task):
# #     """
# #     Ensures only valid FLAML models remain.
# #     """
# #     clean = []
# #     for m in models:
# #         m = m.lower()
# #         mapped = ESTIMATOR_MAP.get(m, m)
# #         if mapped in FLAML_SUPPORTED[task]:
# #             clean.append(mapped)

# #     if not clean:
# #         clean = ["xgboost", "lgbm", "rf"]

# #     # Deduplicate
# #     final = []
# #     for m in clean:
# #         if m not in final:
# #             final.append(m)

# #     return final
# from app.utils.json_cleaner import flatten_list

# def _sanitize_candidate_models(models, task):
#     """
#     Ensures only valid FLAML-supported models are used.
#     """
#     if not isinstance(models, list):
#         return ["xgboost", "lgbm", "rf"]

#     task = task if task in ("classification", "regression") else "classification"
#     clean = []

#     for m in models:
#         if not isinstance(m, str):
#             continue
#         m = m.lower().strip()

#         mapped = ESTIMATOR_MAP.get(m, m)
#         if mapped in FLAML_SUPPORTED[task]:
#             clean.append(mapped)

#     if not clean:
#         clean = ["xgboost", "lgbm", "rf"]

#     return list(dict.fromkeys(clean))  # dedupe while preserving order



# def run_automl(run_id: str, train_npz_path: str, ps: dict, preferences: dict):
#     agent_log(run_id, f"[automl_agent] starting with train file {train_npz_path}", agent="automl_agent")

#     # ----------------------
#     # LOAD TRAINING DATA
#     try:
#         data = np.load(train_npz_path, allow_pickle=True)
#         X_train, y_train = data["X"], data["y"]
#         y_train = np.asarray(y_train).ravel()
#     except Exception as e:
#         raise RuntimeError(f"Training data load failed: {e}")

#     # ----------------------
#     # LLM MODEL SELECTION
#     llm_plan = _ask_llm_plan(ps, X_train, y_train)
#     task_type = llm_plan.get("task_type", ps.get("task_type", "classification"))

#     # ----------------------
#     # MODEL CANDIDATE SELECTION
#     raw_candidates = llm_plan.get("candidate_models", ["xgboost", "lgbm", "rf"])
#     est_list = _sanitize_candidate_models(raw_candidates, task_type)

#     # ----------------------
#     # TIME BUDGET
#     time_budget = int(preferences.get("training_budget_minutes", 3)) * 60
#     metric = preferences.get("primary_metric", "f1" if task_type == "classification" else "r2")

#     settings = {
#         "time_budget": max(30, time_budget),
#         "metric": metric,
#         "task": task_type,
#         "estimator_list": est_list,
#         "log_file_name": f"artifacts/{run_id}_flaml.log"
#     }

#     agent_log(run_id, f"[automl_agent] settings: {settings}", agent="automl_agent")

#     # ----------------------
#     # TRAIN THE MODEL
#     automl = AutoML()
#     try:
#         automl.fit(X_train=X_train, y_train=y_train, **settings)
#     except Exception as e:
#         tb = traceback.format_exc()
#         agent_log(run_id, f"[automl_agent] AutoML FAILED:\n{e}\n{tb}", agent="automl_agent")
#         raise

#     # ----------------------
#     # SAVE MODEL
#     model_path = f"artifacts/{run_id}_best_model.pkl"
#     try:
#         joblib.dump(automl.model, model_path)
#     except:
#         joblib.dump(automl, model_path)

#     # ----------------------
#     # LEADERBOARD
#     try:
#         leaderboard = automl.leaderboard().to_dict()
#     except:
#         leaderboard = {}

#     agent_log(run_id, "[automl_agent] FINISHED", agent="automl_agent")

#     return {
#         "model_path": model_path,
#         "artifact_uri": model_path,
#         "leaderboard": leaderboard,
#         "automl_settings": settings,
#         "task_type": task_type
#     }






# app/agents/automl_agent.py

# import os
# import json
# import traceback
# import numpy as np
# import joblib
# from flaml import AutoML

# # from app.utils.llm_clients import llm_generate_json
# # from app.utils.run_logger import agent_log
# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log


# # -------------------------
# # SUPPORTED MODELS LIST
# # -------------------------
# FLAML_SUPPORTED = {
#     "classification": {
#         "xgboost", "xgb_limitdepth", "rf", "lgbm", "catboost",
#         "extra_tree", "kneighbor", "svc", "sgd", "histgb"
#     },
#     "regression": {
#         "xgboost", "rf", "lgbm",
#         "extra_tree", "histgb", "sgd"
#     }}

# # Normalization mapping
# ESTIMATOR_MAP = {
#     "xgboost": "xgboost",
#     "lightgbm": "lgbm",
#     "lgbm": "lgbm",
#     "random_forest": "rf",
#     "rf": "rf",
#     "catboost": "catboost",
#     "logistic_regression": "lrl1",
#     "logreg": "lrl1",
#     "lr": "lrl1",
#     "sgd": "sgd",
#     "svc": "svc",
#     "kneighbor": "kneighbor",
#     "extra_tree": "extra_tree",
# }


# # -------------------------
# # LLM PLANNING
# # -------------------------
# def _ask_llm_plan(ps, X_train, y_train):
#     """
#     Ask the LLM to propose task type + model list.
#     Works safely with fallback.
#     """
#     prompt = f"""
# You are an ML system designer.

# Problem: {ps.get('raw_text') or ps}
# First 10 labels: {list(y_train[:10])}

# Return ONLY valid JSON with:
# {{
#   "task_type": "classification" or "regression",
#   "candidate_models": ["xgboost", "lgbm", "rf"],
#   "hpo_suggestion": {{"time_minutes": 5}}
# }}
# """

#     try:
#         out = llm_generate_json(prompt)
#         if out is None:
#             return {}
#         return out
#     except Exception:
#         return {}


# # -------------------------
# # MODEL SANITIZER
# # -------------------------
# def _sanitize_candidate_models(models, task):
#     """Ensures only valid models for FLAML remain."""
#     if not isinstance(models, list):
#         return ["xgboost", "lgbm", "rf"]

#     task = task if task in ("classification", "regression") else "classification"

#     clean = []
#     for m in models:
#         if not isinstance(m, str):
#             continue
#         m = m.lower().strip()
#         mapped = ESTIMATOR_MAP.get(m, m)
#         if mapped in FLAML_SUPPORTED[task]:
#             clean.append(mapped)

#     if not clean:
#         clean = ["xgboost", "lgbm", "rf"]

#     # dedupe preserving order
#     final = []
#     for c in clean:
#         if c not in final:
#             final.append(c)

#     return final


# # -------------------------
# # MAIN AUTOML FUNCTION
# # -------------------------
# def run_automl(run_id: str, train_npz_path: str, ps: dict, preferences: dict):
#     agent_log(run_id, f"[automl_agent] Starting AutoML with train file: {train_npz_path}", agent="automl_agent")

#     # LOAD TRAIN DATA
#     try:
#         data = np.load(train_npz_path, allow_pickle=True)
#         X_train = np.asarray(data["X"])
#         y_train = np.asarray(data["y"]).ravel()
#     except Exception as e:
#         raise RuntimeError(f"Training data load failed: {e}")

#     # SANITIZE LABELS (fix NaN, Inf)
#     if np.any(np.isnan(y_train)) or np.any(np.isinf(y_train)):
#         agent_log(run_id, "[automl_agent] WARNING: NaN/Inf labels detected — cleaning...", agent="automl_agent")

#         valid_mask = ~(np.isnan(y_train) | np.isinf(y_train))
#         X_train = X_train[valid_mask]
#         y_train = y_train[valid_mask]

#         if len(y_train) == 0:
#             raise RuntimeError("All labels were invalid (NaN/inf).")

#     # ASK LLM FOR A PLAN
#     llm_plan = {}
#     try:
#         llm_plan = _ask_llm_plan(ps, X_train, y_train) or {}
#     except Exception:
#         llm_plan = {}

#     task_type = llm_plan.get("task_type") or ps.get("task_type") or "classification"

#     # SELECT MODELS SAFELY
#     raw_candidates = llm_plan.get("candidate_models", ["xgboost", "lgbm", "rf"])
#     est_list = _sanitize_candidate_models(raw_candidates, task_type)

#     # TIME BUDGET
#     time_budget = int(preferences.get("training_budget_minutes", 3)) * 60
#     metric = preferences.get(
#         "primary_metric",
#         "f1" if task_type == "classification" else "r2"
#     )

#     # AUTOML SETTINGS
#     settings = {
#         "time_budget": max(30, time_budget),
#         "metric": metric,
#         "task": task_type,
#         "estimator_list": est_list,
#         "log_file_name": f"artifacts/{run_id}_flaml.log",
#     }

#     agent_log(run_id, f"[automl_agent] Settings: {settings}", agent="automl_agent")

#     # TRAIN MODEL
#     automl = AutoML()
#     try:
#         automl.fit(X_train=X_train, y_train=y_train, **settings)
#     except Exception as e:
#         agent_log(
#             run_id,
#             f"[automl_agent] AutoML.fit failed: {e}\n{traceback.format_exc()}",
#             agent="automl_agent",
#         )
#         raise

#     # SAVE BEST MODEL
#     model_path = f"artifacts/{run_id}_best_model.pkl"
#     try:
#         to_save = getattr(automl, "model", None) or automl
#         joblib.dump(to_save, model_path)
#     except Exception as e:
#         agent_log(run_id, f"[automl_agent] Model save failed: {e}", agent="automl_agent")
#         model_path = None

#     # LEADERBOARD SAFE FETCH
#     try:
#         lb = automl.leaderboard()
#         try:
#             lb_json = lb.to_dict()
#         except:
#             lb_json = str(lb)
#     except:
#         lb_json = {}

#     res = {
#         "artifact_uri": model_path,
#         "leaderboard": lb_json,
#         "model_path": model_path,
#         "automl_settings": settings,
#         "task_type": task_type,
#     }

#     agent_log(run_id, "[automl_agent] Finished successfully", agent="automl_agent")
#     return res


# # app/agents/automl_agent.py

# import os
# import json
# import traceback
# import numpy as np
# import joblib
# from flaml import AutoML

# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log


# # ============================================================
# # Supported FLAML Models
# # ============================================================
# FLAML_SUPPORTED = {
#     "classification": {
#         "xgboost", "xgb_limitdepth", "rf", "lgbm",
#         "catboost", "extra_tree", "kneighbor", "svc",
#         "sgd", "histgb"
#     },
#     "regression": {
#         "xgboost", "rf", "lgbm",
#         "extra_tree", "histgb", "sgd"
#     },
# }

# # Map alias → FLAML estimator
# ESTIMATOR_MAP = {
#     "xgboost": "xgboost",
#     "lightgbm": "lgbm",
#     "lgbm": "lgbm",
#     "rf": "rf",
#     "random_forest": "rf",
#     "catboost": "catboost",
#     "sgd": "sgd",
#     "svc": "svc",
#     "kneighbor": "kneighbor",
#     "extra_tree": "extra_tree",
#     "logistic_regression": "lrl1",
#     "logreg": "lrl1",
#     "lr": "lrl1",
# }


# # ============================================================
# # ---- LLM-BASED MODEL PLANNING ----
# # ============================================================
# def _ask_llm_plan(ps: dict, X_train, y_train):
#     """
#     Ask LLM to propose an AutoML plan.
#     Always returns a dict.
#     """
#     prompt = f"""
# You are an ML system designer.

# Problem:
# {ps.get('raw_text')}

# First few labels: {list(y_train[:8])}

# Return ONLY JSON with:
# {{
#   "task_type": "classification" or "regression",
#   "candidate_models": ["xgboost", "lgbm", "rf"]
# }}
# """

#     try:
#         out = llm_generate_json(prompt)
#         if isinstance(out, dict):
#             return out
#         return {}
#     except:
#         return {}


# # ============================================================
# # ---- SANITIZE MODEL LIST ----
# # ============================================================
# # def _sanitize_candidate_models(models, task):
# #     """
# #     Fix nonsense model names from LLM,
# #     keep only valid FLAML-supported estimators.
# #     """
# #     if not isinstance(models, list):
# #         return ["xgboost", "lgbm", "rf"]

# #     task = task if task in FLAML_SUPPORTED else "classification"

# #     clean = []
# #     for m in models:
# #         if not isinstance(m, str):
# #             continue
# #         m = m.lower().strip()

# #         # map alias → flaml name
# #         mapped = ESTIMATOR_MAP.get(m, m)

# #         if mapped in FLAML_SUPPORTED[task]:
# #             clean.append(mapped)

# #     # fallback
# #     if not clean:
# #         clean = ["xgboost", "lgbm", "rf"]

# #     # remove duplicates
# #     final = []
# #     for x in clean:
# #         if x not in final:
# #             final.append(x)

# #     return final
# def _sanitize_candidate_models(models, task):
#     """Guarantee safe estimator list for FLAML. No unsupported model will ever pass."""
#     task = task if task in ("classification", "regression") else "classification"

#     # Only models FLAML ACTUALLY supports
#     allowed = FLAML_SUPPORTED[task]

#     safe_list = []

#     if isinstance(models, list):
#         for m in models:
#             if not isinstance(m, str):
#                 continue

#             m = m.lower().strip()
#             mapped = ESTIMATOR_MAP.get(m, m)

#             # Keep only FLAML-supported models
#             if mapped in allowed:
#                 safe_list.append(mapped)

#     # If LLM gave garbage → force fallback
#     if not safe_list:
#         safe_list = ["xgboost", "lgbm", "rf"]

#     # Deduplicate
#     final_list = []
#     for model in safe_list:
#         if model not in final_list:
#             final_list.append(model)

#     return final_list



# # ============================================================
# # ---- MAIN AUTOML FUNCTION ----
# # ============================================================
# def run_automl(run_id: str, train_npz_path: str, ps: dict, preferences: dict):
#     agent_log(run_id, f"[automl_agent] Loading training data from {train_npz_path}", agent="automl_agent")

#     # ---------------------------------------------------------
#     # LOAD TRAINING DATA SAFELY
#     # ---------------------------------------------------------
#     try:
#         data = np.load(train_npz_path, allow_pickle=True)
#         X_train = np.asarray(data["X"], dtype=float)
#         y_train = np.asarray(data["y"]).ravel()
#     except Exception as e:
#         raise RuntimeError(f"Failed to load train npz: {e}")

#     # ---------------------------------------------------------
#     # CLEAN LABELS (Fix NaN, INF)
#     # ---------------------------------------------------------
#     if np.any(np.isnan(y_train)) or np.any(np.isinf(y_train)):
#         agent_log(run_id, "[automl_agent] Cleaning NaN/Inf from labels", agent="automl_agent")

#         mask = ~(np.isnan(y_train) | np.isinf(y_train))
#         X_train = X_train[mask]
#         y_train = y_train[mask]

#         if len(y_train) == 0:
#             raise RuntimeError("All labels were NaN/inf.")

#     # ---------------------------------------------------------
#     # Use LLM to pick model list
#     # ---------------------------------------------------------
#     try:
#         llm_plan = _ask_llm_plan(ps, X_train, y_train) or {}
#     except Exception:
#         llm_plan = {}

#     task_type = llm_plan.get("task_type") or ps.get("task_type") or "classification"

#     # ---------------------------------------------------------
#     # Sanitize candidate models
#     # ---------------------------------------------------------
#     raw_models = llm_plan.get("candidate_models", ["xgboost", "lgbm", "rf"])
#     estimator_list = _sanitize_candidate_models(raw_models, task_type)

#     # ---------------------------------------------------------
#     # Compute AutoML parameters
#     # ---------------------------------------------------------
#     time_budget = int(preferences.get("training_budget_minutes", 3)) * 60
#     metric = preferences.get("primary_metric") or ("f1" if task_type == "classification" else "r2")

#     settings = {
#         "time_budget": max(20, time_budget),
#         "metric": metric,
#         "task": task_type,
#         "estimator_list": estimator_list,
#         "log_file_name": f"artifacts/{run_id}_flaml.log",
#     }

#     agent_log(run_id, f"[automl_agent] AutoML settings: {settings}", agent="automl_agent")

#     # ---------------------------------------------------------
#     # Train AutoML
#     # ---------------------------------------------------------
#     automl = AutoML()
#     try:
#         automl.fit(X_train=X_train, y_train=y_train, **settings)
#     except Exception as e:
#         agent_log(run_id, f"[automl_agent] AutoML.fit FAILED: {e}\n{traceback.format_exc()}", agent="automl_agent")
#         raise

#     # ---------------------------------------------------------
#     # Save Model
#     # ---------------------------------------------------------
#     model_path = f"artifacts/{run_id}_best_model.pkl"
#     try:
#         joblib.dump(getattr(automl, "model", automl), model_path)
#     except Exception as e:
#         agent_log(run_id, f"[automl_agent] Model save failed: {e}", agent="automl_agent")
#         model_path = None

#     # ---------------------------------------------------------
#     # Leaderboard
#     # ---------------------------------------------------------
#     try:
#         lb = automl.leaderboard()
#         try:
#             leaderboard_json = lb.to_dict()
#         except:
#             leaderboard_json = str(lb)
#     except:
#         leaderboard_json = {}

#     agent_log(run_id, "[automl_agent] Completed successfully", agent="automl_agent")

#     return {
#         "artifact_uri": model_path,
#         "model_path": model_path,
#         "leaderboard": leaderboard_json,
#         "automl_settings": settings,
#         "task_type": task_type,
#     }


# ============================
#     FIXED & STABLE AutoML Agent
# ============================

import os
import json
import traceback
import numpy as np
import joblib
from flaml import AutoML

from app.utils.llm_clients import llm_generate_json
from app.utils.run_logger import agent_log


# -----------------------------------------
# SUPPORTED MODELS
# -----------------------------------------
FLAML_SUPPORTED = {
    "classification": {
        "xgboost", "xgb_limitdepth", "rf", "lgbm",
        "catboost", "extra_tree", "kneighbor",
        "svc", "sgd", "histgb"
    },
    "regression": {
        "xgboost", "rf", "lgbm",
        "extra_tree", "histgb", "sgd"
    },
}

# Normalize model names to FLAML’s internal names
ESTIMATOR_MAP = {
    "xgboost": "xgboost",
    "lightgbm": "lgbm",
    "lgbm": "lgbm",
    "random_forest": "rf",
    "rf": "rf",
    "catboost": "catboost",
    "logistic_regression": "lrl1",
    "logreg": "lrl1",
    "lr": "lrl1",
    "sgd": "sgd",
    "svc": "svc",
    "kneighbor": "kneighbor",
    "extra_tree": "extra_tree",
}


# -----------------------------------------
# LLM: Ask for candidate models
# -----------------------------------------
def _ask_llm_plan(ps: dict, X_train, y_train):
    """
    Ask LLM to produce task_type + model suggestions.
    Must return JSON only. Has fallback.
    """
    prompt = f"""
You are an ML system designer.

Problem: {ps.get('raw_text')}
First 10 labels: {list(y_train[:10])}

Return ONLY clean JSON:
{{
  "task_type": "classification" or "regression",
  "candidate_models": ["xgboost", "lgbm", "rf"],
  "hpo_suggestion": {{"time_minutes": 5}}
}}
"""

    try:
        result = llm_generate_json(prompt)
        return result or {}
    except:
        return {}


# -----------------------------------------
# SANITIZE LLM MODELS
# -----------------------------------------
def _sanitize_candidate_models(models, task):
    """Ensure the model list contains ONLY FLAML-supported models."""
    if not isinstance(models, list):
        return ["xgboost", "lgbm", "rf"]

    task = task if task in ("classification", "regression") else "classification"

    clean = []
    for m in models:
        if not isinstance(m, str):
            continue
        m = m.lower().strip()
        mapped = ESTIMATOR_MAP.get(m, m)
        if mapped in FLAML_SUPPORTED[task]:
            clean.append(mapped)

    if not clean:
        clean = ["xgboost", "lgbm", "rf"]

    # remove duplicates
    final = []
    for name in clean:
        if name not in final:
            final.append(name)

    return final


# -----------------------------------------
# MAIN AUTO ML
# -----------------------------------------
def run_automl(run_id: str, train_npz_path: str, ps: dict, preferences: dict):
    agent_log(run_id, f"[automl_agent] Loading train file: {train_npz_path}",
              agent="automl_agent")

    # LOAD TRAINING DATA
    try:
        data = np.load(train_npz_path, allow_pickle=True)
        X_train = np.asarray(data["X"])
        y_train = np.asarray(data["y"]).ravel()
    except Exception as e:
        raise RuntimeError(f"Could not load training npz: {e}")

    # CLEAN LABELS
    if np.any(np.isnan(y_train)) or np.any(np.isinf(y_train)):
        agent_log(run_id,
                  "[automl_agent] WARNING: NaN/Inf labels detected—cleaning...",
                  agent="automl_agent")

        mask = ~(np.isnan(y_train) | np.isinf(y_train))
        X_train = X_train[mask]
        y_train = y_train[mask]

        if len(y_train) == 0:
            raise RuntimeError("All labels were NaN/inf. Nothing to train on.")

    # ---------------------------
    # TASK TYPE: from LLM or PS agent
    # ---------------------------
    try:
        llm_plan = _ask_llm_plan(ps, X_train, y_train)
    except:
        llm_plan = {}

    task_type = llm_plan.get("task_type") or ps.get("task_type")
    if task_type not in ["classification", "regression"]:
        # Auto-detect task
        if len(np.unique(y_train)) > 20:
            task_type = "regression"
        else:
            task_type = "classification"

    # ---------------------------
    # AUTO METRIC FIX (IMPORTANT)
    # ---------------------------
    given_metric = preferences.get("primary_metric")

    if task_type == "regression":
        # Never allow classification metrics in regression
        if given_metric in ["f1", "accuracy", "precision", "recall"]:
            metric = "r2"
        else:
            metric = given_metric or "r2"
    else:
        # classification - detect multiclass
        n_classes = len(np.unique(y_train))
        
        if n_classes > 2:
            # Multiclass: use accuracy or macro_f1
            if given_metric == "f1":
                metric = "macro_f1"  # FLAML's multiclass F1
            elif given_metric in ["accuracy", "log_loss", "roc_auc_ovr", "roc_auc_ovo"]:
                metric = given_metric
            else:
                metric = "accuracy"  # Safe default for multiclass
        else:
            # Binary classification
            metric = given_metric or "f1"

    # ---------------------------
    # MODEL LIST SELECTION
    # ---------------------------
    raw_candidates = llm_plan.get("candidate_models", ["xgboost", "lgbm", "rf"])
    est_list = _sanitize_candidate_models(raw_candidates, task_type)

    # ---------------------------
    # TIME BUDGET
    # ---------------------------
    time_budget = int(preferences.get("training_budget_minutes", 5)) * 60  # Increased default from 3 to 5 minutes

    # ---------------------------
    # SETTINGS FOR BETTER ACCURACY
    # ---------------------------
    settings = {
        "time_budget": max(60, time_budget),  # Minimum 60 seconds (increased from 30)
        "metric": metric,
        "task": task_type,
        "estimator_list": est_list,
        "log_file_name": f"artifacts/{run_id}_flaml.log",
        "n_jobs": -1,  # Use all CPU cores for faster training
        "eval_method": "cv",  # Use cross-validation for better model selection
        "n_splits": 3,  # 3-fold cross-validation
        "early_stop": True,  # Enable early stopping
        "verbose": 0,  # Reduce logging noise
    }

    agent_log(run_id, f"[automl_agent] Settings: {settings}",
              agent="automl_agent")

    # ---------------------------
    # TRAIN MODEL
    # ---------------------------
    automl = AutoML()

    try:
        automl.fit(X_train=X_train, y_train=y_train, **settings)
    except Exception as e:
        agent_log(run_id,
                  f"[automl_agent] AutoML.fit FAILED: {e}\n{traceback.format_exc()}",
                  agent="automl_agent")
        raise

    # ---------------------------
    # CHECK IF MODEL WAS TRAINED
    # ---------------------------
    if automl.model is None:
        error_msg = "AutoML training failed - no model was produced. This usually means all estimators failed during training."
        agent_log(run_id, f"[automl_agent] ERROR: {error_msg}", agent="automl_agent")
        raise RuntimeError(error_msg)

    # ---------------------------
    # SAVE MODEL
    # ---------------------------
    model_path = f"artifacts/{run_id}_best_model.pkl"
    try:
        joblib.dump(automl.model, model_path)
        agent_log(run_id, f"[automl_agent] Model saved to {model_path}", agent="automl_agent")
    except Exception as e:
        agent_log(run_id, f"[automl_agent] Failed to save automl.model, trying to save entire automl object: {e}", agent="automl_agent")
        joblib.dump(automl, model_path)

    # ---------------------------
    # LEADERBOARD & TRAINED MODELS
    # ---------------------------
    lb_json = {}
    trained_models_list = []
    
    try:
        lb = automl.leaderboard()
        lb_json = lb.to_dict()
        agent_log(run_id, f"[automl_agent] Leaderboard extracted: {list(lb_json.keys())}", agent="automl_agent")
        
        # Extract trained models from leaderboard
        if 'estimator' in lb_json and isinstance(lb_json['estimator'], list):
            estimators = lb_json['estimator']
            # Find metric column
            metric_col = None
            for col in lb_json.keys():
                if col != 'estimator' and isinstance(lb_json[col], list):
                    metric_col = col
                    break
            
            if metric_col:
                scores = lb_json[metric_col]
                for i, est in enumerate(estimators):
                    if i < len(scores):
                        trained_models_list.append({
                            "name": str(est),
                            "score": float(scores[i]) if isinstance(scores[i], (int, float)) else 0
                        })
                agent_log(run_id, f"[automl_agent] Extracted {len(trained_models_list)} models from leaderboard", agent="automl_agent")
    except Exception as e:
        agent_log(run_id, f"[automl_agent] Failed to extract leaderboard: {e}", agent="automl_agent")
        lb_json = {}
    
    # Get best model name
    best_model_name = "Unknown"
    try:
        best_model_name = type(automl.model).__name__
        agent_log(run_id, f"[automl_agent] Best model: {best_model_name}", agent="automl_agent")
    except:
        pass

    agent_log(run_id, "[automl_agent] Completed successfully",
              agent="automl_agent")

    return {
        "artifact_uri": model_path,
        "leaderboard": lb_json,
        "trained_models": trained_models_list,
        "best_model_name": best_model_name,
        "model_path": model_path,
        "automl_settings": settings,
        "task_type": task_type,
    }
