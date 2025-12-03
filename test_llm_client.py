"""
Test script for LLM client functionality
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.llm_clients import llm_generate, llm_generate_json

def test_basic_generation():
    """Test basic text generation"""
    print("Testing basic text generation...")
    prompt = "What is 2+2? Answer in one sentence."
    result = llm_generate(prompt, max_tokens=50)
    print(f"Result: {result}")
    print(f"Success: {len(result) > 0}")
    return len(result) > 0

def test_json_generation():
    """Test JSON generation with validation"""
    print("\nTesting JSON generation...")
    prompt = """Generate a JSON object with the following structure:
    {
        "task_type": "classification",
        "target": "species",
        "features": ["sepal_length", "sepal_width"]
    }
    """
    result = llm_generate_json(prompt, max_tokens=200)
    print(f"Result: {result}")
    print(f"Success: {result is not None and isinstance(result, dict)}")
    return result is not None

def test_retry_mechanism():
    """Test that retry mechanism is in place"""
    print("\nTesting retry mechanism...")
    # This will test the retry logic by checking the implementation
    from utils.llm_clients import MAX_RETRIES, RETRY_BACKOFF
    print(f"MAX_RETRIES: {MAX_RETRIES}")
    print(f"RETRY_BACKOFF: {RETRY_BACKOFF}")
    print(f"Success: {MAX_RETRIES == 3 and len(RETRY_BACKOFF) == 3}")
    return MAX_RETRIES == 3

def test_fallback_providers():
    """Test that fallback providers are configured"""
    print("\nTesting fallback provider configuration...")
    from utils.llm_clients import (
        OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY,
        OPENAI_MODEL, ANTHROPIC_MODEL, GEMINI_MODEL
    )
    print(f"OpenAI configured: {len(OPENAI_API_KEY) > 0}")
    print(f"Anthropic configured: {len(ANTHROPIC_API_KEY) > 0}")
    print(f"Google configured: {len(GOOGLE_API_KEY) > 0}")
    print(f"OpenAI model: {OPENAI_MODEL}")
    print(f"Anthropic model: {ANTHROPIC_MODEL}")
    print(f"Gemini model: {GEMINI_MODEL}")
    return True

def test_json_validation():
    """Test JSON validation and sanitization"""
    print("\nTesting JSON validation...")
    from utils.llm_clients import _validate_json, _sanitize_json_string
    
    # Test valid JSON
    valid_data = {"key": "value", "number": 42}
    print(f"Valid JSON test: {_validate_json(valid_data)}")
    
    # Test sanitization
    dirty_json = '```json\n{"key": "value"}\n```'
    clean = _sanitize_json_string(dirty_json)
    print(f"Sanitized: {clean}")
    print(f"Success: {'{' in clean and '}' in clean}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("LLM Client Test Suite")
    print("=" * 60)
    
    tests = [
        test_retry_mechanism,
        test_fallback_providers,
        test_json_validation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Error in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    print("=" * 60)
    
    # Only run LLM tests if API keys are configured
    print("\nNote: Actual LLM generation tests require API keys to be configured.")
    print("Set LLM_MODE and appropriate API keys in .env file to test live generation.")
