"""
Intent Classifier for XOFlowers Conversational AI
This module is responsible for classifying the user's intent.
In the new system, this is part of the ConversationManager's
natural language understanding capabilities.
"""

import logging
from typing import Dict, Any

from .conversation_manager import get_conversation_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the global conversation manager
conversation_manager = get_conversation_manager()


class IntentClassifier:
    """
    A class to classify user intent. This is now a lightweight
    wrapper around the ConversationManager.
    """

    async def classify(self, user_id: str, message_text: str) -> Dict[str, Any]:
        """
        Classifies the intent of a user's message.

        Args:
            user_id: The unique identifier for the user.
            message_text: The text of the user's message.

        Returns:
            A dictionary containing the classified intent and any extracted entities.
        """
        logger.info(f"Classifying intent for user {user_id} using ConversationManager")

        # In the new architecture, the ConversationManager handles the full flow.
        # We can call the analysis step here for a more focused "classification",
        # but for simplicity, we'll just return a generic action that
        # triggers the main message handling pipeline.

        return {
            "action": "handle_message",
            "context": {
                "user_id": user_id,
                "message_text": message_text,
            },
        }
