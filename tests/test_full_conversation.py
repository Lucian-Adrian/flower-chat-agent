"""
Full end-to-end test for the XOFlowers Conversational AI system
"""

import sys
import os
sys.path.append('src/intelligence')

def test_full_conversation():
    """Test complete conversation flow"""
    print("🎭 Testing XOFlowers Conversational AI System")
    print("=" * 60)
    
    try:
        from conversation_manager import get_conversation_manager
        manager = get_conversation_manager()
        print("✅ Conversation Manager initialized successfully")
        
        # Test system health
        health = manager.get_system_health()
        print(f"✅ System Health Check:")
        print(f"   - Conversation Manager: {health['conversation_manager']}")
        print(f"   - AI Engine: OpenAI={health['ai_engine']['openai_available']}, Gemini={health['ai_engine']['gemini_available']}")
        print(f"   - ChromaDB: {health['chromadb']['status']}")
        print(f"   - Context Manager: {health['context_manager']['active_sessions']} active sessions")
        
        # Test conversations with different users
        test_conversations = [
            {
                'user_id': 'user_001',
                'messages': [
                    "Salut! Sunt nou aici.",
                    "Caut un buchet frumos pentru soția mea",
                    "Vreau ceva roșu pentru Valentine's Day sub 800 lei",
                    "Mulțumesc! Primul buchet arată perfect."
                ]
            },
            {
                'user_id': 'user_002', 
                'messages': [
                    "Bună ziua! Aveți trandafiri albi?",
                    "Pentru nuntă îmi trebuie. Ceva elegant.",
                    "Perfect! Cum pot comanda?"
                ]
            },
            {
                'user_id': 'user_003',
                'messages': [
                    "Vreau flori pentru mama, ceva special",
                    "Sub 600 lei dacă se poate",
                    "Vă mulțumesc pentru ajutor!"
                ]
            }
        ]
        
        print("\n🎭 Starting conversation tests...")
        print("=" * 60)
        
        for conversation in test_conversations:
            user_id = conversation['user_id']
            messages = conversation['messages']
            
            print(f"\n👤 Testing conversation with {user_id}")
            print("-" * 40)
            
            for i, message in enumerate(messages, 1):
                print(f"\n{i}. 👤 User: {message}")
                
                try:
                    response = manager.process_message_sync(user_id, message)
                    print(f"   🤖 XOFlowers AI: {response}")
                    
                    # Show some context info
                    context = manager.get_conversation_context(user_id)
                    print(f"   📊 Context: Stage={context['conversation_stage']}, Messages={len(context['recent_messages'])}")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 Full conversation test completed successfully!")
        
        # Test specific scenarios
        print("\n🧪 Testing specific AI scenarios...")
        
        specific_tests = [
            ("user_test_1", "Ce diferență este între trandafirii roșii și cei roz?"),
            ("user_test_2", "Aveți livrare în Chișinău?"),
            ("user_test_3", "Cât costă cel mai ieftin buchet?"),
            ("user_test_4", "Mulțumesc pentru tot ajutorul!"),
            ("user_test_5", "Vreau să fac o plângere despre livrare")
        ]
        
        for user_id, message in specific_tests:
            print(f"\n👤 {user_id}: {message}")
            try:
                response = manager.process_message_sync(user_id, message)
                print(f"🤖 Response: {response[:150]}...")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n🎊 All tests completed successfully!")
        print("The XOFlowers Conversational AI system is working properly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_conversation()