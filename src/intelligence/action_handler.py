"""
Enhanced Action Handler Module with Vector Search Integration
Handles different user actions with context awareness and personalization
"""

import os
import sys
from typing import Dict, List, Optional, Tuple

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

try:
    from settings import BUSINESS_INFO, RESPONSE_CONFIG
except ImportError:
    # Fallback settings if import fails
    BUSINESS_INFO = {"name": "XOFlowers", "phone": "+373 22 123 456"}
    RESPONSE_CONFIG = {"default_language": "ro"}

from .prompts import (
    ENHANCED_PRODUCT_SEARCH_PROMPT, ENHANCED_FAQ_RESPONSES, 
    ENHANCED_SUBSCRIPTION_PROMPT, ENHANCED_PAYMENT_SUCCESS_PROMPT, 
    ENHANCED_FALLBACK_PROMPT, ENHANCED_GREETING_RESPONSES,
    CONTEXT_AWARE_TEMPLATES, AI_ENHANCEMENT_TEMPLATES
)
from .intent_classifier import IntentClassifier
from .conversation_context import ConversationContext

# Import the new Universal Vector Search System
from ..database.vector_search import UniversalXOFlowersSearch


class ActionHandler:
    """
    Enhanced action handler with vector search integration
    """
    
    def __init__(self):
        """Initialize the enhanced action handler with vector search"""
        self.intent_classifier = IntentClassifier()
        self.vector_search = UniversalXOFlowersSearch()
        self.context_manager = ConversationContext()
        self.business_info = BUSINESS_INFO
        
        # Initialize the vector search system with our data
        self._initialize_vector_search()
        
    def _initialize_vector_search(self):
        """Initialize vector search with final_products_case_standardized.csv"""
        try:
            print("🚀 Initializing Vector Search System...")
            self.vector_search.load_products_from_csv("final_products_case_standardized.csv")
            print("✅ Vector Search System initialized successfully")
            
            # Get stats for verification
            stats = self.vector_search.get_stats()
            print(f"📊 Loaded {stats.get('total_products', 0)} products")
            print(f"🌸 Flower products: {stats.get('flower_products', 0)}")
            print(f"📂 Categories: {stats.get('categories_count', 0)}")
            
        except Exception as e:
            print(f"❌ Error initializing vector search: {e}")
            print("⚠️ Falling back to basic search functionality")
        
    def handle_message(self, message: str, user_id: str) -> Tuple[str, str, float]:
        """
        Main message handling with context awareness
        
        Args:
            message (str): User message
            user_id (str): User identifier
            
        Returns:
            Tuple[str, str, float]: (response, intent, confidence)
        """
        # Classify intent with context
        intent, confidence = self.intent_classifier.classify_intent(message, user_id)
        
        # Handle special cases
        if intent == "jailbreak":
            response = self._handle_jailbreak()
        else:
            # Route to appropriate handler
            response = self._route_to_handler(intent, message, user_id)
            
            # Personalize response based on context
            response = self._personalize_response(response, user_id, intent)
        
        # Update conversation context
        self.context_manager.add_turn(
            user_id=user_id,
            user_message=message,
            bot_response=response,
            intent=intent,
            confidence=confidence
        )
        
        return response, intent, confidence
    
    def _route_to_handler(self, intent: str, message: str, user_id: str) -> str:
        """Route message to appropriate handler"""
        handlers = {
            'find_product': lambda: self.handle_find_product(message, user_id),
            'ask_question': lambda: self.handle_ask_question(message, user_id),
            'subscribe': lambda: self.handle_subscribe(message, user_id),
            'pay_for_product': lambda: self.handle_pay_for_product(message, user_id),
            'greeting': lambda: self.handle_greeting(message, user_id),
            'order_status': lambda: self.handle_order_status(message),
            'complaint': lambda: self.handle_complaint(message),
            'recommendation': lambda: self.handle_recommendation(message),
            'availability': lambda: self.handle_availability(message),
            'delivery_info': lambda: self.handle_delivery_info(message),
            'cancel_order': lambda: self.handle_cancel_order(message),
            'price_inquiry': lambda: self.handle_price_inquiry(message),
            'seasonal_offers': lambda: self.handle_seasonal_offers(message),
            'gift_suggestions': lambda: self.handle_gift_suggestions(message),
            'care_instructions': lambda: self.handle_care_instructions(message),
            'bulk_orders': lambda: self.handle_bulk_orders(message),
            'farewell': lambda: self.handle_farewell(message),
            'fallback': lambda: self.handle_fallback(message)
        }
        
        handler = handlers.get(intent, handlers['fallback'])
        return handler()
    
    def _personalize_response(self, response: str, user_id: str, intent: str) -> str:
        """Personalize response based on user context"""
        user_profile = self.context_manager.get_user_profile(user_id)
        
        if user_profile:
            # Add personal touches based on profile
            if user_profile.name:
                response = response.replace("dumneavoastră", f"dumneavoastră, {user_profile.name}")
            
            # Add preferences if relevant
            if intent == "find_product" and user_profile.preferences:
                favorite_colors = user_profile.preferences.get("favorite_colors", [])
                if favorite_colors:
                    response += f"\n\n💫 *Știu că preferați {', '.join(favorite_colors)} - am inclus opțiuni în aceste nuanțe!*"
        
        return response
    
    def handle_greeting(self, message: str, user_id: str) -> str:
        """Handle greeting messages with personalization"""
        if self.context_manager.is_returning_user(user_id):
            user_profile = self.context_manager.get_user_profile(user_id)
            if user_profile and user_profile.conversation_count > 5:
                return ENHANCED_GREETING_RESPONSES["regular"]
            else:
                return ENHANCED_GREETING_RESPONSES["returning"]
        else:
            return ENHANCED_GREETING_RESPONSES["first_time"]
    
    def handle_find_product(self, message: str, user_id: str) -> str:
        """Handle product search requests using vector search"""
        try:
            # Extract search query from message
            query = self._extract_search_query(message)
            
            # Extract budget from message
            budget_amount = self._extract_budget_from_message(message)
            
            # Analyze the context and occasion
            occasion_context = self._analyze_occasion_context(message)
            
            # Get user preferences for personalized search
            user_profile = self.context_manager.get_user_profile(user_id)
            search_context = {}
            
            if user_profile:
                search_context = {
                    "favorite_products": user_profile.favorite_products,
                    "favorite_colors": user_profile.preferences.get("favorite_colors", []) if user_profile.preferences else [],
                    "budget_range": user_profile.budget_range,
                    "special_occasions": user_profile.special_occasions
                }
            
            # Perform smart search using vector search
            if budget_amount:
                print(f"💰 Searching with budget: {budget_amount} MDL")
                products = self.vector_search.smart_search(
                    query, 
                    limit=5, 
                    budget=budget_amount
                )
            else:
                print(f"🔍 Smart search for: '{query}'")
                products = self.vector_search.smart_search(query, limit=5)
            
            if products:
                # Generate contextual response
                contextual_response = self._generate_contextual_response(occasion_context, message)
                
                # Add budget-specific intro if budget was specified
                if budget_amount:
                    contextual_response += f"\n\n💰 *Am găsit opțiuni excelente în bugetul dumneavoastră de {budget_amount} MDL:*"
                
                # Format products for response with conversational tone
                formatted_products = self._format_products_conversationally(products, occasion_context)
                
                # Generate personalized advice
                personalized_advice = self._generate_personalized_advice(occasion_context, products)
                
                response = ENHANCED_PRODUCT_SEARCH_PROMPT.format(
                    contextual_response=contextual_response,
                    products=formatted_products,
                    personalized_advice=personalized_advice
                )
            else:
                # Get some popular products as fallback
                popular_products = self.vector_search.search_all_products("flori populare", limit=3)
                if popular_products:
                    contextual_response = self._generate_contextual_response("general", message)
                    formatted_popular = self._format_products_conversationally(popular_products, "general")
                    
                    response = f"""
{contextual_response}

Iată câteva sugestii frumoase din colecția noastră care s-ar putea să vă placă:

{formatted_popular}

💫 *Doriți să caut ceva specific sau să vă recomand pe baza preferințelor dumneavoastră?*
                    """
                else:
                    response = f"""
🌸 Înțeleg ce căutați, dar să verific mai bine opțiunile disponibile pentru dumneavoastră.

Vă rugăm să îmi spuneți mai multe despre:
• Ocazia specială
• Preferințele de culoare
• Bugetul aproximativ

📞 **Telefon:** +373 22 123 456
📧 **Email:** hello@xoflowers.md

💫 *Sunt aici să vă ajut să găsiți florile perfecte!*
                    """
            
            return response
            
        except Exception as e:
            print(f"❌ Error in handle_find_product: {e}")
            return self._fallback_product_response(message)
    
    def _fallback_product_response(self, message: str) -> str:
        """Fallback response when vector search fails"""
        return f"""
🌸 **Vă mulțumim pentru interesul în florile noastre!**

Din păcate, sistemul nostru de căutare întâmpină o problemă temporară. 

📞 **Vă rugăm să ne contactați direct:**
• Telefon: +373 22 123 456
• Email: hello@xoflowers.md
• Website: www.xoflowers.md

🌺 **Echipa noastră vă va ajuta să găsiți:**
• Buchete pentru orice ocazie
• Aranjamente personalizate
• Opțiuni în bugetul dumneavoastră

💫 *Îmi pare rău pentru inconvenient - vă garantez că veți fi mulțumit de serviciile noastre!*
        """
    
    def handle_ask_question(self, message: str, user_id: str = None) -> str:
        """Handle general questions about business"""
        message_lower = message.lower()
        
        # Check for specific FAQ topics
        if any(word in message_lower for word in ['program', 'orar', 'ore', 'deschis']):
            return ENHANCED_FAQ_RESPONSES["working_hours"]
        elif any(word in message_lower for word in ['livrare', 'transport', 'livrat']):
            return ENHANCED_FAQ_RESPONSES["delivery"]
        elif any(word in message_lower for word in ['unde', 'locație', 'adresă']):
            return ENHANCED_FAQ_RESPONSES["location"]
        elif any(word in message_lower for word in ['returnare', 'schimb', 'retur']):
            return ENHANCED_FAQ_RESPONSES["return_policy"]
        else:
            return """
🌸 **Informații XOFlowers:**

Pentru întrebări generale, vă rugăm să contactați echipa noastră:
📞 **Telefon:** +373 22 123 456
📧 **Email:** hello@xoflowers.md
🌐 **Website:** www.xoflowers.md

🌺 **Întrebări frecvente:**
• Program de lucru și orar
• Informații despre livrare
• Locația magazinului
• Politica de returnare

💫 *Cum vă pot ajuta mai exact?*
            """
    
    def handle_subscribe(self, message: str, user_id: str = None) -> str:
        """Handle subscription requests"""
        return ENHANCED_SUBSCRIPTION_PROMPT
    
    def handle_pay_for_product(self, message: str, user_id: str = None) -> str:
        """Handle payment requests"""
        return ENHANCED_PAYMENT_SUCCESS_PROMPT
    
    def handle_order_status(self, message: str) -> str:
        """Handle order status inquiries"""
        return """
📋 **Verificarea Comenzii XOFlowers:**

Pentru a verifica statusul comenzii dumneavoastră, vă rugăm să ne furnizați:
• Numărul comenzii
• Numărul de telefon folosit la comandă
• Data aproximativă a comenzii

📞 **Contact rapid:** +373 22 123 456
📧 **Email:** comenzi@xoflowers.md

🌸 *Sau spuneți-mi numărul comenzii și vă verific imediat statusul!*
        """
    
    def handle_complaint(self, message: str) -> str:
        """Handle complaints and issues"""
        return """
🌸 **Îmi pare foarte rău pentru problemă!**

*La XOFlowers, calitatea și satisfacția dumneavoastră sunt prioritatea noastră absolută.*

🛡️ **Rezolvăm imediat:**
📞 **Urgențe:** +373 22 123 456 (disponibil 24/7)
📧 **Email:** reclamatii@xoflowers.md
💬 **Chat direct:** Descrieți problema aici

✅ **Garanția noastră:**
• Înlocuire gratuită în 24 ore
• Rambursarea banilor 100%
• Compensație pentru inconvenient

🌺 *Vă rugăm să ne descrieți exact problema pentru a putea rezolva rapid!*
        """
    
    def handle_recommendation(self, message: str) -> str:
        """Handle recommendation requests using vector search"""
        try:
            # Get popular products from vector search
            popular_products = self.vector_search.search_all_products("flori populare premium", limit=3)
            
            if popular_products:
                formatted_products = self._format_vector_products(popular_products)
                return f"""
🌸 **Recomandări Experte XOFlowers:**

*Bazându-mă pe experiența noastră, iată sugestiile mele:*

{formatted_products}

🎁 **Pentru cadouri speciale:**
• Cutii premium cu flori și ciocolată
• Aranjamente de masă elegante
• Buchete personalizate

💫 *Pentru ce ocazie căutați? Vă pot da recomandări mai personalizate!*
                """
            else:
                # Fallback to static recommendations
                return """
🌸 **Recomandări Experte XOFlowers:**

*Bazându-mă pe experiența noastră, iată sugestiile mele:*

💐 **Cele mai populare:**
• **Buchet Romantic** - Trandafiri roșii clasici - 750 MDL
• **Buchet Pastel** - Mix delicat pentru orice ocazie - 600 MDL
• **Buchet Sezon** - Flori proaspete de sezon - 450 MDL

🎁 **Pentru cadouri:**
• **Cutie Premium** - Flori + ciocolată - 900 MDL
• **Aranjament Masă** - Perfect pentru acasă - 400 MDL

💫 *Pentru ce ocazie căutați? Vă pot da recomandări mai personalizate!*
                """
        except Exception as e:
            print(f"❌ Error in handle_recommendation: {e}")
            return self.handle_recommendation.__doc__.split('"""')[1]  # Fallback
    
    def handle_availability(self, message: str) -> str:
        """Handle availability inquiries"""
        return """
📋 **Verificarea Disponibilității XOFlowers:**

*Pentru a verifica disponibilitatea exactă:*

🌸 **Menționați produsul specific:**
• Tipul florilor (trandafiri, bujori, etc.)
• Culoarea dorită
• Mărimea aranjamentului

📞 **Verificare rapidă:** +373 22 123 456
🌺 **În general avem disponibile:**
• Trandafiri în toate culorile
• Bujori de sezon
• Flori mixte și arrangements

💫 *Ce anume verificați? Vă spun imediat!*
        """
    
    def handle_delivery_info(self, message: str) -> str:
        """Handle delivery information requests"""
        return ENHANCED_FAQ_RESPONSES["delivery"]
    
    def handle_cancel_order(self, message: str) -> str:
        """Handle order cancellation requests"""
        return """
🌸 **Anularea Comenzii XOFlowers:**

*Înțelegem că planurile se pot schimba!*

⚡ **Pentru anulare rapidă:**
📞 **Telefon:** +373 22 123 456
📧 **Email:** comenzi@xoflowers.md
💬 **Sau spuneți-mi numărul comenzii aici**

⏰ **Politica de anulare:**
• Gratuit cu 2 ore înainte de livrare
• Rambursare completă în 24 ore
• Serviciu disponibil 24/7

🌺 *Vă pot ajuta să modificați comanda în loc să o anulați complet?*
        """
    
    def handle_price_inquiry(self, message: str) -> str:
        """Handle price inquiries with vector search integration"""
        try:
            # Check if specific price range is mentioned
            budget = self._extract_budget_from_message(message)
            
            if budget:
                # Get products within budget
                products = self.vector_search.search_all_products("flori populare", limit=3, budget=budget)
                
                if products:
                    formatted_products = self._format_vector_products(products)
                    return f"""
💰 **Prețuri XOFlowers în bugetul dumneavoastră ({budget} MDL):**

{formatted_products}

🌹 **Categorii generale de preț:**
• Buchete mici (7-12 flori): 200-400 MDL
• Buchete medii (15-20 flori): 450-650 MDL
• Buchete mari (25+ flori): 700-1000 MDL

🚚 **Livrare:**
• Gratuită peste 500 MDL
• Standard: 100 MDL
• Express: 150 MDL

💫 *Vă pot ajuta să găsiți ceva specific în bugetul dumneavoastră!*
                    """
            
            # Default price response
            return """
💰 **Prețuri XOFlowers - Transparent și Competitiv:**

🌹 **Buchete Clasice:**
• Mici (7-12 flori): 200-400 MDL
• Medii (15-20 flori): 450-650 MDL
• Mari (25+ flori): 700-1000 MDL

🎁 **Aranjamente Speciale:**
• Cutii cadou: 500-1200 MDL
• Aranjamente masă: 300-600 MDL
• Coroane: 800-1500 MDL

🚚 **Livrare:**
• Gratuită peste 500 MDL
• Standard: 100 MDL
• Express: 150 MDL

💫 *Pentru preț exact, descrieți ce căutați!*
            """
            
        except Exception as e:
            print(f"❌ Error in handle_price_inquiry: {e}")
            return self.handle_price_inquiry.__doc__.split('"""')[1]  # Fallback
    
    def handle_seasonal_offers(self, message: str) -> str:
        """Handle seasonal offers and promotions"""
        return """
🎉 **Oferte Speciale XOFlowers:**

*Profitați de promoțiile noastre actuale!*

🌸 **Oferte curente:**
• **Reducere 20%** la buchete peste 500 MDL
• **Livrare gratuită** pentru comenzi peste 400 MDL
• **2+1 GRATIS** la aranjamente mici

🎁 **Pachete speciale:**
• **Romantic Package** - Buchete + ciocolată - 850 MDL (în loc de 1000)
• **Corporate Deal** - 5 aranjamente - 1500 MDL (în loc de 2000)

⏰ **Oferte limitate - valabile până la sfârșitul lunii!**

💫 *Care dintre oferte vă interesează?*
        """
    
    def handle_gift_suggestions(self, message: str) -> str:
        """Handle gift suggestions with vector search"""
        try:
            # Search for gift-appropriate products
            gift_products = self.vector_search.search_all_products("cadou elegant frumos", limit=4)
            
            if gift_products:
                formatted_products = self._format_vector_products(gift_products)
                return f"""
🎁 **Sugestii Cadou XOFlowers:**

*Să găsim cadoul perfect împreună!*

{formatted_products}

🎉 **Pentru ocazii speciale:**
• Aniversări: Buchete mari cu felicitare
• Valentine: Trandafiri roșii clasici
• Mama: Aranjamente delicate și calde

💫 *Pentru ce ocazie și pentru cine căutați cadou?*
                """
            else:
                # Fallback to static suggestions
                return """
🎁 **Sugestii Cadou XOFlowers:**

*Să găsim cadoul perfect împreună!*

👩 **Pentru EA:**
• Trandafiri roșii + ciocolată premium - 900 MDL
• Buchet pastel cu bujori - 650 MDL
• Aranjament în cutie elegantă - 750 MDL

👨 **Pentru EL:**
• Aranjament verde cu plante - 450 MDL
• Buchet simplu și elegant - 350 MDL
• Plante pentru birou - 250 MDL

🎉 **Pentru ocazii speciale:**
• Aniversări: Buchete mari cu felicitare
• Valentine: Trandafiri roșii clasici
• Mama: Aranjamente delicate și calde

💫 *Pentru ce ocazie și pentru cine căutați cadou?*
                """
        except Exception as e:
            print(f"❌ Error in handle_gift_suggestions: {e}")
            return self.handle_gift_suggestions.__doc__.split('"""')[1]  # Fallback
    
    def handle_care_instructions(self, message: str) -> str:
        """Handle flower care instructions"""
        return """
🌸 **Îngrijirea Florilor XOFlowers:**

*Păstrați frumusețea florilor mai mult timp!*

💧 **Reguli de bază:**
• Schimbați apa la 2-3 zile
• Tăiați tulpinile la 45° sub jet de apă
• Îndepărtați frunzele de sub linia apei
• Poziționați departe de surse de căldură

🌺 **Pentru trandafiri:**
• Apă călduță inițial, apoi rece
• Tăiați 2-3 cm din tulpină zilnic
• Adăugați o aspirină în apă

🌻 **Pentru flori mixte:**
• Fiecare tip poate avea nevoi diferite
• Consultați ghidul nostru complet online

💫 *Pentru ce tip de flori aveți nevoie de sfaturi specifice?*
        """
    
    def handle_bulk_orders(self, message: str) -> str:
        """Handle bulk order requests"""
        return """
🏢 **Comenzi Corporate XOFlowers:**

*Servicii profesionale pentru afaceri și evenimente!*

🎭 **Specializăm în:**
• Decorațiuni evenimente corporate
• Aranjamente pentru hoteluri/restaurante
• Buchete pentru delegații și parteneri
• Aranjamente pentru conferințe

💼 **Avantaje corporate:**
• Prețuri speciale pentru cantități mari
• Factură cu TVA
• Livrare programată
• Servicii de mentenanță

📞 **Contact dedicat:**
• Manager corporate: +373 22 123 457
• Email: corporate@xoflowers.md
• Consultare gratuită

💫 *Pentru câte persoane/locații planificați?*
        """
    
    def handle_farewell(self, message: str) -> str:
        """Handle farewell messages"""
        return """
🌸 **Vă mulțumim că ați ales XOFlowers!**

*Sperăm că v-am fost de ajutor și că veți fi mulțumit de serviciile noastre!*

🌺 **Rămâneți în legătură:**
📞 Pentru comenzi: +373 22 123 456
📧 Email: hello@xoflowers.md
🌐 Website: www.xoflowers.md

💐 **Să aveți o zi frumoasă plină de flori!**
✨ *Așteptăm să vă servim din nou cu plăcere!*
        """
    
    def handle_fallback(self, message: str) -> str:
        """Handle unrecognized messages"""
        return ENHANCED_FALLBACK_PROMPT
    
    def _handle_jailbreak(self) -> str:
        """Handle jailbreak attempts"""
        return """
🌸 **Sunt aici exclusiv pentru XOFlowers!**

*Mă concentrez pe florile noastre frumoase și serviciile premium.*

💐 **Cum vă pot ajuta cu:**
• Căutarea florilor perfecte
• Informații despre servicii
• Procesarea comenzilor
• Răspunsuri la întrebări

✨ *Să revenim la florile noastre superbe - ce vă interesează?*
        """
    
    def _extract_search_query(self, message: str) -> str:
        """Extract search query from user message"""
        # Remove common Romanian words that don't help with search
        stop_words = ['vreau', 'caut', 'arată', 'mi', 'pentru', 'să', 'cu', 'la', 'de', 'în', 'pe', 'care', 'sunt', 'este', 'am', 'ai', 'au']
        
        words = message.lower().split()
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return ' '.join(filtered_words) if filtered_words else message.lower()
    
    def _extract_budget_from_message(self, message: str) -> Optional[int]:
        """Extract budget amount from user message"""
        import re
        
        # Look for budget patterns in Romanian
        budget_patterns = [
            r'până la (\d+)\s*(?:lei|mdl|md)',
            r'buget(?:ul)?\s*(?:de|până la)?\s*(\d+)\s*(?:lei|mdl|md)',
            r'maxim\s*(\d+)\s*(?:lei|mdl|md)',
            r'sub\s*(\d+)\s*(?:lei|mdl|md)',
            r'mai ieftin de\s*(\d+)\s*(?:lei|mdl|md)',
            r'(\d+)\s*(?:lei|mdl|md)\s*maxim',
            r'(\d+)\s*(?:lei|mdl|md)\s*budget',
            r'cu\s*(\d+)\s*(?:lei|mdl|md)',
        ]
        
        message_lower = message.lower()
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None

    def _analyze_occasion_context(self, message: str) -> str:
        """Analyze the occasion context from the message"""
        message_lower = message.lower()
        
        # Check for specific occasions
        if any(word in message_lower for word in ['aniversar', 'ziua', 'birthday', 'sărbător']):
            return "birthday"
        elif any(word in message_lower for word in ['nuntă', 'căsător', 'wedding', 'mireasă']):
            return "wedding"
        elif any(word in message_lower for word in ['valentine', 'dragoste', 'iubire', 'romantic']):
            return "romantic"
        elif any(word in message_lower for word in ['mamă', 'mama', 'mother', '8 martie']):
            return "mother"
        elif any(word in message_lower for word in ['înmormântare', 'condoleanțe', 'funeral', 'coroană']):
            return "funeral"
        elif any(word in message_lower for word in ['felicitări', 'congratulations', 'succes', 'promovare']):
            return "congratulations"
        elif any(word in message_lower for word in ['scuze', 'iertare', 'sorry', 'apologize']):
            return "apology"
        else:
            return "general"
    
    def _generate_contextual_response(self, occasion_context: str, message: str) -> str:
        """Generate contextual response based on occasion"""
        contextual_responses = {
            "birthday": "🎉 Pentru o zi de naștere specială! Am găsit cele mai frumoase buchete care vor face această zi de neuitat:",
            "wedding": "👰 Pentru ziua cea mare! Iată aranjamentele noastre elegante perfecte pentru nuntă:",
            "romantic": "💕 Pentru momentele romantice! Am selectat cele mai frumoase flori pentru a-ți exprima dragostea:",
            "mother": "🌸 Pentru cea mai dragă mamă! Iată florile perfecte pentru a-i arăta cât de mult o iubești:",
            "funeral": "🕊️ Pentru momentele de reculegere. Aranjamentele noastre sunt create cu respect și empatie:",
            "congratulations": "🎊 Pentru a celebra succesul! Am ales cele mai potrivite flori pentru felicitări:",
            "apology": "🌹 Pentru a cere iertare cu sinceritate. Florile pot spune ceea ce cuvintele nu pot:",
            "general": "🌸 Am găsit câteva opțiuni frumoase pentru dumneavoastră:"
        }
        
        return contextual_responses.get(occasion_context, contextual_responses["general"])
    
    def _format_products_conversationally(self, products: List[Dict], occasion_context: str) -> str:
        """Format products with conversational tone based on occasion"""
        if not products:
            return "Din păcate, nu am găsit produse potrivite în acest moment."
        
        formatted = []
        for i, product in enumerate(products[:5], 1):
            name = product.get('name', 'Produs special')
            price = product.get('price', 'Preț la cerere')
            
            # Create occasion-specific descriptions
            if occasion_context == "birthday":
                emoji = "🎂"
                tone = "Perfect pentru sărbătorirea zilei speciale!"
            elif occasion_context == "wedding":
                emoji = "👰"
                tone = "Ideal pentru ziua nunții!"
            elif occasion_context == "romantic":
                emoji = "💕"
                tone = "Pentru momentele romantice!"
            elif occasion_context == "mother":
                emoji = "🌸"
                tone = "Perfecte pentru mama dragă!"
            elif occasion_context == "funeral":
                emoji = "🕊️"
                tone = "Cu respect și empatie."
            else:
                emoji = "🌺"
                tone = "Frumos și elegant!"
            
            # Handle price display
            if isinstance(price, (int, float)) and price > 0:
                price_display = f"{price} MDL"
            elif str(price).replace('.', '').isdigit():
                price_display = f"{price} MDL"
            else:
                price_display = "Preț la cerere"
            
            # Get additional product info
            category = product.get('category', '')
            flowers = product.get('flowers', '')
            source = product.get('source', '')
            
            description_parts = []
            if flowers:
                description_parts.append(f"🌺 {flowers}")
            if category:
                description_parts.append(f"📂 {category}")
            if source:
                description_parts.append(f"🔍 {source}")
            
            description = " • ".join(description_parts) if description_parts else "Aranjament floral elegant"
            
            formatted.append(f"""
{emoji} **{i}. {name}**
💰 {price_display}
📝 {description}
✨ *{tone}*
            """)
        
        return "\n".join(formatted)
    
    def _format_vector_products(self, products: List[Dict]) -> str:
        """Format products from vector search for display"""
        if not products:
            return "Nu am găsit produse disponibile."
        
        formatted = []
        for i, product in enumerate(products[:5], 1):
            name = product.get('name', 'Produs special')
            price = product.get('price', 0)
            category = product.get('category', '')
            flowers = product.get('flowers', '')
            score = product.get('score', 0)
            
            # Handle price display
            if isinstance(price, (int, float)) and price > 0:
                price_display = f"{price} MDL"
            else:
                price_display = "Preț la cerere"
            
            # Create description
            description_parts = []
            if flowers:
                description_parts.append(f"🌺 {flowers}")
            if category:
                description_parts.append(f"📂 {category}")
            if score > 0:
                description_parts.append(f"⭐ Relevanță: {score:.2f}")
            
            description = " • ".join(description_parts) if description_parts else "Aranjament floral elegant"
            
            formatted.append(f"""
🌸 **{i}. {name}**
💰 {price_display}
📝 {description}
            """)
        
        return "\n".join(formatted)
    
    def _generate_personalized_advice(self, occasion_context: str, products: List[Dict]) -> str:
        """Generate personalized advice based on occasion and products"""
        advice_templates = {
            "birthday": "🎉 *Sfat personal:* Pentru o zi de naștere, adăugați o felicitare personalizată și poate o cutie de ciocolată pentru a face cadoul complet!",
            "wedding": "👰 *Sfat personal:* Pentru nuntă, considerați să comandați în avans și să discutați cu noi despre decorațiunile sălii!",
            "romantic": "💕 *Sfat personal:* Pentru momente romantice, trandafirii roșii sunt întotdeauna o alegere sigură, dar nu uitați de preferințele ei!",
            "mother": "🌸 *Sfat personal:* Pentru mamă, florile cu parfum delicat și culorile calde sunt mereu apreciate!",
            "funeral": "🕊️ *Sfat personal:* Pentru condoleanțe, alegem întotdeauna culori sobri și aranjamente elegante, cu respect.",
            "congratulations": "🎊 *Sfat personal:* Pentru felicitări, culorile vii și aranjamentele mari fac o impresie excelentă!",
            "apology": "🌹 *Sfat personal:* Pentru a cere iertare, sinceritatea contează mai mult decât mărimea buchetului.",
            "general": "🌺 *Sfat personal:* Dacă nu sunteți sigur, sunați-ne și vă vom ajuta să alegeți perfect!"
        }
        
        base_advice = advice_templates.get(occasion_context, advice_templates["general"])
        
        # Add product-specific advice
        if products:
            total_products = len(products)
            if total_products > 3:
                base_advice += f"\n\n📞 *Avem {total_products} opțiuni disponibile - sunați pentru a discuta toate variantele!*"
        
        return base_advice
    
    def handle_action(self, intent: str, message: str, user_id: str) -> Dict:
        """
        Handle action with specific intent (backward compatibility method)
        
        Args:
            intent (str): Intent type
            message (str): User message
            user_id (str): User identifier
            
        Returns:
            Dict: Response dictionary with 'response' and 'action_type' keys
        """
        response = self._route_to_handler(intent, message, user_id)
        response = self._personalize_response(response, user_id, intent)
        
        # Update conversation context
        self.context_manager.add_turn(
            user_id=user_id,
            user_message=message,
            bot_response=response,
            intent=intent,
            confidence=0.8  # Default confidence for direct intent calls
        )
        
        return {
            'response': response,
            'action_type': intent
        }
    
    def get_vector_search_stats(self) -> Dict:
        """Get statistics from vector search system"""
        try:
            return self.vector_search.get_stats()
        except Exception as e:
            print(f"❌ Error getting vector search stats: {e}")
            return {"error": str(e)}
    
    def test_vector_search(self, query: str, limit: int = 3) -> List[Dict]:
        """Test vector search functionality"""
        try:
            return self.vector_search.smart_search(query, limit)
        except Exception as e:
            print(f"❌ Error testing vector search: {e}")
            return []
    
    def search_products_by_budget(self, budget: int, query: str = "flori frumoase", limit: int = 5) -> List[Dict]:
        """Search products within a specific budget"""
        try:
            return self.vector_search.smart_search(query, limit, budget=budget)
        except Exception as e:
            print(f"❌ Error searching by budget: {e}")
            return []