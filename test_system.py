"""
Comprehensive system test for AutoML platform
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/checkllm", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_ps_interactive():
    """Test problem statement generation"""
    print("\n" + "=" * 60)
    print("Testing Problem Statement Generation")
    print("=" * 60)
    
    payload = {
        "have_ps": False,
        "problem_statement": "",
        "preferences": {},
        "hint": "loan default prediction"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/ps", json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Mode: {result.get('mode')}")
        if result.get('ps_options'):
            print(f"Generated {len(result['ps_options'])} options")
            for i, opt in enumerate(result['ps_options'][:2]):
                print(f"\nOption {i+1}: {opt.get('title')}")
                print(f"Statement: {opt.get('statement', '')[:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"PS test failed: {e}")
        return False

def test_full_run():
    """Test complete ML pipeline"""
    print("\n" + "=" * 60)
    print("Testing Full ML Pipeline")
    print("=" * 60)
    
    payload = {
        "problem_statement": "Predict loan default based on customer features",
        "user": {},
        "preferences": {
            "training_budget_minutes": 1,
            "primary_metric": "f1",
            "allow_synthetic": True
        }
    }
    
    try:
        # Start run
        response = requests.post(f"{BASE_URL}/run", json=payload, timeout=10)
        print(f"Run started: {response.status_code}")
        result = response.json()
        run_id = result.get("run_id")
        print(f"Run ID: {run_id}")
        
        if not run_id:
            print("Failed to get run ID")
            return False
        
        # Poll status
        max_polls = 60  # 5 minutes max
        for i in range(max_polls):
            time.sleep(5)
            status_response = requests.get(f"{BASE_URL}/status/{run_id}", timeout=10)
            status_data = status_response.json()
            
            current_status = status_data.get("status")
            phase = status_data.get("state", {}).get("phase", "unknown")
            
            print(f"\nPoll {i+1}: Status={current_status}, Phase={phase}")
            
            if current_status == "completed":
                print("\n✓ Run completed successfully!")
                print(f"Artifacts: {status_data.get('artifacts', [])}")
                print(f"Metrics: {status_data.get('state', {}).get('metrics', {})}")
                return True
            elif current_status == "failed":
                print(f"\n✗ Run failed: {status_data.get('last_error')}")
                print(f"Log tail:\n{status_data.get('log_tail', '')[-500:]}")
                return False
        
        print("\n⚠ Run timed out")
        return False
        
    except Exception as e:
        print(f"Full run test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("AutoML System Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Health
    results['health'] = test_health()
    
    # Test 2: PS Generation
    results['ps_generation'] = test_ps_interactive()
    
    # Test 3: Full Pipeline
    results['full_pipeline'] = test_full_run()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
