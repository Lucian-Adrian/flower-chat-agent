#!/usr/bin/env python3
"""
Test Runner for XOFlowers AI System
Runs all tests and provides a summary
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run([
            sys.executable, str(test_file)
        ], capture_output=False, text=True, cwd=os.path.dirname(__file__))
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Run all tests"""
    print("🌸 XOFlowers AI System Test Runner")
    print("=" * 60)
    
    # Test files to run
    test_files = [
        "tests/integration/test_logging.py",
        "tests/integration/test_openai.py", 
        "tests/integration/test_xoflowers_ai.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        if os.path.exists(test_file):
            results[test_file] = run_test_file(test_file)
        else:
            print(f"❌ Test file not found: {test_file}")
            results[test_file] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = 0
    failed = 0
    
    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {test_file}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
