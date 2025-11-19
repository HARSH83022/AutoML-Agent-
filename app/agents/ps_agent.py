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



# app/agents/ps_agent.py
import re
import json
from typing import Dict, Any, Optional
from app.utils.llm_clients import llm_generate_json
from app.utils.run_logger import agent_log


def _prompt_parse_ps(text: str, preferences: Dict[str, Any], hint: Optional[str] = None) -> str:
    """LLM prompt to parse a user-provided problem statement."""
    hint_text = f"Topic hint: {hint}\n" if hint else ""
    return f"""
You are a data scientist assistant. Parse the following problem statement into structured JSON.

Return ONLY JSON with keys:
task_type, domain, target, entities, keywords, constraints, plan, raw_text.

{hint_text}
Preferences: {json.dumps(preferences)}

Input:
\"\"\"{text}\"\"\"

Return ONLY JSON.
"""


def _prompt_generate_options(hint: Optional[str], preferences: Dict[str, Any]) -> str:
    """LLM prompt to generate 2–3 problem statement options for the user's topic/hint."""
    hint_text = hint or "general topic"
    return f"""
You are a data scientist assistant. Based on topic '{hint_text}', generate 2–3 high-quality problem statement OPTIONS.

Each option must be JSON with:
title, statement, task_type, metrics, plan.

Return ONLY JSON like:
{{ "options": [ {{...}}, {{...}} ] }}
"""


def fallback_parse(text: str, preferences: Dict[str, Any], hint: Optional[str] = None) -> Dict[str, Any]:
    """Used when LLM fails — returns a deterministic safe PS structure."""
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
            "metrics": [preferences.get("primary_metric", "f1")]
        },
        "raw_text": text or hint or ""
    }

    # Regression detection
    if "regress" in t or "price" in t or "amount" in t:
        out["task_type"] = "regression"

    # simple keyword / target extraction
    for cand in ["price", "age", "income", "churn", "default"]:
        if cand in t:
            out["target"] = cand
            out["keywords"].append(cand)

    if hint and not out["keywords"]:
        out["keywords"] = hint.lower().split()[:3]

    return out


def parse_problem_or_generate(run_id: str, problem_statement: str, preferences: Dict[str, Any]):
    """
    Main entrypoint used by orchestrator and /ps endpoint.
    If problem_statement is empty => generate options.
    If provided => parse it properly.
    """
    hint = preferences.get("hint")
    agent_log(run_id, f"[ps_agent] called with hint={hint}", agent="ps_agent")

    # CASE A: User did NOT provide PS -> generate PS options
    if not problem_statement or problem_statement.strip() == "":
        prompt = _prompt_generate_options(hint, preferences)
        out = llm_generate_json(prompt)

        if out and "options" in out:
            agent_log(run_id, "[ps_agent] LLM returned PS options", agent="ps_agent")
            return out

        # fallback option set
        agent_log(run_id, "[ps_agent] LLM failed; fallback options", agent="ps_agent")
        return {
            "options": [
                {
                    "title": "Customer Churn Prediction",
                    "statement": "Predict whether a customer will churn based on behavior and demographic history.",
                    "task_type": "classification",
                    "metrics": ["f1"],
                    "plan": {"required_modalities": ["tabular"]}
                },
                {
                    "title": "Loan Default Prediction",
                    "statement": "Predict probability of loan default using applicant features.",
                    "task_type": "classification",
                    "metrics": ["roc_auc"],
                    "plan": {"required_modalities": ["tabular"]}
                }
            ]
        }

    # CASE B: User provided PS → parse it
    prompt = _prompt_parse_ps(problem_statement, preferences, hint)
    parsed = llm_generate_json(prompt)

    if parsed and isinstance(parsed, dict):
        parsed.setdefault("task_type", "classification")
        parsed.setdefault("plan", {
            "required_modalities": ["tabular"],
            "candidate_models": ["xgboost", "lightgbm"],
            "metrics": [preferences.get("primary_metric", "f1")]
        })
        parsed["raw_text"] = problem_statement
        agent_log(run_id, "[ps_agent] PS parsed via LLM", agent="ps_agent")
        return parsed

    # fallback
    agent_log(run_id, "[ps_agent] LLM parsing failed, fallback", agent="ps_agent")
    return fallback_parse(problem_statement, preferences, hint)
