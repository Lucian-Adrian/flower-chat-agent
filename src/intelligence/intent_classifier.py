"""
Intent Classification Module
Handles intent recognition and classification for user messages
"""

import os
import sys
from typing import Dict, List, Optional

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from settings import INTENTS, AI_MODEL
from .prompts import INTENT_RECOGNITION_PROMPT, JAILBREAK_RESPONSE


class IntentClassifier:
    """
    Classifies user intents using AI models
    """
    
    def __init__(self):
        """Initialize the intent classifier"""
        self.intents = INTENTS
        self.ai_config = AI_MODEL
        
    def classify_intent(self, message: str) -> str:
        """
        Classify the intent of a user message
        
        Args:
            message (str): User message to classify
            
        Returns:
            str: Classified intent (find_product, ask_question, subscribe, pay_for_product, fallback)
        """
        # TODO: Implement AI-based intent classification
        # For now, return a placeholder
        return "find_product"
    
    def is_jailbreak_attempt(self, message: str) -> bool:
        """
        Check if message is a jailbreak attempt
        
        Args:
            message (str): User message to check
            
        Returns:
            bool: True if jailbreak attempt detected
        """
        jailbreak_keywords = [
            "ignore previous instructions",
            "ignore all previous",
            "forget everything",
            "you are now",
            "new role"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in jailbreak_keywords)
    
    def get_intent_confidence(self, message: str) -> Dict[str, float]:
        """
        Get confidence scores for all intents
        
        Args:
            message (str): User message
            
        Returns:
            Dict[str, float]: Intent confidence scores
        """
        # TODO: Implement confidence scoring
        return {"find_product": 0.8, "ask_question": 0.2}
