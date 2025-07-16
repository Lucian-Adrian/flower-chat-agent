"""
Comprehensive test for the new XOFlowers Conversational AI system
Tests the complete flow from user message to natural response
"""

import sys
import os
import asyncio
sys.path.append('src/intelligence')

try:
    from conversation_manager import get_conversation_manager
    print("✅ Conversation Manager imported successfully")
    
    # Initialize the conversation manager
    manager = get_conversation_manager()
    print("✅ Conversation Manager initialized")
    
    # Test system health
    health = manager.get_system_health()
    print(f"✅ System Health: {health}")
    
    # Test conversations
    test_user_id = "test_user_123"
    
    test_conversations = [
        "Salut! Sunt nou aici.",
        "Caut un buchet frumos pentru soția mea",
        "Vreau ceva roșu pentru Valentine's Day",
        "Ce aveți sub 1000 de lei?",
        "Mulțumesc! Arată foarte frumos primul buchet."
    ]
    
    print("\n🎭 Starting conversation test...")
    print("=" * 60)
    
    for i, message in enumerate(test_conversations, 1):
        print(f"\n👤 User: {message}")
        
        try:
            # Process message
            response = manager.process_message_sync(test_user_id, message)
            print(f"🤖 XOFlowers AI: {response}")
            
            # Show conversation context
            context = manager.get_conversation_context(test_user_id)
            print(f"📊 Context: Stage={context['conversation_stage']}, Messages={len(context['recent_messages'])}")
            
        except Exception as e:
            print(f"❌ Error processing message {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Conversation test completed!")
    
    # Test specific scenarios
    print("\n🧪 Testing specific scenarios...")
    
    scenarios = [
        ("test_user_2", "Bună ziua! Vreau trandafiri albi pentru nuntă"),
        ("test_user_3", "Caut flori pentru mama, ceva elegant sub 800 lei"),
        ("test_user_4", "Ce diferență este între buchetul Passion și buchetul Romance?"),
        ("test_user_5", "Mulțumesc pentru ajutor! Sunteți foarte amabili!")
    ]
    
    for user_id, message in scenarios:
        print(f"\n👤 {user_id}: {message}")
        try:
            response = manager.process_message_sync(user_id, message)
            print(f"🤖 Response: {response[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎊 All tests completed successfully!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()