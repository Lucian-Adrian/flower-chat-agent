#!/usr/bin/env python3
"""
Script de testare pentru XOFlowers Instagram AI Agent
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = "test_user_demo"

def test_chat_endpoint(message: str, user_id: str = TEST_USER_ID):
    """Test chat endpoint with a message"""
    
    url = f"{BASE_URL}/api/chat"
    payload = {
        "message": message,
        "user_id": user_id
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test passed")
            print(f"📤 Message: {message}")
            print(f"📥 Response: {data['response']}")
            print(f"⏰ Timestamp: {data['timestamp']}")
            print("-" * 50)
            return data
        else:
            print(f"❌ Test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return None

def test_products_endpoint():
    """Test products endpoint"""
    
    url = f"{BASE_URL}/api/products"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Products endpoint working")
            print(f"📦 Found {data['count']} products")
            print(f"🔍 Filters: {data['filters']}")
            
            if data['products']:
                print(f"📋 Sample product: {data['products'][0]['name']}")
            print("-" * 50)
            return data
        else:
            print(f"❌ Products test failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return None

def test_analytics_endpoint():
    """Test analytics endpoint"""
    
    url = f"{BASE_URL}/api/analytics"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics endpoint working")
            print(f"💬 Total conversations: {data['total_conversations']}")
            print(f"📊 Intent distribution: {len(data['intent_distribution'])} intents")
            print(f"📈 Recent activity: {len(data['recent_activity'])} days")
            print("-" * 50)
            return data
        else:
            print(f"❌ Analytics test failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return None

def test_home_endpoint():
    """Test home endpoint"""
    
    url = f"{BASE_URL}/"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Home endpoint working")
            print(f"🏠 Message: {data['message']}")
            print(f"🔢 Version: {data['version']}")
            print("-" * 50)
            return data
        else:
            print(f"❌ Home test failed: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return None

def run_comprehensive_tests():
    """Run comprehensive test suite"""
    
    print("🧪 Starting XOFlowers AI Agent Tests")
    print("=" * 50)
    
    # Test 1: Home endpoint
    print("🏠 Testing Home Endpoint...")
    test_home_endpoint()
    
    # Test 2: Basic chat functionality
    print("💬 Testing Chat Functionality...")
    
    test_messages = [
        "Salut!",
        "Vreau trandafiri roșii",
        "Aveți buchete pentru ziua de naștere?", 
        "Cât costă livrarea?",
        "Vreau un abonament lunar",
        "Cum pot plăti?",
        "Am o problemă cu comanda"
    ]
    
    for message in test_messages:
        test_chat_endpoint(message)
        time.sleep(1)  # Be nice to the server
    
    # Test 3: Products endpoint
    print("📦 Testing Products Endpoint...")
    test_products_endpoint()
    
    # Test 4: Analytics endpoint
    print("📊 Testing Analytics Endpoint...")
    test_analytics_endpoint()
    
    print("🎉 Test suite completed!")
    print("=" * 50)

def interactive_test():
    """Interactive testing mode"""
    
    print("🤖 XOFlowers AI Agent - Interactive Test Mode")
    print("Type 'quit' to exit, 'help' for commands")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print("Available commands:")
                print("- Type any message to chat with the AI")
                print("- 'products' - Test products endpoint")
                print("- 'analytics' - Test analytics endpoint")
                print("- 'quit' - Exit")
                continue
            
            elif user_input.lower() == 'products':
                test_products_endpoint()
                continue
            
            elif user_input.lower() == 'analytics':
                test_analytics_endpoint()
                continue
            
            elif user_input:
                result = test_chat_endpoint(user_input)
                if result:
                    print(f"Bot: {result['response']}")
                print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_comprehensive_tests()
        
        # Ask if user wants interactive mode
        response = input("\n🤖 Would you like to try interactive mode? (y/n): ")
        if response.lower() in ['y', 'yes']:
            print()
            interactive_test()
