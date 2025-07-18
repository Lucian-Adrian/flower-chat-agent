#!/usr/bin/env python3
"""
Deployment Testing Script
Tests the deployed application to ensure all components are working
"""

import sys
import time
import requests
import json
from pathlib import Path

def test_health_endpoints():
    """Test all health check endpoints"""
    print("🏥 Testing Health Endpoints...")
    
    endpoints = [
        ("Liveness", "http://localhost:8000/health/live"),
        ("Readiness", "http://localhost:8000/health/ready"),
        ("Comprehensive", "http://localhost:8000/health")
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {name}: OK")
                if name == "Comprehensive":
                    data = response.json()
                    print(f"     Status: {data.get('status')}")
                    print(f"     Uptime: {data.get('uptime_seconds', 0):.1f}s")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            return False
    
    return True

def test_api_endpoints():
    """Test main API endpoints"""
    print("\n🔌 Testing API Endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get("http://localhost:8000/", timeout=10)
        if response.status_code == 200:
            print("  ✅ Root endpoint: OK")
        else:
            print(f"  ❌ Root endpoint: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Root endpoint: {e}")
        return False
    
    # Test business info endpoint
    try:
        response = requests.get("http://localhost:8000/api/business-info", timeout=10)
        if response.status_code == 200:
            print("  ✅ Business info: OK")
        else:
            print(f"  ❌ Business info: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Business info: {e}")
        return False
    
    # Test metrics endpoint
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=10)
        if response.status_code == 200:
            print("  ✅ Metrics: OK")
        else:
            print(f"  ❌ Metrics: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Metrics: {e}")
        return False
    
    return True

def test_chat_api():
    """Test the main chat API"""
    print("\n💬 Testing Chat API...")
    
    test_message = {
        "message": "Hello, this is a test message",
        "user_id": "test_user_123",
        "platform": "api"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json=test_message,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Chat API: OK")
            print(f"     Response: {data.get('response', '')[:100]}...")
            print(f"     Success: {data.get('success')}")
            print(f"     Processing time: {data.get('processing_time', 0):.3f}s")
            return True
        else:
            print(f"  ❌ Chat API: HTTP {response.status_code}")
            print(f"     Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"  ❌ Chat API: {e}")
        return False

def test_documentation():
    """Test API documentation endpoints"""
    print("\n📚 Testing Documentation...")
    
    docs_endpoints = [
        ("Swagger UI", "http://localhost:8000/docs"),
        ("ReDoc", "http://localhost:8000/redoc")
    ]
    
    for name, url in docs_endpoints:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {name}: OK")
            else:
                print(f"  ❌ {name}: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            return False
    
    return True

def wait_for_service(max_wait=60):
    """Wait for service to be ready"""
    print(f"⏳ Waiting for service to be ready (max {max_wait}s)...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8000/health/live", timeout=5)
            if response.status_code == 200:
                print("  ✅ Service is ready!")
                return True
        except:
            pass
        
        print("  ⏳ Waiting...")
        time.sleep(5)
    
    print("  ❌ Service failed to become ready")
    return False

def main():
    """Main testing function"""
    print("🧪 XOFlowers AI Agent - Deployment Testing")
    print("=" * 50)
    
    # Wait for service to be ready
    if not wait_for_service():
        print("\n💥 Service is not ready - aborting tests")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Health Endpoints", test_health_endpoints),
        ("API Endpoints", test_api_endpoints),
        ("Chat API", test_chat_api),
        ("Documentation", test_documentation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} test failed")
        except Exception as e:
            print(f"\n💥 {test_name} test error: {e}")
    
    # Summary
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment is successful.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()