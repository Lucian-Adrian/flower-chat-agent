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
    
    async def handle_message(self, user_id: str, message: str) -> str:
        """
        Process user message and return natural response (async version for Telegram bot)
        
        Args:
            user_id: Unique user identifier
            message: User's message
            
        Returns:
            Natural language response
        """
        # For now, just call the sync version
        # In the future, this can be enhanced with actual async AI calls
        return self.process_message_sync(user_id, message)
    
    def _generate_simple_response(self, message: str, conversation_context: Dict[str, Any]) -> str:
        """Generate a simple response without async AI calls for testing"""
        message_lower = message.lower()
        
        # Check if it's a product search - расширенный список ключевых слов
        search_keywords = [
            'caut', 'vreau', 'doresc', 'buchet', 'flori', 'trandafir', 'socia', 'mama', 
            'девушки', 'букет', 'хочу', 'купить', 'want', 'buy', 'flowers', 'bouquet',
            'розы', 'цветы', 'girlfriend', 'wife', 'мама', 'девушка'
        ]
        
        if any(word in message_lower for word in search_keywords):
            try:
                # Use ChromaDB search directly
                from src.database.chromadb_search_engine import search_products
                
                logger.info(f"🔍 Searching for: {message}")
                
                # Perform search
                search_results = search_products(message, limit=3)
                
                logger.info(f"📊 Search returned {len(search_results) if search_results else 0} results")
                
                if search_results and len(search_results) > 0:
                    response = "🌸 Am găsit câteva opțiuni frumoase pentru dumneavoastră:\n\n"
                    for i, result in enumerate(search_results, 1):
                        name = result.get('name', 'Produs necunoscut')
                        price = result.get('price', 'Preț la cerere')
                        category = result.get('category', '')
                        url = result.get('url', '')
                        
                        response += f"{i}. **{name}**\n"
                        response += f"   💰 Preț: {price} MDL\n"
                        
                        if category:
                            response += f"   📂 Categorie: {category}\n"
                        
                        if url:
                            response += f"   🔗 Vizualizați: {url}\n"
                        
                        response += "\n"
                    
                    response += "🌸 Ce părere aveți despre aceste opțiuni? Puteți să îmi spuneți mai multe despre preferințele dumneavoastră!"
                    return response
                else:
                    return "🌸 Îmi pare rău, nu am găsit produse care să corespundă exact cererii dumneavoastră. Puteți să îmi spuneți mai multe detalii despre ce căutați? De exemplu:\n\n• Culoarea preferată\n• Tipul de flori (trandafiri, bujori, etc.)\n• Ocazia (zi de naștere, aniversare, etc.)\n• Bugetul aproximativ\n\nCu aceste detalii vă pot ajuta mai bine! 😊"
                    
            except Exception as e:
                logger.error(f"❌ Error in product search: {e}")
                import traceback
                traceback.print_exc()
                return "🌸 Am întâmpinat o problemă tehnică cu căutarea. Vă rog să încercați din nou sau să mă contactați pentru asistență."
        
        # Handle greetings
        elif any(word in message_lower for word in ['salut', 'bună', 'hello', 'hi', 'привет', 'start']):
            return "🌸 Bună ziua! Bine ați venit la XOFlowers! 💐\n\nSunt asistentul dumneavoastră virtual și vă pot ajuta să găsiți florile perfecte pentru orice ocazie.\n\n**Cum vă pot ajuta astăzi?**\n• Căutați un buchet special?\n• Aveți o ocazie particulară?\n• Doriți recomandări?\n\nSpuneți-mi ce aveți în minte și vă voi ajuta cu plăcere! 😊"
        
        # Handle questions about what they offer
        elif any(word in message_lower for word in ['ce', 'cum', 'când', 'unde', 'de ce', 'что', 'спуне']):
            return "🌸 **La XOFlowers găsiți:**\n\n🌹 **Buchete clasice și premium**\n🇫🇷 **Trandafiri francezi**\n🌸 **Bujori și flori de sezon**\n🎉 **Buchete pentru ocazii speciale**\n📦 **Aranjamente în coșuri și cutii**\n🎁 **Accesorii și cadouri**\n\n**Prețuri:** de la 20 MDL la 3800 MDL\n**Livrare:** în Chișinău și împrejurimi\n\nSpuneți-mi ce căutați și vă voi ajuta să găsesc produsul perfect! 🌺"
        
        # Handle compliments
        elif any(word in message_lower for word in ['mulțumesc', 'frumos', 'minunat', 'perfect', 'спасибо', 'благодар']):
            return "🌸 Vă mulțumesc pentru cuvintele frumoase! Îmi face plăcere să vă ajut să găsiți florile perfecte. \n\n💐 Mai aveți nevoie de ceva? Poate:\n• Alte opțiuni de buchete?\n• Informații despre livrare?\n• Sfaturi pentru îngrijirea florilor?\n\nSunt aici pentru dumneavoastră! 😊"
        
        # Default response - encourage them to search
        else:
            return "🌸 **Înțeleg!** Sunt aici să vă ajut cu orice aveți nevoie legat de flori. \n\n**Pentru a vă ajuta mai bine, spuneți-mi:**\n\n🌺 Ce tip de flori căutați?\n🎉 Pentru ce ocazie sunt?\n💰 Aveți un buget anume?\n🎨 Culori preferate?\n👥 Pentru cine sunt florile?\n\n**Exemple:**\n• \"Caut trandafiri roșii pentru soția mea\"\n• \"Vreau un buchet sub 500 lei\"\n• \"Flori pentru ziua mamei\"\n\nCu cât mai multe detalii îmi oferiți, cu atât mai bine vă pot ajuta! 💪😊"
    
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