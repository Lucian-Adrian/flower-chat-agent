#!/usr/bin/env python3
"""
Test the exact AI engine path with detailed logging
"""

import asyncio
import json
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('.')

async def test_ai_engine_path():
    """Test the AI engine path with detailed logging"""
    
    try:
        from src.intelligence.ai_engine import get_ai_engine
        
        ai_engine = get_ai_engine()
        test_message = "Aveți trandafiri roșii până în 1000 lei?"
        user_id = "debug_user"
        
        print("🔬 TESTING AI ENGINE PATH WITH DETAILED LOGGING")
        print("=" * 60)
        print(f"👤 Message: '{test_message}'")
        print(f"🆔 User ID: {user_id}")
        
        # Test the enhanced method directly
        from src.intelligence.ai_engine import get_ai_engine
        
        ai_engine = get_ai_engine()
        
        # Get context first
        from src.intelligence.gemini_chat_manager import get_enhanced_context_for_ai
        context = await get_enhanced_context_for_ai(user_id)
        print(f"\n📝 Context: {context}")
        
        # Test the enhanced method directly
        request_id = f"{user_id}_debug"
        
        print(f"\n🧠 Testing enhanced Gemini processing...")
        
        try:
            result = await ai_engine._enhanced_gemini_with_products(
                test_message, context, user_id, request_id
            )
            
            print(f"\n✅ Enhanced processing result:")
            print(f"  Success: {result.success}")
            print(f"  Intent: {result.intent}")
            print(f"  Products found: {result.products_found}")
            print(f"  Needs search: {result.needs_product_search}")
            print(f"  Service used: {result.service_used}")
            print(f"  Response length: {len(result.response_text)} chars")
            
            if result.products:
                print(f"\n🛍️ Products returned:")
                for i, product in enumerate(result.products, 1):
                    name = product.get('name', 'N/A')
                    price = product.get('price', 'N/A')
                    print(f"    {i}. {name} - {price} MDL")
            else:
                print(f"\n⚠️ No products in result")
            
            print(f"\n💬 Response preview:")
            print(f"'{result.response_text[:300]}...'")
            
        except Exception as e:
            print(f"❌ Enhanced processing failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_engine_path())
