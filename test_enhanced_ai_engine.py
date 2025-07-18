#!/usr/bin/env python3
"""
Test the Enhanced Gemini+ChromaDB AI Engine
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append('.')

async def test_enhanced_ai_engine():
    """Test the enhanced AI engine with various scenarios"""
    
    try:
        from src.intelligence.ai_engine import process_message_ai
        
        test_cases = [
            {
                "message": "Salut! Sunt nou aici.",
                "user_id": "test_user_1",
                "description": "Greeting test"
            },
            {
                "message": "Caut un buchet pentru o nuntă, vreau ceva elegant",
                "user_id": "test_user_2", 
                "description": "Product search test"
            },
            {
                "message": "Aveți trandafiri roșii până în 1000 lei?",
                "user_id": "test_user_3",
                "description": "Product search with price limit"
            },
            {
                "message": "Care e programul vostru?",
                "user_id": "test_user_4",
                "description": "Business info test"
            }
        ]
        
        print("🚀 TESTING ENHANCED GEMINI+CHROMADB AI ENGINE")
        print("=" * 60)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔬 TEST {i}/{len(test_cases)}: {test_case['description']}")
            print("-" * 50)
            print(f"👤 User: {test_case['message']}")
            
            try:
                # Call the enhanced AI engine
                result = await process_message_ai(
                    test_case['message'], 
                    test_case['user_id']
                )
                
                print(f"\n📊 RESULTS:")
                print(f"✅ Success: {result.get('success', False)}")
                print(f"🎯 Intent: {result.get('intent', 'N/A')}")
                print(f"🎯 Confidence: {result.get('confidence', 0):.2f}")
                print(f"🔍 Products Found: {result.get('products_found', 0)}")
                print(f"⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
                print(f"🔧 Service Used: {result.get('service_used', 'N/A')}")
                
                print(f"\n💬 Response:")
                response_text = result.get('response', 'No response')
                print(f"'{response_text[:300]}{'...' if len(response_text) > 300 else ''}'")
                
                if result.get('products_found', 0) > 0:
                    print(f"\n🛍️ Products context included in response")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎉 Enhanced AI Engine testing completed!")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_ai_engine())
