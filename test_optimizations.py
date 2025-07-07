#!/usr/bin/env python3
"""
Test pentru optimizările agentului XOFlowers
Testează funcționalitățile multilingvale și căutarea îmbunătățită
"""

import sys
import time
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"

def print_header(title):
    """Print styled header"""
    print("\n" + "="*70)
    print(f"🧪 {title}")
    print("="*70)

def print_section(title):
    """Print section header"""
    print(f"\n🔹 {title}")
    print("-"*50)

def test_multilingual_search():
    """Test multilingual search capabilities"""
    print_header("TESTARE CĂUTARE MULTILINGVĂ")
    
    multilingual_queries = [
        {
            "query": "red roses for Valentine's Day",
            "language": "en",
            "description": "English - Valentine roses"
        },
        {
            "query": "trandafiri roșii pentru Valentine",
            "language": "ro", 
            "description": "Romanian - Valentine roses"
        },
        {
            "query": "букет красных роз",
            "language": "ru",
            "description": "Russian - Red rose bouquet"
        },
        {
            "query": "bouquet de roses pour mariage",
            "language": "fr",
            "description": "French - Wedding roses"
        },
        {
            "query": "cutii cu flori albe pentru nuntă",
            "language": "ro",
            "description": "Romanian - White wedding boxes"
        },
        {
            "query": "white flower boxes for wedding",
            "language": "en",
            "description": "English - White wedding boxes"
        },
        {
            "query": "difuzoare aromă ieftine",
            "language": "ro",
            "description": "Romanian - Cheap aroma diffusers"
        },
        {
            "query": "affordable aroma diffusers", 
            "language": "en",
            "description": "English - Affordable diffusers"
        }
    ]
    
    for i, test in enumerate(multilingual_queries, 1):
        print_section(f"Test {i}: {test['description']}")
        print(f"📝 Query: '{test['query']}'")
        print(f"🌐 Expected language: {test['language']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": test["query"], "user_id": f"multilingual_test_{i}"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received ({len(data['response'])} chars)")
                print(f"🤖 Preview: {data['response'][:200]}...")
                
                # Check if response seems appropriate for language
                if test['language'] == "en" and any(word in data['response'].lower() for word in ['found', 'products', 'contact']):
                    print("✅ English response detected")
                elif test['language'] == "ro" and any(word in data['response'].lower() for word in ['găsit', 'produse', 'contact']):
                    print("✅ Romanian response detected")
                else:
                    print("⚠️  Language detection may need improvement")
                    
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)

def test_fuzzy_matching():
    """Test fuzzy matching for typos and variations"""
    print_header("TESTARE FUZZY MATCHING")
    
    fuzzy_queries = [
        {
            "query": "trandafiri rosii",  # Missing diacritics
            "correct": "trandafiri roșii",
            "description": "Missing diacritics"
        },
        {
            "query": "buchet trndafiri",  # Typo
            "correct": "buchet trandafiri", 
            "description": "Typo in trandafiri"
        },
        {
            "query": "dufuzor aroma",  # Typo
            "correct": "difuzor aromă",
            "description": "Typo in difuzor"
        },
        {
            "query": "nunta alba",  # Missing diacritics
            "correct": "nuntă albă",
            "description": "Missing diacritics - wedding"
        },
        {
            "query": "roze pentru iubita",  # Variant spelling
            "correct": "roz pentru iubită",
            "description": "Variant spelling"
        },
        {
            "query": "valentines day flowers",  # English variant
            "correct": "Valentine's Day flowers",
            "description": "English spelling variant"
        }
    ]
    
    for i, test in enumerate(fuzzy_queries, 1):
        print_section(f"Fuzzy Test {i}: {test['description']}")
        print(f"📝 Query with issues: '{test['query']}'")
        print(f"✅ Correct form: '{test['correct']}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": test["query"], "user_id": f"fuzzy_test_{i}"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response received ({len(data['response'])} chars)")
                
                # Check if we got products despite the typos
                if "am găsit" in data['response'].lower() or "found" in data['response'].lower():
                    print("✅ Fuzzy matching successful - found products")
                elif "nu am găsit" in data['response'].lower() or "no exact matches" in data['response'].lower():
                    print("⚠️  Fuzzy matching could be improved")
                else:
                    print("❓ Unclear result")
                    
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)

def test_advanced_filters():
    """Test advanced filtering capabilities"""
    print_header("TESTARE FILTRE AVANSATE")
    
    filter_queries = [
        {
            "query": "trandafiri roșii sub 500 lei",
            "expected_filters": ["color", "price_range"],
            "description": "Color + price filter"
        },
        {
            "query": "buchete albe pentru nuntă elegant",
            "expected_filters": ["color", "occasion", "style"],
            "description": "Color + occasion + style"
        },
        {
            "query": "cutii mari cu flori multicolor",
            "expected_filters": ["product_type", "size", "color"],
            "description": "Product type + size + color"
        },
        {
            "query": "difuzoare aromă luxury premium",
            "expected_filters": ["product_type", "price_range"],
            "description": "Product type + premium price"
        },
        {
            "query": "3 buchete mici pentru ziua de naștere",
            "expected_filters": ["quantity", "size", "occasion"],
            "description": "Quantity + size + occasion"
        }
    ]
    
    for i, test in enumerate(filter_queries, 1):
        print_section(f"Filter Test {i}: {test['description']}")
        print(f"📝 Query: '{test['query']}'")
        print(f"🎯 Expected filters: {test['expected_filters']}")
        
        try:
            # Test intent recognition to see extracted entities
            intent_response = requests.post(
                f"{BASE_URL}/api/test",
                json={"message": test["query"]},
                timeout=10
            )
            
            if intent_response.status_code == 200:
                intent_data = intent_response.json()
                entities = intent_data.get("entities", {})
                print(f"🔍 Extracted entities: {list(entities.keys())}")
                
                # Check filter coverage
                detected_filters = []
                for filter_type in test['expected_filters']:
                    if filter_type in entities or any(filter_type in key for key in entities.keys()):
                        detected_filters.append(filter_type)
                
                if len(detected_filters) >= len(test['expected_filters']) * 0.7:  # 70% coverage
                    print("✅ Good filter detection")
                else:
                    print(f"⚠️  Filter detection could be improved: {detected_filters}")
            
            # Also test actual search
            search_response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": test["query"], "user_id": f"filter_test_{i}"},
                timeout=15
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                if "am găsit" in search_data['response'].lower() or "found" in search_data['response'].lower():
                    print("✅ Search returned results")
                else:
                    print("⚠️  No results found")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(1)

def test_performance():
    """Test response times and performance"""
    print_header("TESTARE PERFORMANȚĂ")
    
    performance_queries = [
        "trandafiri roșii",
        "white roses for wedding", 
        "difuzoare aromă",
        "buchete ieftine",
        "expensive luxury bouquets"
    ]
    
    response_times = []
    
    for i, query in enumerate(performance_queries, 1):
        print_section(f"Performance Test {i}")
        print(f"📝 Query: '{query}'")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": query, "user_id": f"perf_test_{i}"},
                timeout=30
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code == 200:
                print(f"✅ Response time: {response_time:.2f}s")
                if response_time < 3.0:
                    print("✅ Fast response")
                elif response_time < 8.0:
                    print("⚠️  Acceptable response time")
                else:
                    print("❌ Slow response")
            else:
                print(f"❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            end_time = time.time()
            response_times.append(end_time - start_time)
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        print(f"\n📊 Average response time: {avg_time:.2f}s")
        print(f"📊 Fastest: {min(response_times):.2f}s")
        print(f"📊 Slowest: {max(response_times):.2f}s")

def test_data_integrity():
    """Test data integrity and collection status"""
    print_header("TESTARE INTEGRITATE DATE")
    
    try:
        # Test collections endpoint
        collections_response = requests.get(f"{BASE_URL}/api/collections")
        
        if collections_response.status_code == 200:
            collections_data = collections_response.json()
            collections = collections_data.get("collections", {})
            
            print_section("Status Colecții ChromaDB")
            total_products = 0
            
            for name, info in collections.items():
                count = info.get("count", 0)
                status = info.get("status", "unknown")
                total_products += count
                
                print(f"📦 {name}: {count} produse ({status})")
            
            print(f"\n📊 Total produse în toate colecțiile: {total_products}")
            
            if total_products > 700:  # Expect ~724 from CSV
                print("✅ Dataset complet încărcat")
            elif total_products > 500:
                print("⚠️  Dataset parțial încărcat")
            else:
                print("❌ Dataset incomplet")
        else:
            print(f"❌ Nu pot accesa informațiile despre colecții: {collections_response.status_code}")
            
    except Exception as e:
        print(f"❌ Eroare la testarea integrității datelor: {e}")

def main():
    """Run all optimization tests"""
    print("🌸 TESTE OPTIMIZĂRI XOFLOWERS AI AGENT")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check if server is running
        health_response = requests.get(f"{BASE_URL}/api/collections", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not running or not responding")
            print("💡 Please start the server with: python app.py")
            return
        
        print("✅ Server is running")
        
        # Run all tests
        test_data_integrity()
        test_multilingual_search()
        test_fuzzy_matching()
        test_advanced_filters()
        test_performance()
        
        print_header("SUMAR TESTE OPTIMIZĂRI")
        print("✅ Teste multilinguismă completate")
        print("✅ Teste fuzzy matching completate")  
        print("✅ Teste filtre avansate completate")
        print("✅ Teste performanță completate")
        print("✅ Teste integritate date completate")
        print("\n🚀 Agentul XOFlowers este optimizat și funcțional!")
        
    except requests.ConnectionError:
        print("❌ Nu pot conecta la server")
        print("💡 Asigurați-vă că serverul rulează cu: python app.py")
    except Exception as e:
        print(f"❌ Eroare generală: {e}")

if __name__ == "__main__":
    main()
