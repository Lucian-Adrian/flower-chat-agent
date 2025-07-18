#!/usr/bin/env python3
"""
Simple ChromaDB Test - No Security
Test just ChromaDB integration without security system
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append('.')

async def test_chromadb_only():
    """Test ChromaDB product search"""
    try:
        print("🔍 Testing ChromaDB Product Search...")
        
        # Test ChromaDB directly
        from src.data.chromadb_client import search_products
        
        # Test query for wedding bouquet under 500 MDL
        test_query = "buchet pentru mireasa nunta sub 500 lei"
        print(f"📝 Test Query: {test_query}")
        
        results = await search_products(test_query, max_results=5)
        
        print(f"\n🎉 CHROMADB SEARCH RESULTS")
        print("="*60)
        print(f"✅ Products Found: {len(results)}")
        
        for i, product in enumerate(results, 1):
            print(f"\n{i}. {product.get('name', 'Unknown')}")
            print(f"   💰 Price: {product.get('price', 'N/A')} MDL")
            print(f"   📋 Category: {product.get('category', 'N/A')}")
            score = product.get('score', 'N/A')
            if isinstance(score, (int, float)):
                print(f"   🎯 Score: {score:.3f}")
            else:
                print(f"   🎯 Score: {score}")
            
        return len(results) > 0
            
    except Exception as e:
        print(f"\n❌ CHROMADB TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_gemini_directly():
    """Test Gemini API directly"""
    try:
        print("\n🤖 Testing Gemini API Directly...")
        
        from google import genai
        
        # Initialize with our API key
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # Test message
        test_message = "Salut! Test message pentru Gemini."
        print(f"📝 Test Message: {test_message}")
        
        # Call Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=test_message
        )
        
        print(f"\n✅ Gemini Response:")
        print(f"'{response.text[:100]}...'")
        
        return True
        
    except Exception as e:
        print(f"\n❌ GEMINI TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 SIMPLE COMPONENT TESTS")
    print("="*60)
    
    # Run tests
    chromadb_works = asyncio.run(test_chromadb_only())
    gemini_works = asyncio.run(test_gemini_directly())
    
    print(f"\n📊 TEST SUMMARY")
    print("="*60)
    print(f"🔍 ChromaDB: {'✅ WORKING' if chromadb_works else '❌ FAILED'}")
    print(f"🤖 Gemini API: {'✅ WORKING' if gemini_works else '❌ FAILED'}")
    
    if chromadb_works and gemini_works:
        print(f"\n🎉 SUCCESS: Both components working!")
        print("Now we can integrate them properly in the AI engine.")
    else:
        print(f"\n🔧 ISSUE: Need to fix individual components first.")
    
    print(f"\nSimple test completed.")
