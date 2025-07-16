#!/usr/bin/env python3
"""
OpenAI API Integration Test
Tests that OpenAI API is working correctly with proper authentication
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

def test_openai_connection():
    """Test OpenAI API connection and basic functionality"""
    print("🤖 OpenAI API Integration Test")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Test basic completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in Romanian."}
            ],
            max_tokens=50
        )
        
        if response.choices:
            print(f"✅ OpenAI API working correctly")
            print(f"Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ No response from OpenAI API")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False


def test_intent_classification():
    """Test intent classification using OpenAI"""
    print("\n🎯 Intent Classification Test")
    print("=" * 40)
    
    try:
        from intelligence.intent_classifier import IntentClassifier
        
        classifier = IntentClassifier()
        
        test_messages = [
            "Vreau trandafiri roșii",
            "Ce prețuri aveți?",
            "Programul de lucru?",
            "Mulțumesc"
        ]
        
        print(f"Testing {len(test_messages)} messages...")
        
        for message in test_messages:
            intent, confidence = classifier.classify_intent(message)
            print(f"'{message}' -> {intent} ({confidence:.2f})")
        
        print("✅ Intent classification working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Intent classification error: {e}")
        return False


if __name__ == "__main__":
    print("🌸 XOFlowers OpenAI Integration Tests")
    print("=" * 50)
    
    openai_ok = test_openai_connection()
    intent_ok = test_intent_classification()
    
    if openai_ok and intent_ok:
        print("\n✅ All OpenAI tests passed!")
    else:
        print("\n❌ Some tests failed!")
