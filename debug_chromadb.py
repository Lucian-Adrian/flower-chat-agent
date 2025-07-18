#!/usr/bin/env python3
"""
Debug ChromaDB Integration Test
Test specifically for ChromaDB integration and product search
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append('.')

async def test_chromadb_search():
    """Test ChromaDB product search specifically"""
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

async def test_ai_engine_flow():
    """Test the AI engine to see which flow it takes"""
    try:
        print("\n" + "="*60)
        print("🤖 Testing AI Engine Flow...")
        
        # Import AI engine
        from src.intelligence.ai_engine import process_message_ai
        
        # Test query for wedding bouquet
        test_message = "Este pentru mireasa, pana in 500 lei, vreau ceva frumos si ieftin, ce imi recomanzi?"
        test_user_id = "debug_user_456"
        
        print(f"📝 Test Query: {test_message}")
        print(f"👤 Test User: {test_user_id}")
        print("⏳ Processing...")
        
        # Process the message
        result = await process_message_ai(
            user_message=test_message,
            user_id=test_user_id
        )
        
        # Display results
        print(f"\n🎉 AI ENGINE FLOW RESULTS")
        print("="*60)
        print(f"✅ Success: {result.get('success', False)}")
        print(f"🔧 Service Used: {result.get('service_used', 'unknown')}")
        print(f"🎯 Intent Detected: {result.get('intent', 'unknown')}")
        print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"🛍️  Products Found: {len(result.get('products', []))}")
        
        print(f"\n💬 AI Response:")
        print("-" * 40)
        response = result.get('response', 'No response received')
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 40)
        
        # Check if ChromaDB was used
        if result.get('service_used') == 'gemini_chat':
            print("\n⚠️  ISSUE: Using Gemini Chat instead of ChromaDB search!")
            print("The system should be using ChromaDB for product searches.")
            return False
        elif len(result.get('products', [])) > 0:
            print("\n🎊 PERFECT: ChromaDB search working with products!")
            return True
        else:
            print("\n⚠️  ISSUE: No products found in response!")
            return False
            
    except Exception as e:
        print(f"\n❌ AI ENGINE FLOW TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔬 CHROMADB INTEGRATION DEBUG TEST")
    print("="*60)
    
    # Run tests
    chromadb_works = asyncio.run(test_chromadb_search())
    ai_flow_works = asyncio.run(test_ai_engine_flow())
    
    print(f"\n📊 TEST SUMMARY")
    print("="*60)
    print(f"🔍 ChromaDB Direct: {'✅ WORKING' if chromadb_works else '❌ FAILED'}")
    print(f"🤖 AI Engine Flow: {'✅ WORKING' if ai_flow_works else '❌ NEEDS FIX'}")
    
    if chromadb_works and not ai_flow_works:
        print(f"\n🎯 DIAGNOSIS: ChromaDB works, but AI Engine is bypassing it!")
        print("Need to fix AI Engine to use ChromaDB for product searches.")
    elif chromadb_works and ai_flow_works:
        print(f"\n🎉 SUCCESS: Both ChromaDB and AI integration working!")
    else:
        print(f"\n🔧 ISSUE: Need to fix ChromaDB integration.")
    
    print(f"\nDebug test completed.")
