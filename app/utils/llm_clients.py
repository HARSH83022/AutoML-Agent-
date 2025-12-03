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

import os
import json
import re
import logging
import time
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger("llm_clients")

# ===============================
# ENV CONFIG
# ===============================
LLM_MODE = os.environ.get("LLM_MODE", "none").lower()

# OpenAI settings
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4-turbo-preview")

# Anthropic settings
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

# Google Gemini settings
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")

# OLLAMA settings
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:latest")

# HF settings
HF_MODEL = os.environ.get("HF_MODEL", "google/flan-t5-small")

# Retry settings
MAX_RETRIES = 3
RETRY_BACKOFF = [1, 2, 4]  # seconds

_hf_pipe = None


# ===============================
# HUGGINGFACE LLM
# ===============================
def _init_hf():
    """Initialize HF pipeline once."""
    global _hf_pipe
    if _hf_pipe:
        return
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
        tok = AutoTokenizer.from_pretrained(HF_MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(HF_MODEL)
        _hf_pipe = pipeline("text2text-generation", model=model, tokenizer=tok)
        logger.info("HF model loaded OK")
    except Exception as e:
        logger.error(f"HF init failed: {e}")
        _hf_pipe = None


def _call_hf(prompt, max_length=256):
    _init_hf()
    if _hf_pipe is None:
        raise RuntimeError("HF pipeline not available")
    out = _hf_pipe(prompt, max_new_tokens=max_length)[0]["generated_text"]
    return out


# ===============================
# OLLAMA LLM (STREAMING FIXED)
# ===============================
def _call_ollama(prompt, model=OLLAMA_MODEL, max_tokens=256):
    """
    Calls Ollama and combines stream chunks into a clean final string.
    """
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "max_tokens": max_tokens},
            stream=True,
            timeout=60
        )

        resp.raise_for_status()

        final_text = ""

        # Ollama returns EACH TOKEN as a JSON line!
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line.decode("utf-8"))
                part = chunk.get("response", "")
                final_text += part
            except json.JSONDecodeError:
                # Ignore malformed chunks
                continue

        return final_text.strip()

    except Exception as e:
        logger.error(f"Ollama call failed: {e}")
        return ""


# ===============================
# OPENAI LLM
# ===============================
def _call_openai(prompt: str, max_tokens: int = 256) -> str:
    """Call OpenAI API"""
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI call failed: {e}")
        raise


# ===============================
# ANTHROPIC LLM
# ===============================
def _call_anthropic(prompt: str, max_tokens: int = 256) -> str:
    """Call Anthropic Claude API"""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        message = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    except Exception as e:
        logger.error(f"Anthropic call failed: {e}")
        raise


# ===============================
# GOOGLE GEMINI LLM
# ===============================
def _call_gemini(prompt: str, max_tokens: int = 256) -> str:
    """Call Google Gemini API"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini call failed: {e}")
        raise


# ===============================
# RETRY WITH EXPONENTIAL BACKOFF
# ===============================
def _retry_with_backoff(func, *args, **kwargs) -> Optional[str]:
    """
    Retry function with exponential backoff.
    Returns None if all attempts fail.
    """
    for attempt in range(MAX_RETRIES):
        try:
            result = func(*args, **kwargs)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_BACKOFF[attempt]
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    logger.error(f"All {MAX_RETRIES} attempts failed")
    return None


# ===============================
# GENERIC LLM CALL WITH FALLBACK
# ===============================
def llm_generate(prompt: str, max_tokens: int = 256) -> str:
    """
    Generate text from LLM with automatic fallback.
    Tries primary provider, then falls back to others if available.
    """
    # Try primary provider based on LLM_MODE
    if LLM_MODE == "openai" and OPENAI_API_KEY:
        result = _retry_with_backoff(_call_openai, prompt, max_tokens)
        if result:
            return result
        logger.warning("OpenAI failed, trying fallback...")
    
    if LLM_MODE == "anthropic" and ANTHROPIC_API_KEY:
        result = _retry_with_backoff(_call_anthropic, prompt, max_tokens)
        if result:
            return result
        logger.warning("Anthropic failed, trying fallback...")
    
    if LLM_MODE == "gemini" and GOOGLE_API_KEY:
        result = _retry_with_backoff(_call_gemini, prompt, max_tokens)
        if result:
            return result
        logger.warning("Gemini failed, trying fallback...")
    
    if LLM_MODE == "hf":
        result = _retry_with_backoff(_call_hf, prompt, max_tokens)
        if result:
            return result
        logger.warning("HuggingFace failed, trying fallback...")
    
    if LLM_MODE == "ollama":
        result = _retry_with_backoff(_call_ollama, prompt, max_tokens=max_tokens)
        if result:
            return result
        logger.warning("Ollama failed...")
    
    # Try fallback providers if primary failed
    fallback_providers = []
    
    if LLM_MODE != "openai" and OPENAI_API_KEY:
        fallback_providers.append(("OpenAI", _call_openai))
    if LLM_MODE != "anthropic" and ANTHROPIC_API_KEY:
        fallback_providers.append(("Anthropic", _call_anthropic))
    if LLM_MODE != "gemini" and GOOGLE_API_KEY:
        fallback_providers.append(("Gemini", _call_gemini))
    if LLM_MODE != "ollama":
        fallback_providers.append(("Ollama", lambda p, m: _call_ollama(p, max_tokens=m)))
    
    for provider_name, provider_func in fallback_providers:
        logger.info(f"Trying fallback provider: {provider_name}")
        result = _retry_with_backoff(provider_func, prompt, max_tokens)
        if result:
            logger.info(f"Fallback to {provider_name} succeeded")
            return result
    
    logger.error("All LLM providers failed")
    return ""


# ===============================
# JSON OUTPUT HANDLING WITH VALIDATION
# ===============================
def _validate_json(data: Any) -> bool:
    """Validate that data is valid JSON-serializable"""
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False


def _sanitize_json_string(text: str) -> str:
    """Clean and extract JSON from LLM response"""
    if not text:
        return ""
    
    # Remove markdown code fences
    clean = re.sub(r"```(?:json)?", "", text)
    clean = clean.replace("```", "").strip()
    
    # Try to extract JSON object or array
    # Look for outermost braces/brackets
    match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", clean)
    if match:
        clean = match.group(1)
    
    return clean


def llm_generate_json(prompt: str, max_tokens: int = 512, safe: bool = True) -> Optional[Dict[str, Any]]:
    """
    Generate JSON response from LLM with validation and sanitization.
    
    Args:
        prompt: The prompt to send to LLM
        max_tokens: Maximum tokens in response
        safe: If True, return None on error; if False, raise exception
    
    Returns:
        Parsed JSON dict/list or None if parsing fails
    """
    text = llm_generate(prompt, max_tokens=max_tokens)
    if not text:
        logger.warning("LLM returned empty response")
        return None
    
    # Sanitize and extract JSON
    clean_text = _sanitize_json_string(text)
    
    if not clean_text:
        logger.warning("No JSON found in LLM response")
        return None
    
    # Try to parse JSON
    try:
        data = json.loads(clean_text)
        
        # Validate it's JSON-serializable
        if not _validate_json(data):
            logger.warning("Parsed data is not JSON-serializable")
            return None
        
        return data
        
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON from LLM output: {e}")
        logger.debug(f"Raw LLM output: {text[:500]}")
        logger.debug(f"Cleaned text: {clean_text[:500]}")
        
        if not safe:
            raise
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing JSON: {e}")
        if not safe:
            raise
        return None
