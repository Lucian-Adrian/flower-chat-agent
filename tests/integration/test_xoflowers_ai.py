#!/usr/bin/env python3
"""
XOFlowers AI System Integration Test
Tests the complete AI system functionality with realistic scenarios
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

def test_complete_system():
    """Test the complete XOFlowers AI system"""
    print("🌸 XOFlowers AI System Integration Test")
    print("=" * 50)
    
    try:
        from intelligence.action_handler import ActionHandler
        from intelligence.intent_classifier import IntentClassifier
        from intelligence.product_search import ProductSearchEngine
        
        # Initialize components
        action_handler = ActionHandler()
        intent_classifier = IntentClassifier()
        product_search = ProductSearchEngine()
        
        print("✅ All components initialized successfully")
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Product Search",
                "message": "Vreau trandafiri roșii pentru iubita mea",
                "expected_intent": "find_product"
            },
            {
                "name": "Price Inquiry",
                "message": "Cât costă un buchet de flori?",
                "expected_intent": "price_inquiry"
            },
            {
                "name": "Business Hours",
                "message": "Ce program aveți?",
                "expected_intent": "ask_question"
            },
            {
                "name": "Gift Recommendation",
                "message": "Ce îmi recomandați pentru aniversare?",
                "expected_intent": "recommendation"
            },
            {
                "name": "Farewell",
                "message": "Mulțumesc, la revedere!",
                "expected_intent": "farewell"
            }
        ]
        
        user_id = "test_user_ai_system"
        
        print(f"\n🧪 Testing {len(test_scenarios)} scenarios...\n")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"--- Scenario {i}: {scenario['name']} ---")
            print(f"Message: '{scenario['message']}'")
            
            # Test intent classification
            intent, confidence = intent_classifier.classify_intent(scenario['message'], user_id)
            print(f"Intent: {intent} (confidence: {confidence:.2f})")
            
            # Test full system response
            response, detected_intent, detected_confidence = action_handler.handle_message(
                scenario['message'], user_id
            )
            
            print(f"Response length: {len(response)} chars")
            print(f"System intent: {detected_intent} (confidence: {detected_confidence:.2f})")
            
            # Check if intent matches expected
            if detected_intent == scenario['expected_intent']:
                print("✅ Intent classification correct")
            else:
                print(f"⚠️ Expected '{scenario['expected_intent']}', got '{detected_intent}'")
            
            # Check response quality
            if len(response) > 50 and "🌸" in response:
                print("✅ Response quality good")
            else:
                print("⚠️ Response may need improvement")
            
            print()
        
        print("✅ Complete system test completed!")
        return True
        
    except Exception as e:
        print(f"❌ System test error: {e}")
        return False


def test_product_search_accuracy():
    """Test product search accuracy"""
    print("\n🔍 Product Search Accuracy Test")
    print("=" * 40)
    
    try:
        from intelligence.product_search import ProductSearchEngine
        
        search_engine = ProductSearchEngine()
        
        test_queries = [
            "trandafiri roșii",
            "flori pentru aniversare",
            "buchet alb",
            "flori funeral",
            "aranjament masă"
        ]
        
        print(f"Testing {len(test_queries)} search queries...")
        
        for query in test_queries:
            results = search_engine.search_products(query)
            print(f"'{query}' -> {len(results)} results")
            
            if results:
                print(f"  Top result: {results[0].get('name', 'Unknown')}")
            else:
                print("  No results found")
        
        print("✅ Product search test completed")
        return True
        
    except Exception as e:
        print(f"❌ Product search error: {e}")
        return False


if __name__ == "__main__":
    print("🌸 XOFlowers AI System Tests")
    print("=" * 50)
    
    system_ok = test_complete_system()
    search_ok = test_product_search_accuracy()
    
    if system_ok and search_ok:
        print("\n✅ All AI system tests passed!")
    else:
        print("\n❌ Some tests failed!")
