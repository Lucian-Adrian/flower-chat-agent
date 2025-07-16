"""
Action Handler for XOFlowers Conversational AI
This module is the entry point for handling user actions and messages,
connecting them to the new conversational AI system.
"""

import logging
from typing import Dict, Any

from .conversation_manager import get_conversation_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the global conversation manager
conversation_manager = get_conversation_manager()


async def handle_action(action: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles a specific action from the user.
    This function is now a bridge to the new ConversationManager.

    Args:
        action: The action to be performed (e.g., 'handle_message').
        context: The context of the action, containing user_id and message_text.

    Returns:
        A dictionary with the response for the user.
    """
    if action == "handle_message":
        user_id = context.get("user_id")
        message_text = context.get("message_text")

        if not user_id or not message_text:
            logger.error("❌ Missing user_id or message_text in context")
            return {"response": "A apărut o eroare internă."}

        logger.info(f"Handling message for user {user_id} via new ConversationManager")
        response_text = await conversation_manager.handle_message(user_id, message_text)

        return {"response": response_text}

    else:
        logger.warning(f"⚠️ Received unhandled action: {action}")
        return {"response": "Nu înțeleg această acțiune."}
