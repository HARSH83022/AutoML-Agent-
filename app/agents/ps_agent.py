# # app/agents/ps_agent.py

# import re
# import json
# from typing import Dict
# from app.utils.llm_clients import llm_generate_json


# # -----------------------------------------------------
# # PROMPTS
# # -----------------------------------------------------

# def _prompt_parse_ps(text, preferences):
#     return f"""
# You are a data scientist assistant. Parse the following problem statement into JSON with keys:
# task_type, domain, target, entities (list), keywords (list), constraints (object), plan (object).

# Preferences: {json.dumps(preferences)}

# Input:
# \"\"\"{text}\"\"\"

# Return ONLY valid JSON. No explanation. No extra text.
# """


# def _prompt_generate_ps_options(hints):
#     return f"""
# You are an expert ML problem designer.
# User needs a structured machine-learning problem statement.

# Based on the user's hints:
# \"\"\"{hints}\"\"\"

# Generate **3 problem statement OPTIONS**, each with:
# - title
# - statement
# - task_type (classification or regression)
# - metrics (list)
# - domain
# - target (if applicable)

# Return ONLY JSON in the format:
# {{
#   "options": [
#     {{
#       "title": "...",
#       "statement": "...",
#       "task_type": "...",
#       "domain": "...",
#       "target": "...",
#       "metrics": ["f1","roc_auc"]
#     }},
#     ...
#   ]
# }}
# """


# # -----------------------------------------------------
# # FALLBACK PARSER (when LLM fails)
# # -----------------------------------------------------

# def fallback_parse(text, preferences):
#     t = (text or "").lower()
#     out = {
#         "task_type": "classification",
#         "domain": preferences.get("domain", "general"),
#         "target": None,
#         "entities": [],
#         "keywords": [],
#         "constraints": preferences
#     }

#     if "regress" in t or "predict value" in t:
#         out["task_type"] = "regression"

#     m = re.search(r"(target|label|predict)\s*[:=]?\s*([a-zA-Z0-9_]+)", text or "")
#     if m:
#         out["target"] = m.group(2)

#     for w in ["loan", "default", "credit", "fraud", "churn", "price",
#               "transaction", "customer", "age", "income"]:
#         if w in t:
#             out["keywords"].append(w)

#     out["plan"] = {
#         "required_modalities": ["tabular"],
#         "candidate_models": ["xgboost", "lightgbm", "logreg"],
#         "metrics": [preferences.get("primary_metric", "f1"), "roc_auc"]
#     }

#     out["raw_text"] = text
#     return out


# # -----------------------------------------------------
# # MAIN FUNCTION FOR PS HANDLING
# # -----------------------------------------------------

# def parse_problem_or_generate(run_id, user_input: Dict):
#     """
#     Behavior:

#     1) If user says they HAVE a problem statement:
#           → parse it and return structured JSON.

#     2) If user says they DO NOT have a PS:
#           → ask for hints
#           → generate 2–3 PS options via LLM
#           → user selects one downstream.

#     user_input structure expected:
#     {
#         "has_ps": True/False,
#         "problem_statement": "...",
#         "ps_hints": "...",
#         "preferences": {...}
#     }
#     """

#     has_ps = user_input.get("has_ps")
#     ps = user_input.get("problem_statement", "")
#     hints = user_input.get("ps_hints", "")
#     preferences = user_input.get("preferences", {})

#     # ------------------------------------------------------------------
#     # CASE-1: USER ALREADY HAS A PROBLEM STATEMENT
#     # ------------------------------------------------------------------
#     if has_ps:
#         if not ps.strip():
#             return {
#                 "error": "User indicated they have a problem statement but did not provide it."
#             }

#         prompt = _prompt_parse_ps(ps, preferences)
#         j = llm_generate_json(prompt)

#         if j and isinstance(j, dict):
#             j.setdefault("task_type", "classification")
#             j.setdefault("plan", {
#                 "required_modalities": ["tabular"],
#                 "candidate_models": ["xgboost", "lightgbm", "logreg"],
#                 "metrics": [preferences.get("primary_metric", "f1"), "roc_auc"]
#             })
#             j["raw_text"] = ps
#             return j

#         # fallback
#         return fallback_parse(ps, preferences)

#     # ------------------------------------------------------------------
#     # CASE-2: USER DOES NOT HAVE A PS → We generate structured options
#     # ------------------------------------------------------------------
#     if not hints.strip():
#         return {
#             "need_hints": True,
#             "message": "Please provide hints: domain/topic/type of prediction you want (e.g. loan default, rainfall prediction, customer churn, price forecast)."
#         }

#     prompt = _prompt_generate_ps_options(hints)
#     j = llm_generate_json(prompt)

#     if j and "options" in j:
#         return j

#     # fallback options when LLM fails
#     return {
#         "options": [
#             {
#                 "title": "Loan Default Prediction",
#                 "statement": "Predict probability of loan default using customer and transaction features.",
#                 "task_type": "classification",
#                 "domain": "finance",
#                 "target": "default",
#                 "metrics": ["f1", "roc_auc"]
#             },
#             {
#                 "title": "Customer Churn Prediction",
#                 "statement": "Predict whether a customer will churn in the next 30 days using behavior logs.",
#                 "task_type": "classification",
#                 "domain": "telecom",
#                 "target": "churn",
#                 "metrics": ["precision", "recall"]
#             },
#             {
#                 "title": "House Price Regression",
#                 "statement": "Predict final sale price of a house using property and neighborhood attributes.",
#                 "task_type": "regression",
#                 "domain": "real_estate",
#                 "target": "price",
#                 "metrics": ["rmse", "mae"]
#             }
#         ]
#     }





# # app/agents/ps_agent.py
# import json
# from typing import Dict, Any, Optional
# from app.utils.llm_clients import llm_generate_json
# from app.utils.run_logger import agent_log

# def _prompt_parse_ps(text: str, preferences: Dict[str, Any], hint: Optional[str] = None) -> str:
#     hint_text = f"Topic hint: {hint}\n" if hint else ""
#     return f"""
# You are a data scientist assistant. Parse the following problem statement into JSON with keys:
# task_type, domain, target (if present), entities (list), keywords (list), constraints (object), plan (object), raw_text.

# {hint_text}
# Preferences: {json.dumps(preferences)}

# Input:
# \"\"\"{text}\"\"\"

# Return ONLY valid JSON. Do NOT include any other text.
# """

# def _prompt_generate_options(hint: Optional[str], preferences: Dict[str, Any]) -> str:
#     hint_text = hint or "general"
#     return f"""
# You are a data scientist assistant. Based on topic '{hint_text}', generate 2 to 3 concise problem-statement OPTIONS.
# Each option should be a JSON object with fields: title, statement, task_type, metrics, plan.
# Return ONLY valid JSON: {{ "options": [ {{...}}, {{...}} ] }}
# """

# def fallback_parse(text: str, preferences: Dict[str, Any], hint: Optional[str] = None) -> Dict[str, Any]:
#     t = (text or "").lower()
#     out = {
#         "task_type":"classification",
#         "domain":preferences.get("domain","general"),
#         "target":None,
#         "entities":[],
#         "keywords":[],
#         "constraints":preferences,
#         "plan":{"required_modalities":["tabular"], "candidate_models":["xgboost","lightgbm","rf"], "metrics":[preferences.get("primary_metric","f1")]},
#         "raw_text": text or hint or ""
#     }
#     if any(k in t for k in ("regress","predict value","price","amount","sale price")):
#         out["task_type"] = "regression"
#     for cand in ["price","target","label","default","churn","income","age","winner","result","vote"]:
#         if cand in t or (hint and cand in hint.lower()):
#             out["target"] = cand
#             out["keywords"].append(cand)
#     if not out["keywords"] and hint:
#         out["keywords"] = [w.strip() for w in hint.split()[:5]]
#     return out

# def parse_problem_or_generate(run_id: str, problem_statement: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
#     hint = preferences.get("hint") if isinstance(preferences, dict) else None
#     agent_log(run_id, f"[ps_agent] called with hint={hint}", agent="ps_agent")
#     if not problem_statement or problem_statement.strip() == "":
#         p = _prompt_generate_options(hint, preferences)
#         j = llm_generate_json(p)
#         if j and isinstance(j, dict) and "options" in j:
#             agent_log(run_id, "[ps_agent] generated options from LLM", agent="ps_agent")
#             return j
#         return {"options":[
#             {"title":"Loan Default Prediction","statement":"Predict probability of loan default using applicant and transaction history.","task_type":"classification","metrics":["f1","roc_auc"],"plan":{"required_modalities":["tabular"]}},
#             {"title":"Customer Churn Prediction","statement":"Predict whether a customer will churn within 90 days.","task_type":"classification","metrics":["precision","recall"],"plan":{"required_modalities":["tabular"]}},
#             {"title":"House Price Regression","statement":"Predict house sale price given property features.","task_type":"regression","metrics":["rmse","r2"],"plan":{"required_modalities":["tabular"]}}
#         ]}
#     p = _prompt_parse_ps(problem_statement, preferences, hint=hint)
#     j = llm_generate_json(p)
#     if j and isinstance(j, dict):
#         j.setdefault("task_type", "classification")
#         j.setdefault("plan", {"required_modalities":["tabular"], "candidate_models":["xgboost","lightgbm","rf"], "metrics":[preferences.get("primary_metric","f1")]})
#         j["raw_text"] = problem_statement
#         agent_log(run_id, "[ps_agent] parsed PS via LLM", agent="ps_agent")
#         return j
#     agent_log(run_id, "[ps_agent] LLM parse failed, using fallback", agent="ps_agent")
#     return fallback_parse(problem_statement, preferences, hint=hint)




# app/agents/ps_agent.py

import json
from typing import Dict, Any, Optional

from app.utils.llm_clients import llm_generate_json
from app.utils.run_logger import agent_log


# -----------------------------
# PROMPT TEMPLATES
# -----------------------------

def _prompt_parse_ps(text: str, preferences: Dict[str, Any], hint: Optional[str] = None) -> str:
    hint_text = f"Topic hint: {hint}\n" if hint else ""

    return f"""
You are an expert Machine Learning project planner.

Parse the following problem statement into STRICT JSON with fields:
- task_type: "classification" or "regression"
- domain: short description
- target: column name if identifiable else null
- entities: list
- keywords: list
- constraints: dictionary
- plan: object with fields:
    - required_modalities: ["tabular"]
    - candidate_models: list of ML models
    - metrics: list of metrics
- raw_text: copy of input PS

{hint_text}
Preferences: {json.dumps(preferences)}

Input Problem Statement:
\"\"\"{text}\"\"\"

Return ONLY VALID JSON. NO extra words.
"""


def _prompt_generate_options(hint: Optional[str], preferences: Dict[str, Any]) -> str:
    hint_text = hint or "general"

    return f"""
You are an expert ML assistant.
Generate 3 problem statement OPTIONS for topic: "{hint_text}".

Each option MUST be a JSON object:
{{
  "title": "...",
  "statement": "...",
  "task_type": "classification" or "regression",
  "metrics": ["f1", "accuracy", ...],
  "plan": {{
     "required_modalities": ["tabular"],
     "candidate_models": ["xgboost","lightgbm","rf"],
     "metrics": ["f1"]
  }}
}}

Return ONLY valid JSON in this shape:
{{
  "options": [ {{...}}, {{...}}, {{...}} ]
}}
"""


# -----------------------------
# FALLBACK (NO LLM)
# -----------------------------

def fallback_parse(text: str, preferences: Dict[str, Any], hint: Optional[str]) -> Dict[str, Any]:
    """Used when LLM fails to parse the PS."""

    t = (text or "").lower()

    out = {
        "task_type": "classification",
        "domain": preferences.get("domain", "general"),
        "target": None,
        "entities": [],
        "keywords": [],
        "constraints": preferences,
        "plan": {
            "required_modalities": ["tabular"],
            "candidate_models": ["xgboost", "lightgbm", "rf"],
            "metrics": [preferences.get("primary_metric", "f1")],
        },
        "raw_text": text or hint or "",
    }

    # detect regression
    if any(
        w in t
        for w in ["regress", "price", "amount", "value", "continuous", "prediction of value"]
    ):
        out["task_type"] = "regression"

    # detect target keywords
    for cand in ["price", "target", "label", "default", "churn", "income", "risk", "age"]:
        if cand in t or (hint and cand in hint.lower()):
            out["keywords"].append(cand)
            out["target"] = cand

    # fallback keywords from hint
    if not out["keywords"] and hint:
        out["keywords"] = hint.split()[:5]

    return out


# -----------------------------
# MAIN FUNCTION
# -----------------------------

def parse_problem_or_generate(run_id: str, problem_statement: str, preferences: Dict[str, Any]):
    """
    Entry point for PS Agent.
    Handles:
      - full PS parsing
      - PS option generation
      - fallback mode
    """

    hint = preferences.get("hint") if isinstance(preferences, dict) else None
    agent_log(run_id, f"[ps_agent] called | hint={hint}", agent="ps_agent")

    # --------------------------------------------------------------------
    # CASE 1: USER DID NOT PROVIDE A PROBLEM STATEMENT → GENERATE OPTIONS
    # --------------------------------------------------------------------
    if not problem_statement or not problem_statement.strip():
        agent_log(run_id, "[ps_agent] No PS provided → generating options", agent="ps_agent")

        prompt = _prompt_generate_options(hint, preferences)
        j = llm_generate_json(prompt)

        if j and isinstance(j, dict) and "options" in j:
            agent_log(run_id, "[ps_agent] Generated options via LLM", agent="ps_agent")
            return j

        # LLM FAILED → provide fallback options
        agent_log(run_id, "[ps_agent] LLM failed. Returning fallback options.", agent="ps_agent")
        return {
            "options": [
                {
                    "title": "Loan Default Prediction",
                    "statement": "Predict whether a customer will default on a loan.",
                    "task_type": "classification",
                    "metrics": ["f1", "roc_auc"],
                    "plan": {"required_modalities": ["tabular"]},
                },
                {
                    "title": "Customer Churn Prediction",
                    "statement": "Predict whether a customer will churn within 90 days.",
                    "task_type": "classification",
                    "metrics": ["precision", "recall"],
                    "plan": {"required_modalities": ["tabular"]},
                },
                {
                    "title": "House Price Prediction",
                    "statement": "Predict house prices from property attributes.",
                    "task_type": "regression",
                    "metrics": ["rmse", "r2"],
                    "plan": {"required_modalities": ["tabular"]},
                },
            ]
        }

    # --------------------------------------------------------------------
    # CASE 2: USER PROVIDED PROBLEM STATEMENT → PARSE IT
    # --------------------------------------------------------------------
    agent_log(run_id, "[ps_agent] Parsing user problem statement via LLM", agent="ps_agent")

    prompt = _prompt_parse_ps(problem_statement, preferences, hint)
    parsed = llm_generate_json(prompt)

    if parsed and isinstance(parsed, dict):
        # ensure minimum fields
        parsed.setdefault("task_type", "classification")
        parsed.setdefault(
            "plan",
            {
                "required_modalities": ["tabular"],
                "candidate_models": ["xgboost", "lightgbm", "rf"],
                "metrics": [preferences.get("primary_metric", "f1")],
            },
        )
        parsed["raw_text"] = problem_statement

        agent_log(run_id, "[ps_agent] Parsed PS successfully", agent="ps_agent")
        return parsed

    # --------------------------------------------------------------------
    # LLM PARSING FAILED → USE FALLBACK
    # --------------------------------------------------------------------
    agent_log(run_id, "[ps_agent] LLM parse failed → using fallback", agent="ps_agent")
    return fallback_parse(problem_statement, preferences, hint)
