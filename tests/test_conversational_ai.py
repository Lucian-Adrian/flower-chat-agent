#!/usr/bin/env python3
"""
Test script for the complete XOFlowers conversational AI system
"""

import sys
import os
import asyncio
import logging
from dotenv import load_dotenv

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_conversational_ai():
    """Test the complete conversational AI system"""
    
    print("Testing XOFlowers Conversational AI System")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("⚠️ Missing OPENAI_API_KEY or GEMINI_API_KEY environment variable.")
        print("   Skipping full conversation tests.")
        return

    try:
        from intelligence.conversation_manager import get_conversation_manager

        print("✅ ConversationManager imported successfully")
        
        conversation_manager = get_conversation_manager()
        
        print("✅ ConversationManager initialized successfully")
        
        test_scenarios = [
            {
                'user_id': 'test_user_1',
                'message': 'Salut! Cum merge?',
            },
            {
                'user_id': 'test_user_1',
                'message': 'Caut un buchet pentru ziua de naștere',
            },
            {
                'user_id': 'test_user_2',
                'message': 'Vreau flori romantice pentru iubita mea',
            },
            {
                'user_id': 'test_user_2',
                'message': 'Cât costă buchetele?',
            }
        ]
        
        print("\n🧪 Testing conversation scenarios:")
        print("-" * 40)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. Testing: '{scenario['message']}' for user {scenario['user_id']}")
            
            response = await conversation_manager.handle_message(
                user_id=scenario['user_id'],
                message_text=scenario['message']
            )
            
            try:
                print(f"   Response: {response}")
            except UnicodeEncodeError:
                print(f"   Response (encoded): {response.encode('utf-8')}")

        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    asyncio.run(test_conversational_ai())