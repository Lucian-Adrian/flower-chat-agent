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
    
    def _extract_budget(self, message: str) -> Optional[float]:
        """Extract budget from user message"""
        import re
        
        # Look for patterns like "до 1000", "под 500", "до 1000 лей", "under 500", etc.
        budget_patterns = [
            r'до\s*(\d+)',           # до 1000
            r'под\s*(\d+)',          # под 500  
            r'under\s*(\d+)',        # under 500
            r'sub\s*(\d+)',          # sub 500
            r'maximum\s*(\d+)',      # maximum 1000
            r'max\s*(\d+)',          # max 1000
            r'не\s*более\s*(\d+)',   # не более 1000
            r'максимум\s*(\d+)',     # максимум 1000
            r'nu\s*mai\s*mult\s*de\s*(\d+)', # nu mai mult de 1000
            r'максимально\s*(\d+)',  # максимально 1000
        ]
        
        message_lower = message.lower()
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    budget = float(match.group(1))
                    logger.info(f"💰 Extracted budget: {budget} MDL")
                    return budget
                except ValueError:
                    continue
        
        return None
    
    def _filter_by_budget(self, results: List[Dict], max_budget: float) -> List[Dict]:
        """Filter search results by budget"""
        if not results or not max_budget:
            return results
        
        filtered = []
        for result in results:
            price = result.get('price', 0)
            if isinstance(price, (int, float)) and price <= max_budget:
                filtered.append(result)
        
        logger.info(f"💰 Filtered {len(results)} → {len(filtered)} results within budget {max_budget} MDL")
        return filtered

    def _detect_language(self, message: str) -> str:
        """Detect user's language from message"""
        message_lower = message.lower()
        
        # Romanian indicators
        romanian_words = ['caut', 'vreau', 'doresc', 'buchet', 'flori', 'trandafir', 'bună', 'mulțumesc', 'când', 'unde', 'cum']
        romanian_count = sum(1 for word in romanian_words if word in message_lower)
        
        # Russian indicators  
        russian_words = ['хочу', 'нужны', 'букет', 'цветы', 'розы', 'привет', 'спасибо', 'где', 'когда', 'как']
        russian_count = sum(1 for word in russian_words if word in message_lower)
        
        # English indicators
        english_words = ['want', 'need', 'flowers', 'roses', 'bouquet', 'hello', 'thanks', 'where', 'when', 'how']
        english_count = sum(1 for word in english_words if word in message_lower)
        
        # Determine dominant language
        if russian_count > romanian_count and russian_count > english_count:
            return 'ru'
        elif english_count > romanian_count and english_count > russian_count:
            return 'en'
        else:
            return 'ro'  # Default to Romanian
    
    def _get_localized_responses(self, language: str) -> Dict[str, str]:
        """Get response templates for detected language"""
        templates = {
            'ro': {
                'greeting': "🌸 Bună ziua! Bine ați venit la XOFlowers! 💐\n\nSunt asistentul dumneavoastră virtual și vă pot ajuta să găsiți florile perfecte pentru orice ocazie.\n\n**Cum vă pot ajuta astăzi?**\n• Căutați un aranjament special?\n• Aveți o ocazie particulară?\n• Doriți recomandări?\n\nSpuneți-mi ce aveți în minte și vă voi ajuta cu plăcere! 😊",
                'catalog': "🌸 **La XOFlowers găsiți:**\n\n🌹 **Buchete clasice și premium**\n🇫🇷 **Trandafiri francezi**\n🌸 **Bujori și flori de sezon**\n🎉 **Buchete pentru ocazii speciale**\n📦 **Aranjamente în coșuri și cutii**\n🎁 **Accesorii și cadouri**\n\n**Prețuri:** de la 565 MDL la 8700 MDL\n**Livrare:** în Chișinău și împrejurimi\n\nSpuneți-mi ce căutați și vă voi ajuta să găsesc produsul perfect! 🌺",
                'thanks': "🌸 Vă mulțumesc pentru cuvintele frumoase! Îmi face plăcere să vă ajut să găsiți florile perfecte. \n\n💐 Mai aveți nevoie de ceva? Poate:\n• Alte opțiuni de buchete?\n• Informații despre livrare?\n• Sfaturi pentru îngrijirea florilor?\n\nSunt aici pentru dumneavoastră! 😊",
                'help': "🌸 **Înțeleg!** Sunt aici să vă ajut cu orice aveți nevoie legat de flori. \n\n**Pentru a vă ajuta mai bine, spuneți-mi:**\n\n🌺 Ce tip de flori căutați?\n🎉 Pentru ce ocazie sunt?\n💰 Aveți un buget anume?\n🎨 Culori preferate?\n👥 Pentru cine sunt florile?\n\n**Exemple:**\n• \"Caut trandafiri roșii pentru soția mea\"\n• \"Vreau un buchet sub 500 lei\"\n• \"Flori pentru ziua mamei\"\n\nCu cât mai multe detalii îmi oferiți, cu atât mai bine vă pot ajuta! 💪😊",
                'search_intro': "🌸 Am găsit câteva opțiuni frumoase pentru dumneavoastră:\n\n",
                'price': "💰 Preț: {price} MDL",
                'category': "📂 Categorie: {category}",
                'view': "🔗 Vizualizați: {url}",
                'within_budget': "🌸 Toate opțiunile sunt în bugetul dumneavoastră de până la {budget} MDL. ",
                'no_results': "🌸 Îmi pare rău, nu am găsit produse care să corespundă exact cererii dumneavoastră. Puteți să îmi spuneți mai multe detalii despre ce căutați?",
                'budget_exceeded': "🌸 Îmi pare rău, nu am găsit buchete în bugetul de până la {budget} MDL care să corespundă cererii dumneavoastră."
            },
            'ru': {
                'greeting': "🌸 Добро пожаловать в XOFlowers! 💐\n\nЯ ваш виртуальный помощник и помогу вам найти идеальные цветы для любого случая.\n\n**Чем могу помочь сегодня?**\n• Ищете особенный композицию?\n• Есть особый повод?\n• Нужны рекомендации?\n\nРасскажите, что у вас на уме, и я с удовольствием помогу! 😊",
                'catalog': "🌸 **В XOFlowers вы найдете:**\n\n🌹 **Классические и премиум букеты**\n🇫🇷 **Французские розы**\n🌸 **Пионы и сезонные цветы**\n🎉 **Букеты для особых случаев**\n📦 **Композиции в корзинах и коробках**\n🎁 **Аксессуары и подарки**\n\n**Цены:** от 565 MDL до 8700 MDL\n**Доставка:** в Кишиневе и пригороде\n\nСкажите, что ищете, и я помогу найти идеальный продукт! 🌺",
                'thanks': "🌸 Спасибо за добрые слова! Мне приятно помогать вам найти идеальные цветы. \n\n💐 Нужно что-то еще? Возможно:\n• Другие варианты букетов?\n• Информация о доставке?\n• Советы по уходу за цветами?\n\nЯ здесь для вас! 😊",
                'help': "🌸 **Понимаю!** Я здесь, чтобы помочь с любыми вопросами о цветах. \n\n**Чтобы лучше помочь, расскажите:**\n\n🌺 Какие цветы ищете?\n🎉 По какому поводу?\n💰 Есть ли бюджет?\n🎨 Предпочитаемые цвета?\n👥 Для кого цветы?\n\n**Примеры:**\n• \"Ищу красные розы для жены\"\n• \"Хочу композицию до 500 рублей\"\n• \"Цветы на день матери\"\n\nЧем больше деталей, тем лучше смогу помочь! 💪😊",
                'search_intro': "🌸 Нашел несколько красивых вариантов для вас:\n\n",
                'price': "💰 Цена: {price} MDL",
                'category': "📂 Категория: {category}",
                'view': "🔗 Посмотреть: {url}",
                'within_budget': "🌸 Все варианты в вашем бюджете до {budget} MDL. ",
                'no_results': "🌸 Извините, не нашел продуктов, точно соответствующих вашему запросу. Можете рассказать больше деталей о том, что ищете?",
                'budget_exceeded': "🌸 Извините, не нашел букетов в бюджете до {budget} MDL, соответствующих вашему запросу."
            },
            'en': {
                'greeting': "🌸 Welcome to XOFlowers! 💐\n\nI'm your virtual assistant and I can help you find perfect flowers for any occasion.\n\n**How can I help you today?**\n• Looking for a special arrangement?\n• Do you have a particular occasion?\n• Need recommendations?\n\nTell me what you have in mind and I'll be happy to help! 😊",
                'catalog': "🌸 **At XOFlowers you'll find:**\n\n🌹 **Classic and premium bouquets**\n🇫🇷 **French roses**\n🌸 **Peonies and seasonal flowers**\n🎉 **Bouquets for special occasions**\n📦 **Arrangements in baskets and boxes**\n🎁 **Accessories and gifts**\n\n**Prices:** from 565 MDL to 8700 MDL\n**Delivery:** in Chisinau and surroundings\n\nTell me what you're looking for and I'll help you find the perfect product! 🌺",
                'thanks': "🌸 Thank you for the kind words! I'm pleased to help you find the perfect flowers. \n\n💐 Need anything else? Perhaps:\n• Other bouquet options?\n• Delivery information?\n• Flower care tips?\n\nI'm here for you! 😊",
                'help': "🌸 **I understand!** I'm here to help with anything flower-related. \n\n**To help you better, tell me:**\n\n🌺 What type of flowers are you looking for?\n🎉 What's the occasion?\n💰 Do you have a budget?\n🎨 Preferred colors?\n👥 Who are the flowers for?\n\n**Examples:**\n• \"Looking for red roses for my wife\"\n• \"Want a bouquet under 500 lei\"\n• \"Flowers for Mother's Day\"\n\nThe more details you give me, the better I can help! 💪😊",
                'search_intro': "🌸 I found some beautiful options for you:\n\n",
                'price': "💰 Price: {price} MDL",
                'category': "📂 Category: {category}",
                'view': "🔗 View: {url}",
                'within_budget': "🌸 All options are within your budget of up to {budget} MDL. ",
                'no_results': "🌸 Sorry, I didn't find products that exactly match your request. Can you tell me more details about what you're looking for?",
                'budget_exceeded': "🌸 Sorry, I didn't find bouquets within the budget of up to {budget} MDL that match your request."
            }
        }
        return templates.get(language, templates['ro'])

    def _generate_simple_response(self, message: str, conversation_context: Dict[str, Any]) -> str:
        """Generate a simple response without async AI calls for testing"""
        message_lower = message.lower()
        
        # Detect user language
        user_language = self._detect_language(message)
        responses = self._get_localized_responses(user_language)
        
        # Check if it's a product search - расширенный список ключевых слов
        search_keywords = [
            'caut', 'vreau', 'doresc', 'buchet', 'flori', 'trandafir', 'socia', 'mama', 
            'девушки', 'букет', 'хочу', 'купить', 'want', 'buy', 'flowers', 'bouquet',
            'розы', 'цветы', 'цветок', 'роза', 'girlfriend', 'wife', 'мама', 'девушка', 'нужны', 'нужен',
            'roses', 'flower', 'trandafiri', 'red', 'красные', 'roșii'
        ]
        
        if any(word in message_lower for word in search_keywords):
            try:
                # Extract budget if mentioned
                budget = self._extract_budget(message)
                
                # Use ChromaDB search directly
                from src.database.chromadb_search_engine import search_products
                
                logger.info(f"🔍 Searching for: {message}")
                
                # Perform search
                search_results = search_products(message, limit=10)  # Get more results to filter
                
                # Filter by budget if specified
                if budget:
                    search_results = self._filter_by_budget(search_results, budget)
                    # Limit to top 3 after filtering
                    search_results = search_results[:3]
                else:
                    # If no budget, just take top 3
                    search_results = search_results[:3] if search_results else []
                
                logger.info(f"📊 Search returned {len(search_results) if search_results else 0} results")
                
                if search_results and len(search_results) > 0:
                    response = responses['search_intro']
                    for i, result in enumerate(search_results, 1):
                        name = result.get('name', 'Produs necunoscut')
                        price = result.get('price', 'Preț la cerere')
                        category = result.get('category', '')
                        url = result.get('url', '')
                        
                        response += f"{i}. **{name}**\n"
                        response += f"   {responses['price'].format(price=price)}\n"
                        
                        if category:
                            response += f"   {responses['category'].format(category=category)}\n"
                        
                        if url:
                            response += f"   {responses['view'].format(url=url)}\n"
                        
                        response += "\n"
                    
                    if budget:
                        response += responses['within_budget'].format(budget=budget)
                    
                    # Add natural closing based on language
                    if user_language == 'ru':
                        response += "Что думаете об этих вариантах? Расскажите больше о ваших предпочтениях!"
                    elif user_language == 'en':
                        response += "What do you think about these options? Tell me more about your preferences!"
                    else:
                        response += "Ce părere aveți despre aceste opțiuni? Puteți să îmi spuneți mai multe despre preferințele dumneavoastră!"
                    
                    return response
                else:
                    if budget:
                        return responses['budget_exceeded'].format(budget=budget) + "\n\n💡 **Sugestii:**\n• Încercați să măriți puțin bugetul\n• Căutați buchete mai simple sau cu flori de sezon\n• Contactați-ne direct pentru opțiuni personalizate\n\n📞 Putem să vă ajutăm să găsim ceva frumos în bugetul dumneavoastră!"
                    else:
                        base_response = responses['no_results']
                        if user_language == 'ru':
                            return base_response + " Например:\n\n• Предпочитаемый цвет\n• Тип цветов (розы, пионы и др.)\n• Повод (день рождения, годовщина и др.)\n• Примерный бюджет\n\nС этими деталями смогу лучше помочь! 😊"
                        elif user_language == 'en':
                            return base_response + " For example:\n\n• Preferred color\n• Type of flowers (roses, peonies, etc.)\n• Occasion (birthday, anniversary, etc.)\n• Approximate budget\n\nWith these details I can help you better! 😊"
                        else:
                            return base_response + " De exemplu:\n\n• Culoarea preferată\n• Tipul de flori (trandafiri, bujori, etc.)\n• Ocazia (zi de naștere, aniversare, etc.)\n• Bugetul aproximativ\n\nCu aceste detalii vă pot ajuta mai bine! 😊"
                    
            except Exception as e:
                logger.error(f"❌ Error in product search: {e}")
                import traceback
                traceback.print_exc()
                return "🌸 Am întâmpinat o problemă tehnică cu căutarea. Vă rog să încercați din nou sau să mă contactați pentru asistență."
        
        # Handle greetings
        elif any(word in message_lower for word in ['salut', 'bună', 'hello', 'hi', 'привет', 'start']):
            return responses['greeting']
        
        # Handle general info questions (about what they offer)
        elif any(word in message_lower for word in ['catalog', 'каталог', 'ce oferiti', 'what do you offer', 'что есть', 'що маєте']):
            return responses['catalog']
        
        # Handle simple questions without product intent
        elif any(word in message_lower for word in ['ce', 'cum', 'când', 'unde', 'de ce', 'что это', 'что', 'как дела', 'спуне']):
            return responses['help']
        
        # Handle compliments
        elif any(word in message_lower for word in ['mulțumesc', 'frumos', 'minunat', 'perfect', 'спасибо', 'благодар', 'thanks', 'thank']):
            return responses['thanks']
        
        # Default response - encourage them to search
        else:
            return responses['help']
    
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