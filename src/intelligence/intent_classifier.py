"""
Intent Classification Module
Handles intent recognition and classification for user messages
"""

import os
import sys
import re
from typing import Dict, List, Optional

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

from settings import INTENTS, AI_MODEL
from .prompts import INTENT_RECOGNITION_PROMPT, JAILBREAK_RESPONSE

# Import AI libraries
try:
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')
except ImportError:
    openai = None

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
except ImportError:
    genai = None


class IntentClassifier:
    """
    Classifies user intents using AI models with enhanced intent types
    """
    
    def __init__(self):
        """Initialize the intent classifier"""
        self.intents = {
            # Core intents
            'find_product': ['vreau', 'caut', 'arată', 'flori', 'buchet', 'cutie', 'cadou', 'plante'],
            'ask_question': ['ce', 'cum', 'când', 'unde', 'program', 'orar', 'locație', 'contact'],
            'subscribe': ['abonez', 'newsletter', 'actualizări', 'notificări', 'planuri'],
            'pay_for_product': ['plată', 'plătesc', 'card', 'comanda', 'cumpăr', 'finalizez'],
            
            # Additional intents
            'greeting': ['bună', 'salut', 'hello', 'hey', 'noroc', 'servus'],
            'order_status': ['comandă', 'status', 'starea', 'verifică', 'livrat'],
            'complaint': ['reclamație', 'problemă', 'nemulțumit', 'calitate', 'rău'],
            'recommendation': ['recomandă', 'sugerează', 'cea mai bună', 'popular'],
            'availability': ['disponibil', 'stoc', 'există', 'aveți'],
            'delivery_info': ['livrare', 'transport', 'când ajunge', 'cost livrare'],
            'cancel_order': ['anulat', 'renunt', 'să nu mai'],
            'price_inquiry': ['preț', 'cost', 'cât costă', 'tarif'],
            'seasonal_offers': ['oferte', 'reduceri', 'promoții', 'special'],
            'gift_suggestions': ['cadou', 'aniversare', 'zi de naștere', 'valentine'],
            'care_instructions': ['îngrijire', 'cum să păstrez', 'conservare', 'durabilitate'],
            'bulk_orders': ['cantitate mare', 'corporate', 'firmă', 'eveniment'],
            'farewell': ['pa', 'la revedere', 'bye', 'mulțumesc']
        }
        self.ai_config = AI_MODEL
        
    def classify_intent(self, message: str) -> str:
        """
        Classify the intent of a user message using multiple approaches
        
        Args:
            message (str): User message to classify
            
        Returns:
            str: Classified intent
        """
        message_lower = message.lower()
        
        # Quick keyword-based classification for common cases
        keyword_intent = self._classify_by_keywords(message_lower)
        if keyword_intent:
            return keyword_intent
            
        # AI-based classification for complex cases
        if openai or genai:
            ai_intent = self._classify_by_ai(message)
            if ai_intent:
                return ai_intent
                
        # Fallback to default
        return "fallback"
    
    def _classify_by_keywords(self, message: str) -> Optional[str]:
        """
        Fast keyword-based intent classification
        
        Args:
            message (str): Lowercase message
            
        Returns:
            Optional[str]: Intent if found, None otherwise
        """
        # Score each intent based on keyword matches
        intent_scores = {}
        
        for intent, keywords in self.intents.items():
            score = 0
            for keyword in keywords:
                if keyword in message:
                    score += 1
            if score > 0:
                intent_scores[intent] = score
        
        # Return the intent with highest score
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return None
    
    def _classify_by_ai(self, message: str) -> Optional[str]:
        """
        AI-based intent classification using OpenAI or Gemini
        
        Args:
            message (str): User message
            
        Returns:
            Optional[str]: Intent if classified, None otherwise
        """
        try:
            # Try OpenAI first
            if openai and openai.api_key:
                return self._classify_with_openai(message)
            
            # Fallback to Gemini
            if genai:
                return self._classify_with_gemini(message)
                
        except Exception as e:
            print(f"❌ AI classification error: {e}")
            
        return None
    
    def _classify_with_openai(self, message: str) -> Optional[str]:
        """Classify using OpenAI"""
        prompt = f"""
        Analyze this Romanian message and classify the intent:
        
        Message: "{message}"
        
        Available intents:
        - find_product: Looking for flowers, bouquets, gifts
        - ask_question: General questions about business
        - subscribe: Want to subscribe to updates
        - pay_for_product: Want to pay/purchase
        - greeting: Greeting messages
        - order_status: Check order status
        - complaint: Complaints or issues
        - recommendation: Ask for recommendations
        - availability: Check product availability
        - delivery_info: Ask about delivery
        - cancel_order: Cancel an order
        - price_inquiry: Ask about prices
        - seasonal_offers: Ask about offers/promotions
        - gift_suggestions: Ask for gift ideas
        - care_instructions: Ask how to care for flowers
        - bulk_orders: Large quantity orders
        - farewell: Goodbye messages
        
        Respond with only the intent name.
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.1
        )
        
        intent = response.choices[0].message.content.strip()
        return intent if intent in self.intents else None
    
    def _classify_with_gemini(self, message: str) -> Optional[str]:
        """Classify using Google Gemini"""
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Classify this Romanian message into one of these intents:
        
        Message: "{message}"
        
        Intents: find_product, ask_question, subscribe, pay_for_product, greeting, order_status, complaint, recommendation, availability, delivery_info, cancel_order, price_inquiry, seasonal_offers, gift_suggestions, care_instructions, bulk_orders, farewell
        
        Respond with only the intent name.
        """
        
        response = model.generate_content(prompt)
        intent = response.text.strip()
        return intent if intent in self.intents else None
    
    def is_jailbreak_attempt(self, message: str) -> bool:
        """
        Check if message is a jailbreak attempt
        
        Args:
            message (str): User message to check
            
        Returns:
            bool: True if jailbreak attempt detected
        """
        jailbreak_patterns = [
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'you\s+are\s+now',
            r'pretend\s+to\s+be',
            r'act\s+as\s+if',
            r'sistem\s+prompt',
            r'uită\s+tot',
            r'instrucțiuni\s+anterioare'
        ]
        
        message_lower = message.lower()
        for pattern in jailbreak_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
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
