"""
Natural Response Generation System for XOFlowers AI Agent
Integrates FAQ data, product recommendations, and conversation context
to generate natural, contextual AI responses
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.utils.system_definitions import get_ai_prompts, get_service_config
from src.utils.utils import setup_logger, log_performance_metrics
from src.data.faq_manager import get_business_info_summary, search_faq, get_faq_responses
from src.data.chromadb_client import search_products, search_products_with_filters
from .product_recommender import get_product_recommendations, format_recommendations_for_ai
from .business_info_integrator import get_business_context, format_business_context_for_ai

logger = setup_logger(__name__)

@dataclass
class ResponseContext:
    """Context data for response generation"""
    user_message: str
    intent_data: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    products: List[Dict[str, Any]]
    business_info: Dict[str, Any]
    faq_match: Optional[Dict[str, str]]

class NaturalResponseGenerator:
    """
    Generates natural AI responses by integrating multiple data sources:
    - FAQ data and business information
    - Product search results from ChromaDB
    - Conversation context and user preferences
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.ai_prompts = get_ai_prompts()
        self.service_config = get_service_config()
        
        self.logger.info("Natural Response Generator initialized")
    
    async def generate_response(self, user_message: str, intent_data: Dict[str, Any], 
                              conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a natural response integrating all available data sources
        
        Args:
            user_message: User's message text
            intent_data: Intent analysis results
            conversation_context: Conversation history and preferences
            
        Returns:
            Dict containing response and metadata
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Step 1: Gather all relevant data
            response_context = await self._gather_response_context(
                user_message, intent_data, conversation_context
            )
            
            # Step 2: Generate contextual response
            response_text = await self._generate_contextual_response(response_context)
            
            # Step 3: Post-process and validate response
            final_response = self._post_process_response(response_text, response_context)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            self.logger.info(f"Response generated successfully in {processing_time:.2f}s")
            
            return {
                "response": final_response,
                "success": True,
                "products_included": len(response_context.products),
                "business_info_used": bool(response_context.business_info),
                "faq_match_found": response_context.faq_match is not None,
                "intent": intent_data.get('intent'),
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            self.logger.error(f"Error generating response: {e}")
            
            return {
                "response": self._get_error_fallback_response(),
                "success": False,
                "error": str(e),
                "processing_time": processing_time
            }
    
    async def _gather_response_context(self, user_message: str, intent_data: Dict[str, Any], 
                                     conversation_context: Dict[str, Any]) -> ResponseContext:
        """
        Gather all relevant context data for response generation
        """
        # Extract conversation data
        conversation_history = conversation_context.get('recent_messages', [])
        user_preferences = conversation_context.get('preferences', {})
        
        # Initialize context
        products = []
        business_info = {}
        faq_match = None
        
        # Gather product data if needed
        if intent_data.get('requires_product_search', False):
            products = await self._get_relevant_products(user_message, intent_data, user_preferences)
        
        # Gather business information using the intelligent integrator
        business_context = await get_business_context(user_message, intent_data)
        business_info = business_context.relevant_info
        faq_match = business_context.faq_matches[0] if business_context.faq_matches else None
        
        return ResponseContext(
            user_message=user_message,
            intent_data=intent_data,
            conversation_history=conversation_history,
            user_preferences=user_preferences,
            products=products,
            business_info=business_info,
            faq_match=faq_match
        )
    
    async def _get_relevant_products(self, user_message: str, intent_data: Dict[str, Any], 
                                   user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get intelligent product recommendations using the advanced recommendation system
        """
        try:
            # Use the new product recommender for intelligent recommendations
            recommendations = await get_product_recommendations(
                user_message, intent_data, user_preferences, max_recommendations=3
            )
            
            # Format recommendations for AI response generation
            formatted_recs = format_recommendations_for_ai(recommendations)
            
            # Convert recommendations back to product format for compatibility
            products = []
            if formatted_recs.get('has_recommendations'):
                for rec_data in formatted_recs['recommendations']:
                    # Find the original product from the recommendation
                    for rec in recommendations:
                        if rec.product.get('name') == rec_data['name']:
                            # Add recommendation metadata to product
                            product = rec.product.copy()
                            product['recommendation_reason'] = rec.recommendation_reason
                            product['relevance_score'] = rec.relevance_score
                            product['is_alternative'] = rec.alternative_to is not None
                            if rec.alternative_to:
                                product['alternative_to'] = rec.alternative_to
                            products.append(product)
                            break
            
            self.logger.debug(f"Generated {len(products)} intelligent product recommendations")
            return products
            
        except Exception as e:
            self.logger.error(f"Error getting intelligent product recommendations: {e}")
            # Fallback to basic search if recommendation system fails
            try:
                products = search_products(user_message, max_results=3)
                self.logger.debug(f"Fallback: Found {len(products)} products via basic search")
                return products
            except Exception as fallback_error:
                self.logger.error(f"Fallback search also failed: {fallback_error}")
                return []
    
    async def _get_relevant_business_info(self, user_message: str, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get relevant business information based on user query
        """
        try:
            # Get comprehensive business info
            business_info = get_business_info_summary()
            
            # Filter relevant information based on intent
            entities = intent_data.get('entities', {})
            message_lower = user_message.lower()
            
            relevant_info = {}
            
            # Check what specific info is requested
            if any(word in message_lower for word in ['orar', 'program', 'deschis', 'închis', 'ore']):
                relevant_info['working_hours'] = business_info['working_hours']
            
            if any(word in message_lower for word in ['contact', 'telefon', 'email', 'adresa', 'unde']):
                relevant_info['basic_info'] = business_info['basic_info']
            
            if any(word in message_lower for word in ['servicii', 'ce faceți', 'ce oferiți']):
                relevant_info['services'] = business_info['services']
            
            if any(word in message_lower for word in ['livrare', 'transport', 'cost']):
                relevant_info['delivery'] = business_info['delivery']
            
            if any(word in message_lower for word in ['plată', 'card', 'numerar', 'cum plătesc']):
                relevant_info['payment_methods'] = business_info['payment_methods']
            
            # If no specific info requested, return basic info
            if not relevant_info:
                relevant_info = {
                    'basic_info': business_info['basic_info'],
                    'working_hours': business_info['working_hours']
                }
            
            return relevant_info
            
        except Exception as e:
            self.logger.error(f"Error getting relevant business info: {e}")
            return {}
    
    async def _generate_contextual_response(self, context: ResponseContext) -> str:
        """
        Generate contextual response using AI with all gathered data
        """
        # Prepare enhanced prompt with all context data
        prompt = self._build_enhanced_prompt(context)
        
        # This will be handled by the AI engine's response generation
        # For now, return a structured prompt that the AI engine can use
        return prompt
    
    def _build_enhanced_prompt(self, context: ResponseContext) -> str:
        """
        Build enhanced prompt with all contextual information
        """
        prompt_parts = []
        
        # Base instruction
        prompt_parts.append("Generate a natural, helpful response for this XOFlowers customer.")
        prompt_parts.append(f"CUSTOMER MESSAGE: \"{context.user_message}\"")
        
        # Intent information
        intent_info = {
            'intent': context.intent_data.get('intent'),
            'confidence': context.intent_data.get('confidence'),
            'entities': context.intent_data.get('entities', {}),
            'language': context.intent_data.get('language', 'ro')
        }
        prompt_parts.append(f"INTENT ANALYSIS: {json.dumps(intent_info, ensure_ascii=False)}")
        
        # Conversation context
        if context.conversation_history:
            recent_messages = context.conversation_history[-3:]  # Last 3 exchanges
            prompt_parts.append("RECENT CONVERSATION:")
            for msg in recent_messages:
                prompt_parts.append(f"  User: {msg.get('user', '')}")
                prompt_parts.append(f"  Assistant: {msg.get('assistant', '')}")
        
        # User preferences
        if context.user_preferences:
            prompt_parts.append(f"USER PREFERENCES: {json.dumps(context.user_preferences, ensure_ascii=False)}")
        
        # Product information
        if context.products:
            prompt_parts.append("INTELLIGENT PRODUCT RECOMMENDATIONS:")
            for i, product in enumerate(context.products[:3], 1):  # Top 3 products
                prompt_parts.append(f"  {i}. {product['name']} - {product['price']} MDL")
                prompt_parts.append(f"     {product['description']}")
                
                # Add recommendation reasoning
                if product.get('recommendation_reason'):
                    prompt_parts.append(f"     Motivul recomandării: {product['recommendation_reason']}")
                
                # Add relevance score for AI context
                if product.get('relevance_score'):
                    prompt_parts.append(f"     Relevanță: {product['relevance_score']:.2f}")
                
                # Add product details
                if product.get('colors'):
                    prompt_parts.append(f"     Culori disponibile: {', '.join(product['colors'])}")
                if product.get('occasions'):
                    prompt_parts.append(f"     Potrivit pentru: {', '.join(product['occasions'])}")
                
                # Mark alternatives
                if product.get('is_alternative'):
                    prompt_parts.append(f"     ⚠️ Alternativă pentru: {product.get('alternative_to', 'cererea inițială')}")
                
                # Availability status
                if not product.get('availability', True):
                    prompt_parts.append(f"     ⚠️ Disponibilitate limitată")
                
                prompt_parts.append("")  # Empty line between products
        
        # Enhanced business information
        if context.business_info:
            prompt_parts.append("CONTEXTUAL BUSINESS INFORMATION:")
            
            # Contact information
            if 'contact' in context.business_info:
                contact = context.business_info['contact']
                prompt_parts.append(f"  📞 Contact: {contact.get('phone', '')}")
                prompt_parts.append(f"  📧 Email: {contact.get('email', '')}")
                prompt_parts.append(f"  🌐 Website: {contact.get('website', '')}")
            
            # Location information
            if 'location' in context.business_info:
                location = context.business_info['location']
                prompt_parts.append(f"  📍 Adresa: {location.get('address', '')}")
                prompt_parts.append(f"  🗺️ Zona: {location.get('area', '')}")
                if location.get('accessibility'):
                    prompt_parts.append(f"  🚌 Acces: {location['accessibility']}")
            
            # Working hours
            if 'working_hours' in context.business_info:
                hours = context.business_info['working_hours']
                prompt_parts.append(f"  🕒 Program: {hours.get('schedule', '')}")
                if hours.get('note'):
                    prompt_parts.append(f"  ℹ️ Notă: {hours['note']}")
            
            # Services
            if 'services' in context.business_info:
                services = context.business_info['services']
                main_services = services.get('main_services', [])[:4]  # Top 4 services
                prompt_parts.append(f"  🌸 Servicii principale: {', '.join(main_services)}")
                if services.get('specialties'):
                    specialties = services['specialties'][:2]  # Top 2 specialties
                    prompt_parts.append(f"  ⭐ Specialități: {', '.join(specialties)}")
            
            # Delivery information
            if 'delivery' in context.business_info:
                delivery = context.business_info['delivery']
                prompt_parts.append(f"  🚚 Livrare: {delivery.get('standard_fee', 0)} MDL")
                prompt_parts.append(f"  🆓 Gratuită peste: {delivery.get('free_threshold', 0)} MDL")
                if delivery.get('express_available'):
                    prompt_parts.append(f"  ⚡ Express: {delivery.get('express_fee', 0)} MDL")
                prompt_parts.append(f"  📍 Zonă livrare: {delivery.get('coverage_area', '')}")
                if delivery.get('delivery_time'):
                    prompt_parts.append(f"  ⏰ Timp livrare: {delivery['delivery_time']}")
            
            # Payment information
            if 'payment' in context.business_info:
                payment = context.business_info['payment']
                methods = payment.get('methods', [])[:4]  # Top 4 methods
                prompt_parts.append(f"  💳 Plată: {', '.join(methods)}")
                if payment.get('security'):
                    prompt_parts.append(f"  🔒 Securitate: {payment['security']}")
            
            # Pricing information
            if 'pricing' in context.business_info:
                pricing = context.business_info['pricing']
                if pricing.get('range'):
                    prompt_parts.append(f"  💰 Prețuri: {pricing['range']}")
                if pricing.get('consultation'):
                    prompt_parts.append(f"  💡 {pricing['consultation']}")
            
            # General information
            if 'general' in context.business_info:
                general = context.business_info['general']
                if general.get('description'):
                    prompt_parts.append(f"  📝 Despre noi: {general['description']}")
                if general.get('commitment'):
                    prompt_parts.append(f"  🎯 Angajament: {general['commitment']}")
            
            prompt_parts.append("")  # Empty line after business info
        
        # FAQ match
        if context.faq_match:
            prompt_parts.append("RELEVANT FAQ:")
            prompt_parts.append(f"  Q: {context.faq_match['question']}")
            prompt_parts.append(f"  A: {context.faq_match['answer']}")
        
        # Response instructions
        prompt_parts.append("\nRESPONSE INSTRUCTIONS:")
        prompt_parts.append("- Respond naturally in Romanian (or customer's preferred language)")
        prompt_parts.append("- Integrate product recommendations naturally into conversation")
        prompt_parts.append("- Include relevant business information when appropriate")
        prompt_parts.append("- Maintain conversation context and flow")
        prompt_parts.append("- Be specific and actionable in recommendations")
        prompt_parts.append("- Ask follow-up questions to better help the customer")
        prompt_parts.append("- Include prices and details when discussing products")
        prompt_parts.append("- Suggest alternatives if exact matches aren't available")
        prompt_parts.append("- Use emojis sparingly and appropriately")
        prompt_parts.append("- Keep response length appropriate (2-4 sentences for simple queries, longer for complex ones)")
        
        return "\n".join(prompt_parts)
    
    def _post_process_response(self, response_text: str, context: ResponseContext) -> str:
        """
        Post-process and validate the generated response
        """
        # For now, return the enhanced prompt - the AI engine will process this
        # In a full implementation, this would validate and clean the AI-generated response
        return response_text
    
    def _get_error_fallback_response(self) -> str:
        """
        Get fallback response when response generation fails
        """
        return ("Îmi pare rău, dar în acest moment întâmpin dificultăți în procesarea cererii tale. "
                "Te rog să încerci din nou sau să ne contactezi direct pentru asistență. "
                "Mulțumesc pentru înțelegere! 🌸")

# Global instance
response_generator = NaturalResponseGenerator()

# Convenience function
async def generate_natural_response(user_message: str, intent_data: Dict[str, Any], 
                                  conversation_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate natural response with integrated data sources
    
    Args:
        user_message: User's message text
        intent_data: Intent analysis results
        conversation_context: Conversation history and preferences
        
    Returns:
        Dict containing response and metadata
    """
    return await response_generator.generate_response(user_message, intent_data, conversation_context)