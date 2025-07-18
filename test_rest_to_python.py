#!/usr/bin/env python3
"""
Test script showing REST API to Python translation for Gemini API
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Method 1: Using google-genai library (RECOMMENDED)
def test_genai_library():
    """Test using the google-genai library"""
    try:
        from google import genai
        
        # Initialize client with API key
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Make the same request as your REST call
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite-preview-06-17",
            contents="Explain how AI works in a few words"
        )
        
        print("✅ Google GenAI Library Response:")
        print(response.text)
        return True
        
    except Exception as e:
        print(f"❌ Google GenAI Library Error: {e}")
        return False

# Method 2: Using requests library (direct REST translation)
def test_requests_library():
    """Test using requests library - direct REST translation"""
    try:
        import requests
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite-preview-06-17:generateContent"
        
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': os.getenv('GEMINI_API_KEY')
        }
        
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "Explain how AI works in a few words"
                        }
                    ]
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print("✅ Requests Library Response:")
        print(result['candidates'][0]['content']['parts'][0]['text'])
        return True
        
    except Exception as e:
        print(f"❌ Requests Library Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing REST to Python Translation\n")
    
    print("Method 1: Google GenAI Library")
    print("-" * 40)
    test_genai_library()
    
    print("\nMethod 2: Direct REST with Requests")
    print("-" * 40)
    test_requests_library()
