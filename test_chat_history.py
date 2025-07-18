#!/usr/bin/env python3
"""
Test Chat History Functionality
===============================

Test that the AI maintains conversation history
"""

import sys
import os
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

async def test_chat_history():
    """Test conversation history maintenance"""
    print("🧪 Testing Chat History Functionality")
    print("=" * 40)
    
    try:
        from src.intelligence.ai_engine import process_message_ai
        
        user_id = "chat_test_user"
        
        # Simulate the exact conversation from the user's example
        conversation = [
            "vreau un buchet pentru bunica mea, maine e ziua ei",
            "II plac florile clasice, as vrea sa fie cadoul pana in 700 lei, ce imi recomanzi",
            "tu ai uitat ca cadoul e pentru bunica mea?"
        ]
        
        responses = []
        
        for i, message in enumerate(conversation, 1):
            print(f"\n💬 Message {i}: '{message}'")
            
            try:
                result = await process_message_ai(
                    user_message=message,
                    user_id=user_id
                )
                
                response = result.get('response', '')
                responses.append(response)
                
                print(f"🤖 Response length: {len(response)} chars")
                print(f"📝 Preview: {response[:150]}...")
                
                # Check for specific indicators
                if i == 1:  # First message
                    if "bunica" in response.lower():
                        print("✅ Bot acknowledged grandmother context")
                    else:
                        print("⚠️  Bot may not have understood grandmother context")
                
                elif i == 3:  # Third message - checking memory
                    if "bunica" in response.lower() or "pentru bunica" in response.lower():
                        print("✅ Bot remembered it's for grandmother!")
                    else:
                        print("❌ Bot forgot it's for grandmother")
                        print(f"   Response: {response[:200]}...")
                
            except Exception as e:
                print(f"❌ Error processing message {i}: {e}")
                responses.append(None)
        
        print(f"\n" + "=" * 40)
        print("🎯 Chat History Test Complete!")
        
        # Summary
        if len(responses) == 3 and all(r for r in responses):
            if "bunica" in responses[2].lower():
                print("🎉 SUCCESS: Chat history working correctly!")
            else:
                print("⚠️  PARTIAL: Chat history may need improvement")
        else:
            print("❌ FAILED: Some messages failed to process")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_history())
