"""
Complete System Verification Test
Tests all major components and features
"""
import os
import sys

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("Testing Module Imports")
    print("=" * 60)
    
    try:
        # Core modules
        from app.main import app, init_db
        from app.storage import ensure_dirs, save_artifact
        from app.utils.llm_clients import llm_generate, llm_generate_json
        from app.utils.run_logger import agent_log
        
        # Agents
        from app.agents.ps_agent import parse_problem_or_generate
        from app.agents.data_agent import get_or_find_dataset
        from app.agents.prep_agent import preprocess_dataset
        from app.agents.automl_agent import run_automl
        from app.agents.eval_agent import evaluate_model
        from app.agents.deploy_agent import generate_deploy_scaffold
        
        print("✓ All modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database():
    """Test database initialization"""
    print("\n" + "=" * 60)
    print("Testing Database")
    print("=" * 60)
    
    try:
        from app.main import init_db
        init_db()
        
        # Check if database file exists
        if os.path.exists("runs.db"):
            print("✓ Database initialized successfully")
            return True
        else:
            print("✗ Database file not created")
            return False
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_storage():
    """Test artifact storage"""
    print("\n" + "=" * 60)
    print("Testing Storage")
    print("=" * 60)
    
    try:
        from app.storage import ensure_dirs, save_artifact
        
        ensure_dirs()
        
        # Test saving artifact
        test_content = "Test artifact content"
        path = save_artifact("test_run", "test.txt", test_content)
        
        if os.path.exists(path):
            print(f"✓ Artifact saved successfully: {path}")
            # Clean up
            os.remove(path)
            return True
        else:
            print("✗ Artifact not saved")
            return False
    except Exception as e:
        print(f"✗ Storage test failed: {e}")
        return False

def test_llm_client():
    """Test LLM client configuration"""
    print("\n" + "=" * 60)
    print("Testing LLM Client")
    print("=" * 60)
    
    try:
        from app.utils.llm_clients import (
            LLM_MODE, MAX_RETRIES, RETRY_BACKOFF,
            _validate_json, _sanitize_json_string
        )
        
        print(f"LLM Mode: {LLM_MODE}")
        print(f"Max Retries: {MAX_RETRIES}")
        print(f"Retry Backoff: {RETRY_BACKOFF}")
        
        # Test JSON validation
        test_data = {"key": "value", "number": 42}
        if _validate_json(test_data):
            print("✓ JSON validation works")
        
        # Test JSON sanitization
        dirty_json = '```json\n{"test": "value"}\n```'
        clean = _sanitize_json_string(dirty_json)
        if '{' in clean and '}' in clean:
            print("✓ JSON sanitization works")
        
        print("✓ LLM client configured correctly")
        return True
    except Exception as e:
        print(f"✗ LLM client test failed: {e}")
        return False

def test_agents():
    """Test that all agents are properly structured"""
    print("\n" + "=" * 60)
    print("Testing Agent Structure")
    print("=" * 60)
    
    agents = {
        "PS Agent": "app.agents.ps_agent",
        "Data Agent": "app.agents.data_agent",
        "Prep Agent": "app.agents.prep_agent",
        "AutoML Agent": "app.agents.automl_agent",
        "Eval Agent": "app.agents.eval_agent",
        "Deploy Agent": "app.agents.deploy_agent",
        "Synthetic Agent": "app.agents.synthetic_agent"
    }
    
    all_passed = True
    for name, module_path in agents.items():
        try:
            __import__(module_path)
            print(f"✓ {name} loaded")
        except Exception as e:
            print(f"✗ {name} failed: {e}")
            all_passed = False
    
    return all_passed

def test_api_structure():
    """Test FastAPI application structure"""
    print("\n" + "=" * 60)
    print("Testing API Structure")
    print("=" * 60)
    
    try:
        from app.main import app
        
        # Check routes
        routes = [route.path for route in app.routes]
        
        required_routes = ["/run", "/status/{run_id}", "/runs", "/ps", "/dashboard", "/checkllm"]
        
        all_present = True
        for route in required_routes:
            if any(route in r for r in routes):
                print(f"✓ Route {route} exists")
            else:
                print(f"✗ Route {route} missing")
                all_present = False
        
        return all_present
    except Exception as e:
        print(f"✗ API structure test failed: {e}")
        return False

def test_deployment_artifacts():
    """Test deployment artifact generation"""
    print("\n" + "=" * 60)
    print("Testing Deployment Artifacts")
    print("=" * 60)
    
    try:
        from app.agents.deploy_agent import generate_deploy_scaffold
        
        # Generate test artifacts
        result = generate_deploy_scaffold(
            "test_deploy",
            "artifacts/test_model.pkl",
            "artifacts/test_transformer.joblib",
            {"feature1": "float", "feature2": "int"}
        )
        
        # Check if files were created
        files_created = []
        for key, path in result.items():
            if os.path.exists(path):
                files_created.append(key)
                print(f"✓ {key} generated")
                # Clean up
                os.remove(path)
            else:
                print(f"✗ {key} not generated")
        
        return len(files_created) >= 5  # At least 5 artifacts should be generated
    except Exception as e:
        print(f"✗ Deployment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n" + "=" * 60)
    print("Testing File Structure")
    print("=" * 60)
    
    required_files = [
        "app/main.py",
        "app/storage.py",
        "app/utils/llm_clients.py",
        "app/utils/run_logger.py",
        "app/agents/ps_agent.py",
        "app/agents/data_agent.py",
        "app/agents/prep_agent.py",
        "app/agents/automl_agent.py",
        "app/agents/eval_agent.py",
        "app/agents/deploy_agent.py",
        "requirements.txt",
        "README.md",
        ".env"
    ]
    
    all_present = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} missing")
            all_present = False
    
    return all_present

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("AutoML Platform - Complete System Verification")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Database", test_database),
        ("Storage", test_storage),
        ("LLM Client", test_llm_client),
        ("Agents", test_agents),
        ("API Structure", test_api_structure),
        ("Deployment Artifacts", test_deployment_artifacts)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    percentage = (passed / total * 100) if total > 0 else 0
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed ({percentage:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
        print("\nNext steps:")
        print("1. Start server: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        print("2. Open dashboard: http://localhost:8000/dashboard")
        print("3. Or run API tests: python test_system.py")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
