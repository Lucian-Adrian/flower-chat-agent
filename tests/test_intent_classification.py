"""
Test Intent Classification and Conversation Flow
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
load_dotenv()

from intelligence.conversation_manager import get_conversation_manager

async def test_intent_and_conversation():
    """
    Tests the conversation manager's ability to handle different inputs.
    """
    print("Testing Intent and Conversation Flow")

    if not os.getenv("OPENAI_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        print("Skipping test: No LLM API key found.")
        return

    manager = get_conversation_manager()
    
    test_cases = [
        "Salut, ce mai faci?",
        "Vreau un buchet de trandafiri roșii",
        "Cât costă livrarea?",
        "Ce program de lucru aveți?",
    ]

    for i, message in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: '{message}' ---")
        response = await manager.handle_message("test_user_intent", message)
        # Safely print the response
        try:
            print(f"Response: {response}")
        except UnicodeEncodeError:
            print(f"Response (encoded): {response.encode('utf-8')}")


if __name__ == "__main__":
    # Set console to UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    asyncio.run(test_intent_and_conversation())