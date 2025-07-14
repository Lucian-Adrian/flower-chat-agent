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
            elif intent == "greeting":
                return self.handle_greeting(message)
            elif intent == "order_status":
                return self.handle_order_status(message)
            elif intent == "complaint":
                return self.handle_complaint(message)
            elif intent == "recommendation":
                return self.handle_recommendation(message)
            elif intent == "availability":
                return self.handle_availability(message)
            elif intent == "delivery_info":
                return self.handle_delivery_info(message)
            elif intent == "cancel_order":
                return self.handle_cancel_order(message)
            elif intent == "price_inquiry":
                return self.handle_price_inquiry(message)
            elif intent == "seasonal_offers":
                return self.handle_seasonal_offers(message)
            elif intent == "gift_suggestions":
                return self.handle_gift_suggestions(message)
            elif intent == "care_instructions":
                return self.handle_care_instructions(message)
            elif intent == "bulk_orders":
                return self.handle_bulk_orders(message)
            elif intent == "farewell":
                return self.handle_farewell(message)
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
    
    def handle_greeting(self, message: str) -> str:
        """Handle greeting messages"""
        return """🌸 Bună ziua! Bine ați venit la XOFlowers! 

Sunt aici să vă ajut cu:
• 🌹 Căutarea celor mai frumoase flori
• 💐 Recomandări personalizate
• 📦 Informații despre comenzi
• 🚚 Detalii despre livrare
• 📧 Abonamente și oferte speciale

Cum vă pot ajuta astăzi?"""

    def handle_order_status(self, message: str) -> str:
        """Handle order status inquiries"""
        return """📦 Pentru verificarea stării comenzii, vă rugăm să ne furnizați:

• Numărul comenzii
• Numele complet
• Numărul de telefon

Alternativ, ne puteți contacta direct:
📞 Telefon: [Your Phone Number]
📧 Email: [Your Email]

Vă mulțumim pentru încredere! 🌸"""

    def handle_complaint(self, message: str) -> str:
        """Handle complaints and feedback"""
        return """🙏 Ne pare foarte rău să aflăm că nu sunteți mulțumit!

Satisfacția clienților este prioritatea noastră.

Pentru a rezolva problema cât mai rapid:
📞 Sunați-ne direct: [Your Phone Number]
📧 Email: [Your Email]
💬 Descrieți situația în detaliu

Vă asigurăm că vom face tot posibilul să remediem situația!"""

    def handle_recommendation(self, message: str) -> str:
        """Handle recommendation requests"""
        return """🌟 Cu plăcere vă oferim recomandări personalizate!

Pentru a vă sugera cele mai potrivite flori, spuneți-ne:
• Pentru ce ocazie? (aniversare, Valentine, reconciliere, etc.)
• Care este bugetul dvs.? 
• Preferințe de culori?
• Stilul dorit? (elegant, modern, rustic, etc.)

Cele mai populare alegeri:
🌹 Buchet cu trandafiri roșii - clasic și romantic
🌷 Buchet mixt primăvăratec - colorat și fresh
🌺 Aranjament în cutie - elegant și durabil"""

    def handle_availability(self, message: str) -> str:
        """Handle availability inquiries"""
        return """📋 Pentru verificarea disponibilității produselor:

• Menționați produsul specific
• Cantitatea dorită
• Data necesară

Stocul se actualizează zilnic, iar produsele sezoniere pot varia.

Pentru verificare în timp real:
📞 Telefon: [Your Phone Number]
🌐 Website: [Your Website]

Vă recomandăm să comandați cu 24h înainte pentru siguranță! 🌸"""

    def handle_delivery_info(self, message: str) -> str:
        """Handle delivery information requests"""
        return """🚚 Informații despre livrare:

📍 **Zone de livrare:** Chișinău și suburbii
⏰ **Program livrări:** 09:00 - 18:00
💰 **Costuri:**
   • Gratuit pentru comenzi > 500 MDL
   • Standard: 100 MDL în Chișinău
   • Express (2-3 ore): 150 MDL

📅 **Timp de livrare:**
   • Standard: 4-6 ore
   • Express: 2-3 ore
   • Programată: la ora dorită

Pentru livrări urgente, vă rugăm să ne contactați direct! 📞"""

    def handle_cancel_order(self, message: str) -> str:
        """Handle order cancellation requests"""
        return """❌ Pentru anularea comenzii:

⏰ **Termene:**
   • Anulare gratuită: cu 2 ore înainte de livrare
   • Anulare tardivă: posibilă cu taxă 50% din valoare

📞 **Contactați-ne urgent:**
   • Telefon: [Your Phone Number]
   • Email: [Your Email]
   • Menționați numărul comenzii

💡 **Alternativă:** Puteți modifica comanda în loc să o anulați!"""

    def handle_price_inquiry(self, message: str) -> str:
        """Handle price inquiries"""
        return """💰 Prețuri XOFlowers:

🌹 **Buchete:**
   • Mici (7-12 flori): 200-400 MDL
   • Medii (15-25 flori): 450-750 MDL
   • Mari (30+ flori): 800-1500 MDL

📦 **Cutii cadou:**
   • Standard: 350-650 MDL
   • Premium: 700-1200 MDL
   • Luxury: 1300-2500 MDL

🪴 **Plante:**
   • Mici: 150-300 MDL
   • Medii: 350-600 MDL
   • Mari: 700-1500 MDL

Prețurile variază în funcție de sezon și disponibilitate."""

    def handle_seasonal_offers(self, message: str) -> str:
        """Handle seasonal offers and promotions"""
        return """🎉 Oferte speciale XOFlowers:

🌸 **Oferte curente:**
   • Reducere 20% la buchete > 500 MDL
   • Livrare gratuită în weekend
   • 2+1 gratis la plante mici

📅 **Oferte sezoniere:**
   • Valentine's Day: pachete speciale
   • 8 Martie: reduceri la toate produsele
   • Crăciun: decorațiuni festive

📧 **Abonați-vă la newsletter pentru:**
   • Oferte exclusive
   • Notificări preț redus
   • Primul acces la noutăți"""

    def handle_gift_suggestions(self, message: str) -> str:
        """Handle gift suggestions"""
        return """🎁 Sugestii cadou XOFlowers:

👩 **Pentru EA:**
   • Trandafiri roșii + ciocolată = romance
   • Flori mixte + prosecco = celebrare
   • Orhidee + parfum = eleganță

👨 **Pentru EL:**
   • Plante suculente = practic
   • Aranjament în cutie = stil
   • Flori pentru mama/soția = atenție

🎂 **Ocazii speciale:**
   • Aniversare: favorite + surprise
   • Reconciliere: trandafiri + scrisoare
   • Felicitări: colorat + vesel

Spuneți-ne mai multe pentru recomandări precise! 🌸"""

    def handle_care_instructions(self, message: str) -> str:
        """Handle care instructions for flowers"""
        return """🌱 Ghid îngrijire flori:

💐 **Flori tăiate:**
   • Schimbați apa la 2-3 zile
   • Tăiați tulpinile la 45° sub apă
   • Evitați soarele direct și curentul
   • Durabilitate: 5-10 zile

🪴 **Plante de interior:**
   • Udați când solul e uscat
   • Lumină indirectă
   • Umiditate moderată
   • Fertilizator lunar

🌹 **Trandafiri:**
   • Îndepărtați frunzele de jos
   • Apa călduță (nu rece)
   • Aspirină în apă = conservare
   • Tăiați capetele ofilite

Vă oferim și ghid detaliat la livrare! 📋"""

    def handle_bulk_orders(self, message: str) -> str:
        """Handle bulk order inquiries"""
        return """🏢 Comenzi corporate/cantități mari:

📊 **Servicii oferite:**
   • Decorațiuni evenimente
   • Aranjamente birou
   • Cadouri corporate
   • Nunți și botezuri

💰 **Avantaje:**
   • Reduceri progresive (10-25%)
   • Consultanță gratuită
   • Livrare programată
   • Facturare juridică

📞 **Contact specialized:**
   • Telefon direct: [Corporate Phone]
   • Email: [Corporate Email]
   • Programare consultanță

Solicităm detalii despre eveniment pentru ofertă personalizată! 🎊"""

    def handle_farewell(self, message: str) -> str:
        """Handle farewell messages"""
        return """🌸 Vă mulțumim că ați ales XOFlowers!

Sperăm că v-am fost de ajutor și că veți fi mulțumit de produsele noastre.

📞 Nu ezitați să ne contactați oricând:
   • Telefon: [Your Phone Number]
   • Email: [Your Email]
   • Website: [Your Website]

O zi frumoasă și mult succes! 🌺

La revedere! 👋"""
