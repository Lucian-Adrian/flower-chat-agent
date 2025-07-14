"""
Action Handler Module
Handles different user actions based on classified intents
"""

import os
import sys
from typing import Dict, List, Optional

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from settings import BUSINESS_INFO, RESPONSE_CONFIG
from .prompts import (
    PRODUCT_SEARCH_PROMPT, FAQ_RESPONSES, SUBSCRIPTION_PROMPT, 
    PAYMENT_SUCCESS_PROMPT, FALLBACK_PROMPT
)
from .intent_classifier import IntentClassifier
from .product_search import ProductSearchEngine


class ActionHandler:
    """
    Handles different user actions based on classified intents
    """
    
    def __init__(self):
        """Initialize the action handler"""
        self.intent_classifier = IntentClassifier()
        self.product_search = ProductSearchEngine()
        self.business_info = BUSINESS_INFO
        
    def handle_find_product(self, message: str) -> str:
        """
        Handle product search requests
        
        Args:
            message (str): User message
            
        Returns:
            str: Response message
        """
        # Extract search query from message
        query = self._extract_search_query(message)
        
        # Search for products
        products = self.product_search.search_products(query)
        
        if products:
            # Format products for response
            formatted_products = self._format_products(products)
            return PRODUCT_SEARCH_PROMPT.format(
                query=query,
                products=formatted_products
            )
        else:
            return "Îmi pare rău, nu am găsit produse care să corespundă cererii dumneavoastră. Încercați cu alți termeni de căutare."
    
    def handle_ask_question(self, message: str) -> str:
        """
        Handle general questions about the business
        
        Args:
            message (str): User message
            
        Returns:
            str: Response message
        """
        # TODO: Implement FAQ matching and AI-powered question answering
        return "Pentru întrebări generale, vă rugăm să contactați echipa noastră."
    
    def handle_subscribe(self, message: str) -> str:
        """
        Handle subscription requests
        
        Args:
            message (str): User message
            
        Returns:
            str: Response message
        """
        return SUBSCRIPTION_PROMPT
    
    def handle_pay_for_product(self, message: str) -> str:
        """
        Handle payment requests (simulation)
        
        Args:
            message (str): User message
            
        Returns:
            str: Response message
        """
        return PAYMENT_SUCCESS_PROMPT
    
    def handle_fallback(self, message: str) -> str:
        """
        Handle unrecognized intents
        
        Args:
            message (str): User message
            
        Returns:
            str: Response message
        """
        return FALLBACK_PROMPT
    
    def handle_action(self, intent: str, message: str) -> str:
        """
        Main handler that routes actions based on intent
        
        Args:
            intent (str): Classified intent
            message (str): User message
            
        Returns:
            str: Response message
        """
        try:
            if intent == "find_product":
                return self.handle_find_product(message)
            elif intent == "ask_question":
                return self.handle_ask_question(message)
            elif intent == "subscribe":
                return self.handle_subscribe(message)
            elif intent == "pay_for_product":
                return self.handle_pay_for_product(message)
            else:
                return self.handle_fallback(message)
        except Exception as e:
            return f"❌ A apărut o eroare: {str(e)}"
    
    def _extract_search_query(self, message: str) -> str:
        """
        Extract search query from user message
        
        Args:
            message (str): User message
            
        Returns:
            str: Extracted search query
        """
        # TODO: Implement intelligent query extraction
        return message.lower()
    
    def _format_products(self, products: List[Dict]) -> str:
        """
        Format products for display
        
        Args:
            products (List[Dict]): List of products
            
        Returns:
            str: Formatted product list
        """
        formatted = []
        for product in products[:RESPONSE_CONFIG['max_product_results']]:
            formatted.append(
                f"🌸 **{product['name']}**\n"
                f"💰 {product['price']}\n"
                f"📝 {product['description']}\n"
            )
        return "\n".join(formatted)
