"""
Conversation Manager for XOFlowers Conversational AI
Central orchestrator that manages the entire conversation flow
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our components with relative imports
from .ai_conversation_engine import get_ai_engine
from .product_search import get_search_engine
from .conversation_context import get_context_manager
from .chromadb_manager import get_chromadb_manager


class ConversationManager:
    """
    Central conversation manager that orchestrates all components
    for natural, AI-driven conversations about flowers
    """
    
    def __init__(self):
        """Initialize conversation manager with all components"""
        self.ai_engine = get_ai_engine()
        self.search_engine = get_search_engine()
        self.context_manager = get_context_manager()
        self.chromadb_manager = get_chromadb_manager()
        
        logger.info("🎯 Conversation Manager initialized")
    
    def process_message_sync(self, user_id: str, message: str) -> str:
        """
        Process user message and return natural response (synchronous version)
        
        Args:
            user_id: Unique user identifier
            message: User's message
            
        Returns:
            Natural language response
        """
        try:
            logger.info(f"💬 Processing message from user {user_id}: '{message[:50]}...'")
            
            # Add user message to context
            self.context_manager.add_message(user_id, 'user', message)
            
            # Get conversation context
            conversation_context = self.context_manager.get_conversation_context(user_id)
            
            # Handle special cases first
            if self._is_greeting(message) and not conversation_context['is_returning_user']:
                response = self.context_manager.get_personalized_greeting(user_id)
                self.context_manager.add_message(user_id, 'assistant', response)
                return response
            
            # Simple response generation for now (without async AI calls)
            response = self._generate_simple_response(message, conversation_context)
            
            # Add response to context
            self.context_manager.add_message(user_id, 'assistant', response)
            
            logger.info(f"✅ Generated response for user {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return self._get_error_response()
    
    def _generate_simple_response(self, message: str, conversation_context: Dict[str, Any]) -> str:
        """Generate a simple response without async AI calls for testing"""
        message_lower = message.lower()
        
        # Check if it's a product search
        if any(word in message_lower for word in ['caut', 'vreau', 'doresc', 'buchet', 'flori', 'trandafir']):
            # Extract search intent and perform search
            search_intent = self.search_engine.extract_search_intent(message, conversation_context)
            search_results = self.search_engine.search_products(search_intent, n_results=3)
            
            if search_results:
                response = "🌸 Am găsit câteva opțiuni frumoase pentru dumneavoastră:\n\n"
                for i, result in enumerate(search_results, 1):
                    product = result.product
                    response += f"{i}. **{product['name']}** - {product['price']} MDL\n"
                    if product.get('colors'):
                        response += f"   Culori: {', '.join(product['colors'])}\n"
                    response += f"   {result.relevance_explanation}\n\n"
                
                response += "Ce părere aveți despre aceste opțiuni?"
                return response
            else:
                return "🌸 Îmi pare rău, nu am găsit produse care să corespundă exact cererii dumneavoastră. Puteți să îmi spuneți mai multe detalii despre ce căutați?"
        
        # Handle greetings
        elif any(word in message_lower for word in ['salut', 'bună', 'hello', 'hi']):
            return self.context_manager.get_personalized_greeting(conversation_context['user_id'])
        
        # Handle questions
        elif any(word in message_lower for word in ['ce', 'cum', 'când', 'unde', 'de ce']):
            return "🌸 Vă pot ajuta cu informații despre florile noastre! Suntem XOFlowers din Chișinău și oferim cele mai frumoase aranjamente florale. Cu ce anume vă pot ajuta?"
        
        # Handle compliments
        elif any(word in message_lower for word in ['mulțumesc', 'frumos', 'minunat', 'perfect']):
            return "🌸 Vă mulțumesc pentru cuvintele frumoase! Îmi face plăcere să vă ajut să găsiți florile perfecte. Mai aveți nevoie de ceva?"
        
        # Default response
        else:
            return "🌸 Înțeleg! Sunt aici să vă ajut cu orice aveți nevoie legat de flori. Căutați un buchet special, aveți întrebări despre produsele noastre, sau vă pot ajuta cu altceva?"
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greeting_words = [
            'salut', 'bună', 'hello', 'hi', 'hey', 
            'bună ziua', 'bună seara', 'bună dimineața'
        ]
        message_lower = message.lower()
        return any(greeting in message_lower for greeting in greeting_words)
    
    def _get_error_response(self) -> str:
        """Get error response when something goes wrong"""
        return "🌸 Îmi pare rău, am întâmpinat o problemă tehnică. Vă rog să încercați din nou sau să mă contactați pentru asistență."
    
    def get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get conversation context for user"""
        return self.context_manager.get_conversation_context(user_id)
    
    def get_personalized_greeting(self, user_id: str) -> str:
        """Get personalized greeting for user"""
        return self.context_manager.get_personalized_greeting(user_id)
    
    def cleanup_inactive_sessions(self):
        """Clean up inactive conversation sessions"""
        self.context_manager.cleanup_inactive_sessions()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get health status of all components"""
        return {
            'conversation_manager': 'healthy',
            'ai_engine': self.ai_engine.get_health_status(),
            'chromadb': self.chromadb_manager.health_check(),
            'context_manager': {
                'active_sessions': len(self.context_manager.active_sessions),
                'storage_path': self.context_manager.storage_path
            }
        }


# Global conversation manager instance
_conversation_manager = None

def get_conversation_manager() -> ConversationManager:
    """Get the global conversation manager instance"""
    global _conversation_manager
    if _conversation_manager is None:
        _conversation_manager = ConversationManager()
    return _conversation_manager


# Compatibility functions for existing code
def handle_conversation(message: str, user_id: str, context: Optional[Dict] = None) -> str:
    """
    Compatibility function for existing code
    
    Args:
        message: User's message
        user_id: User identifier
        context: Optional context (ignored, we use our own context management)
        
    Returns:
        Natural response
    """
    manager = get_conversation_manager()
    return manager.process_message_sync(user_id, message)