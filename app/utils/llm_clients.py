# # app/utils/llm_clients.py
# import os, json, re, logging

# LLM_MODE = os.environ.get("LLM_MODE", "none").lower()
# OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
# HF_MODEL = os.environ.get("HF_MODEL", "google/flan-t5-small")

# logger = logging.getLogger("llm_clients")

# # lazy HF pipeline init
# _hf_pipe = None
# def _init_hf():
#     global _hf_pipe
#     if _hf_pipe is not None:
#         return
#     try:
#         from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
#         tok = AutoTokenizer.from_pretrained(HF_MODEL)
#         model = AutoModelForSeq2SeqLM.from_pretrained(HF_MODEL)
#         _hf_pipe = pipeline("text2text-generation", model=model, tokenizer=tok)
#     except Exception as e:
#         logger.error("HF init failed: %s", e)
#         _hf_pipe = None

# def _call_hf(prompt, max_length=256):
#     _init_hf()
#     if _hf_pipe is None:
#         raise RuntimeError("HF pipeline not available")
#     out = _hf_pipe(prompt, max_length=max_length)[0]["generated_text"]
#     return out

# def _call_ollama(prompt, model="llama2", max_tokens=512):
#     import requests
#     payload = {"model": model, "prompt": prompt, "max_tokens": max_tokens}
#     r = requests.post(OLLAMA_URL, json=payload, timeout=60)
#     r.raise_for_status()
#     return r.text

# def llm_generate(prompt: str, max_tokens: int = 256) -> str:
#     mode = LLM_MODE
#     if mode == "hf":
#         try:
#             return _call_hf(prompt, max_length=max_tokens)
#         except Exception as e:
#             logger.error("HF call failed: %s", e)
#             return ""
#     if mode == "ollama":
#         try:
#             return _call_ollama(prompt, max_tokens=max_tokens)
#         except Exception as e:
#             logger.error("Ollama call failed: %s", e)
#             return ""
#     logger.info("LLM_MODE is 'none' or unavailable - returning empty string")
#     return ""

# def llm_generate_json(prompt: str, max_tokens: int = 512, safe: bool = True):
#     text = llm_generate(prompt, max_tokens=max_tokens)
#     if not text:
#         return None
#     # strip code fences
#     json_text = re.sub(r"```(?:json)?\s*", "", text)
#     json_text = re.sub(r"\s*```$", "", json_text)
#     # locate first JSON block
#     m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", json_text)
#     if m:
#         json_text = m.group(1)
#     try:
#         return json.loads(json_text)
#     except Exception as e:
#         if not safe:
#             raise
#         logger.warning("Failed to parse JSON from LLM output: %s", e)
#         return None




# app/utils/llm_clients.py
import os
import json
import re
import logging
from typing import Optional

logger = logging.getLogger("llm_clients")
logger.setLevel(logging.INFO)

LLM_MODE = os.environ.get("LLM_MODE", "none").lower()
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama2")
HF_MODEL = os.environ.get("HF_MODEL", "google/flan-t5-small")

# HF pipeline cache
_hf_pipe = None

def _init_hf():
    global _hf_pipe
    if _hf_pipe is not None:
        return
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        # CPU-safe: force device to CPU
        tok = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(HF_MODEL)
        _hf_pipe = pipeline("text2text-generation", model=model, tokenizer=tok, device=-1)
        logger.info("HF pipeline initialized for model %s", HF_MODEL)
    except Exception as e:
        logger.exception("HF init failed: %s", e)
        _hf_pipe = None

def _call_hf(prompt: str, max_new_tokens: int = 256) -> str:
    _init_hf()
    if _hf_pipe is None:
        raise RuntimeError("HF pipeline not available")
    try:
        # Use deterministic generation by default
        out = _hf_pipe(prompt, max_new_tokens=max_new_tokens, do_sample=False)
        # the pipeline returns a list of dicts with 'generated_text'
        if isinstance(out, list) and len(out) > 0 and "generated_text" in out[0]:
            return out[0]["generated_text"]
        # fallback: string if pipeline returns other structure
        return str(out)
    except Exception as e:
        logger.exception("HF generation error: %s", e)
        raise

def _call_ollama(prompt: str, model: Optional[str] = None, max_tokens: int = 512) -> str:
    model = model or OLLAMA_MODEL
    try:
        import requests
        payload = {"model": model, "prompt": prompt, "max_tokens": max_tokens}
        r = requests.post(OLLAMA_URL, json=payload, timeout=60)
        r.raise_for_status()
        # Ollama returns JSON text body; adapt as needed
        try:
            return r.json().get("text", r.text)
        except Exception:
            return r.text
    except Exception as e:
        logger.exception("Ollama call failed: %s", e)
        raise

def llm_generate(prompt: str, max_tokens: int = 256) -> str:
    mode = LLM_MODE
    if mode == "hf":
        try:
            return _call_hf(prompt, max_new_tokens=max_tokens)
        except Exception as e:
            logger.error("HF call failed: %s", e)
            return ""
    if mode == "ollama":
        try:
            return _call_ollama(prompt, max_tokens=max_tokens)
        except Exception as e:
            logger.error("Ollama call failed: %s", e)
            return ""
    logger.info("LLM_MODE is 'none' or unavailable - returning empty string")
    return ""

def llm_generate_json(prompt: str, max_tokens: int = 512, safe: bool = True):
    """
    Call llm_generate and robustly parse JSON from its output.
    Returns Python object or None on failure (unless safe=False).
    """
    text = llm_generate(prompt, max_tokens=max_tokens)
    if not text:
        return None

    # remove triple backticks and surrounding markdown fences
    json_text = re.sub(r"```(?:json)?", "", text).strip()
    # find first {...} or [...]
    m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", json_text)
    if m:
        json_text = m.group(1)
    try:
        return json.loads(json_text)
    except Exception as e:
        logger.warning("Failed to parse JSON from LLM output: %s. LLM raw output: %s", e, text[:1000])
        if not safe:
            raise
        return None
