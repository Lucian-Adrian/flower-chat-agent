#!/usr/bin/env python3
"""
Quick Test pentru XOFlowers Flask App
Testează dacă toate componentele funcționează
"""

import sys
import traceback

def test_imports():
    """Test all imports"""
    print("🧪 Testing imports...")
    
    try:
        from app import app, agent, ai_agent, ULTRA_MODE
        print("✅ Main app imports: OK")
        
        print(f"   - ULTRA_MODE: {ULTRA_MODE}")
        print(f"   - Agent available: {agent is not None}")
        print(f"   - AI Agent available: {ai_agent is not None}")
        
        if ULTRA_MODE and ai_agent:
            stats = ai_agent.get_performance_stats()
            print(f"   - Database size: {stats['database_size']} products")
            print(f"   - Average query time: {stats['avg_query_time']:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_endpoints():
    """Test if Flask app can be created"""
    print("\n🧪 Testing Flask app...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test home endpoint
            response = client.get('/')
            print(f"✅ Home endpoint: {response.status_code}")
            
            # Test ULTRA endpoints if available
            if ULTRA_MODE:
                response = client.get('/api/test-ultra')
                print(f"✅ Test ULTRA endpoint: {response.status_code}")
                
                # Test ultra search
                response = client.post('/api/ultra-search', 
                                     json={'query': 'trandafiri roșii', 'user_id': 'test_user'})
                print(f"✅ Ultra search endpoint: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"   - Found {data.get('total_found', 0)} results")
                    if data.get('results'):
                        best = data['results'][0]
                        print(f"   - Best match: {best['title']} (confidence: {best['confidence']:.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Flask test error: {e}")
        traceback.print_exc()
        return False

def test_ultra_search():
    """Test ULTRA search functionality"""
    print("\n🧪 Testing ULTRA search directly...")
    
    try:
        from ai_agent_integration import create_ai_agent
        
        agent = create_ai_agent()
        
        test_queries = [
            "trandafiri roșii pentru iubire",
            "buchet elegant",
            "ceva ieftin"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            results = agent.intelligent_search(query, max_results=2)
            
            if results:
                print(f"   ✅ Found {len(results)} results")
                best = results[0]
                print(f"   📦 Best: {best.title}")
                print(f"   💰 Price: {best.price} MDL ({best.price_tier})")
                print(f"   🎯 Confidence: {best.confidence:.2f}")
                print(f"   ⚡ Time: {best.search_time:.3f}s")
            else:
                print(f"   ❌ No results found")
        
        return True
        
    except Exception as e:
        print(f"❌ ULTRA search test error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 XOFlowers Flask App - Complete Test Suite")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Imports
    if test_imports():
        tests_passed += 1
    
    # Test 2: Flask endpoints
    if test_endpoints():
        tests_passed += 1
    
    # Test 3: ULTRA search
    if test_ultra_search():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Flask app is ready to run!")
        print("\n💡 To start the server, run:")
        print("   python app.py")
        print("\n🌐 Then test at: http://127.0.0.1:5000")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
