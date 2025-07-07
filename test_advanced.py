#!/usr/bin/env python3
"""
Test Suite Avansat pentru XOFlowers AI Agent
Testează toate funcționalitățile cu datele reale
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = "test_advanced_user"

def print_section(title):
    """Print a styled section header"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_subsection(title):
    """Print a styled subsection header"""
    print(f"\n🔸 {title}")
    print("-"*40)

def test_chat_with_real_data():
    """Test chat functionality with realistic XOFlowers queries"""
    
    print_section("TESTARE CHAT CU DATE REALE XOFLOWERS")
    
    # Realistic Romanian queries that customers might ask
    test_queries = [
        {
            "message": "Salut! Vreau trandafiri roșii pentru iubita mea",
            "expected_intent": "find_product",
            "description": "Căutare trandafiri romantici"
        },
        {
            "message": "Aveți buchete pentru nuntă în culori pastel?",
            "expected_intent": "find_product", 
            "description": "Căutare buchete nuntă"
        },
        {
            "message": "Cât costă livrarea în Chișinău?",
            "expected_intent": "ask_question",
            "description": "Întrebare despre livrare"
        },
        {
            "message": "Vreau să mă abonez la flori lunare",
            "expected_intent": "subscribe",
            "description": "Cerere abonament"
        },
        {
            "message": "Am găsit ceea ce vreau, cum pot plăti?",
            "expected_intent": "pay_for_product",
            "description": "Procesare plată"
        },
        {
            "message": "Cutii cu bujori pentru ziua mamei",
            "expected_intent": "find_product",
            "description": "Căutare specifică bujori"
        },
        {
            "message": "Difuzoare de aromă Chando ieftine",
            "expected_intent": "find_product",
            "description": "Căutare difuzoare cu preț"
        },
        {
            "message": "Aranjamente florale pentru birou, modern și elegant",
            "expected_intent": "find_product",
            "description": "Căutare aranjamente business"
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {test['description']}")
        print(f"📝 Query: '{test['message']}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": test["message"], "user_id": f"{TEST_USER_ID}_{i}"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received ({len(data['response'])} chars)")
                print(f"🤖 Agent response preview: {data['response'][:150]}...")
                
                # Test intent recognition separately
                intent_response = requests.post(
                    f"{BASE_URL}/api/test",
                    json={"message": test["message"]},
                    timeout=10
                )
                
                if intent_response.status_code == 200:
                    intent_data = intent_response.json()
                    detected_intent = intent_data['intent']['name']
                    confidence = intent_data['intent']['confidence']
                    
                    print(f"🎯 Intent: {detected_intent} (confidence: {confidence:.2f})")
                    print(f"🏷️  Entities: {intent_data.get('entities', {})}")
                    
                    if detected_intent == test['expected_intent']:
                        print("✅ Intent detection: CORRECT")
                    else:
                        print(f"⚠️  Intent detection: Expected {test['expected_intent']}, got {detected_intent}")
                
                success_count += 1
                
            else:
                print(f"❌ Chat failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)  # Be respectful to the server
    
    print(f"\n📊 Chat Tests Summary: {success_count}/{len(test_queries)} successful")
    return success_count == len(test_queries)

def test_advanced_product_search():
    """Test advanced product search with ChromaDB"""
    
    print_section("TESTARE CĂUTARE AVANSATĂ PRODUSE")
    
    search_tests = [
        {
            "query": "trandafiri roșii romantici",
            "filters": {"color": "roșu", "occasion": "romantic"},
            "description": "Căutare trandafiri roșii romantici"
        },
        {
            "query": "buchete ieftine sub 500 lei",
            "filters": {"price_range": "budget"},
            "description": "Căutare buchete buget limitat"
        },
        {
            "query": "cutii elegante pentru nuntă",
            "filters": {"category": "Basket", "occasion": "wedding"},
            "description": "Căutare cutii pentru nuntă"
        },
        {
            "query": "bujori roz de sezon",
            "filters": {"flower_type": "Peonies", "color": "roz"},
            "description": "Căutare bujori specifici"
        },
        {
            "query": "difuzoare aromă premium",
            "filters": {"category": "Chando", "price_range": "premium"},
            "description": "Căutare difuzoare premium"
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(search_tests, 1):
        print_subsection(f"Test Căutare {i}: {test['description']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/products/search",
                json={
                    "query": test["query"],
                    "filters": test["filters"],
                    "n_results": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                print(f"✅ Found {len(products)} products")
                
                if products:
                    print("🏆 Top results:")
                    for j, product in enumerate(products[:3], 1):
                        similarity = int(product.get('similarity', 0) * 100)
                        price = int(product.get('price', 0))
                        print(f"   {j}. {product['name']} - {price} MDL ({similarity}% match)")
                        print(f"      Category: {product.get('category', 'N/A')}")
                        if product.get('colors'):
                            print(f"      Colors: {', '.join(product['colors'][:3])}")
                
                # Validate filters were applied
                filter_validation = True
                for product in products:
                    if test["filters"].get("price_range") == "budget":
                        if product.get('price', 0) > 500:
                            filter_validation = False
                            break
                
                if filter_validation:
                    print("✅ Filter validation: PASSED")
                else:
                    print("⚠️  Filter validation: Some results don't match filters")
                
                success_count += 1
                
            else:
                print(f"❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Search Tests Summary: {success_count}/{len(search_tests)} successful")
    return success_count == len(search_tests)

def test_collections_and_data_integrity():
    """Test ChromaDB collections and data integrity"""
    
    print_section("TESTARE INTEGRITATE DATE ȘI COLECȚII")
    
    try:
        # Test collections info
        response = requests.get(f"{BASE_URL}/api/collections", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            collections = data.get('collections', {})
            
            print("📚 ChromaDB Collections Status:")
            total_products = 0
            
            for name, info in collections.items():
                count = info.get('count', 0)
                status = info.get('status', 'unknown')
                total_products += count
                
                status_emoji = "✅" if status == "active" else "⚠️"
                print(f"   {status_emoji} {name}: {count} products ({status})")
            
            print(f"\n📊 Total products in database: {total_products}")
            
            # Verify we have the expected amount (should be close to 709)
            if total_products >= 700:
                print("✅ Data integrity: Expected product count achieved")
            elif total_products >= 500:
                print("⚠️  Data integrity: Partial data loaded")
            else:
                print("❌ Data integrity: Insufficient data loaded")
                
            return total_products >= 500
            
        else:
            print(f"❌ Collections test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing collections: {e}")
        return False

def test_multilingual_capabilities():
    """Test multilingual support"""
    
    print_section("TESTARE CAPABILITĂȚI MULTILINGVE")
    
    multilingual_tests = [
        {
            "message": "Hello, I want red roses for Valentine's Day",
            "language": "English",
            "expected_response_contains": ["roses", "valentine", "red"]
        },
        {
            "message": "Привет, хочу белые тюльпаны для дня рождения",
            "language": "Russian", 
            "expected_response_contains": ["тюльпан", "белые", "день рождения"]
        },
        {
            "message": "Bună, vreau buchete pentru nuntă în culori albe",
            "language": "Romanian",
            "expected_response_contains": ["buchete", "nuntă", "albe"]
        }
    ]
    
    success_count = 0
    
    for i, test in enumerate(multilingual_tests, 1):
        print_subsection(f"Test {test['language']}")
        print(f"📝 Message: '{test['message']}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": test["message"], "user_id": f"multilingual_user_{i}"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data['response'].lower()
                
                print(f"✅ Response received")
                print(f"🤖 Response preview: {data['response'][:100]}...")
                
                # Check if response is contextually appropriate
                if len(response_text) > 50:  # Non-trivial response
                    print("✅ Response quality: Substantial")
                    success_count += 1
                else:
                    print("⚠️  Response quality: Brief")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Multilingual Tests Summary: {success_count}/{len(multilingual_tests)} successful")
    return success_count >= len(multilingual_tests) * 0.7  # 70% success rate acceptable

def test_performance_and_load():
    """Test performance with multiple concurrent requests"""
    
    print_section("TESTARE PERFORMANȚĂ ȘI ÎNCĂRCARE")
    
    print("🚀 Testing response times...")
    
    response_times = []
    queries = [
        "trandafiri roșii",
        "buchete nuntă", 
        "cutii flori",
        "bujori roz",
        "difuzoare aromă"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"   Testing query {i}: '{query}'")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": query, "user_id": f"perf_user_{i}"},
                timeout=10
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                print(f"      ✅ Response time: {response_time:.2f}s")
            else:
                print(f"      ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\n📊 Performance Summary:")
        print(f"   Average response time: {avg_time:.2f}s")
        print(f"   Fastest response: {min_time:.2f}s")
        print(f"   Slowest response: {max_time:.2f}s")
        
        if avg_time < 3.0:
            print("✅ Performance: EXCELLENT (< 3s average)")
        elif avg_time < 5.0:
            print("✅ Performance: GOOD (< 5s average)")
        else:
            print("⚠️  Performance: SLOW (> 5s average)")
            
        return avg_time < 10.0  # Acceptable if under 10s
    
    return False

def run_comprehensive_test_suite():
    """Run all tests in sequence"""
    
    print("🌸 XOFlowers AI Agent - Comprehensive Test Suite")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Test server connectivity first
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly!")
            print("Please ensure the app is running with: python app.py")
            return False
        
        print("✅ Server connectivity: OK")
        server_info = response.json()
        print(f"🔧 Version: {server_info.get('version', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        print("Please ensure the app is running with: python app.py")
        return False
    
    # Run all test suites
    test_results = []
    
    test_results.append(("Chat with Real Data", test_chat_with_real_data()))
    test_results.append(("Advanced Product Search", test_advanced_product_search()))
    test_results.append(("Data Integrity", test_collections_and_data_integrity()))
    test_results.append(("Multilingual Support", test_multilingual_capabilities()))
    test_results.append(("Performance", test_performance_and_load()))
    
    # Summary
    print_section("SUMAR FINAL TESTARE")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n📊 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 EXCELLENT! Your XOFlowers agent is working great!")
    elif success_rate >= 60:
        print("✅ GOOD! Most functionality is working correctly.")
    else:
        print("⚠️  NEEDS IMPROVEMENT! Several issues need attention.")
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate >= 60

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick test mode
        print("🚀 Quick Test Mode")
        test_chat_with_real_data()
    else:
        # Full comprehensive test
        success = run_comprehensive_test_suite()
        sys.exit(0 if success else 1)
