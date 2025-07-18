"""
Business Information Integration System for XOFlowers AI Agent
Connects FAQ data to AI response generation naturally
Adds business hours, contact, and service information integration
Creates fallback responses when business data is unavailable
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.utils.utils import setup_logger
from src.data.faq_manager import (
    get_business_info_summary, search_faq, get_faq_responses, 
    get_business_hours, get_contact_info, get_quick_responses
)

logger = setup_logger(__name__)

@dataclass
class BusinessInfoContext:
    """Context for business information integration"""
    relevant_info: Dict[str, Any]
    faq_matches: List[Dict[str, str]]
    quick_responses: Dict[str, str]
    info_confidence: float
    fallback_used: bool

class BusinessInfoIntegrator:
    """
    Integrates business information naturally into AI responses:
    - FAQ data and business information matching
    - Context-aware information selection
    - Natural presentation within conversation flow
    - Fallback responses when data is unavailable
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Business Information Integrator initialized")
    
    async def get_business_context(self, user_message: str, intent_data: Dict[str, Any]) -> BusinessInfoContext:
        """
        Get comprehensive business information context for AI response generation
        
        Args:
            user_message: User's message text
            intent_data: Intent analysis results
            
        Returns:
            BusinessInfoContext with relevant business information
        """
        try:
            # Analyze what business information is needed
            info_needs = self._analyze_business_info_needs(user_message, intent_data)
            
            # Get relevant business information
            relevant_info = await self._get_contextual_business_info(info_needs)
            
            # Search for FAQ matches
            faq_matches = self._find_relevant_faq_matches(user_message, info_needs)
            
            # Get quick responses for common queries
            quick_responses = get_quick_responses()
            
            # Calculate confidence in information completeness
            info_confidence = self._calculate_info_confidence(relevant_info, faq_matches)
            
            # Check if fallback was used
            fallback_used = self._check_fallback_usage(relevant_info)
            
            context = BusinessInfoContext(
                relevant_info=relevant_info,
                faq_matches=faq_matches,
                quick_responses=quick_responses,
                info_confidence=info_confidence,
                fallback_used=fallback_used
            )
            
            self.logger.debug(f"Generated business context with confidence: {info_confidence:.2f}")
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting business context: {e}")
            return self._get_fallback_context()
    
    def _analyze_business_info_needs(self, user_message: str, intent_data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Analyze what specific business information the user needs
        """
        message_lower = user_message.lower()
        entities = intent_data.get('entities', {})
        intent = intent_data.get('intent', '')
        
        needs = {
            'working_hours': False,
            'contact_info': False,
            'location': False,
            'services': False,
            'delivery_info': False,
            'payment_methods': False,
            'pricing_info': False,
            'social_media': False,
            'general_info': False
        }
        
        # Working hours detection
        hour_keywords = ['orar', 'program', 'ore', 'deschis', 'închis', 'când', 'schedule', 'hours', 'open', 'closed']
        if any(keyword in message_lower for keyword in hour_keywords):
            needs['working_hours'] = True
        
        # Contact information detection
        contact_keywords = ['contact', 'telefon', 'email', 'sună', 'apel', 'scrie', 'phone', 'call', 'write']
        if any(keyword in message_lower for keyword in contact_keywords):
            needs['contact_info'] = True
        
        # Location detection
        location_keywords = ['unde', 'adresa', 'locație', 'găsesc', 'vin', 'where', 'address', 'location', 'find']
        if any(keyword in message_lower for keyword in location_keywords):
            needs['location'] = True
        
        # Services detection
        service_keywords = ['servicii', 'faceți', 'oferiți', 'puteți', 'services', 'offer', 'provide', 'do']
        if any(keyword in message_lower for keyword in service_keywords):
            needs['services'] = True
        
        # Delivery information detection
        delivery_keywords = ['livrare', 'transport', 'aduceți', 'delivery', 'shipping', 'bring']
        if any(keyword in message_lower for keyword in delivery_keywords):
            needs['delivery_info'] = True
        
        # Payment methods detection
        payment_keywords = ['plată', 'plătesc', 'card', 'numerar', 'cost', 'preț', 'payment', 'pay', 'price', 'cost']
        if any(keyword in message_lower for keyword in payment_keywords):
            needs['payment_methods'] = True
            if any(word in message_lower for word in ['cât', 'preț', 'cost', 'how much', 'price']):
                needs['pricing_info'] = True
        
        # Social media detection
        social_keywords = ['instagram', 'facebook', 'telegram', 'social', 'urmăresc', 'follow']
        if any(keyword in message_lower for keyword in social_keywords):
            needs['social_media'] = True
        
        # General business info for greetings or general questions
        if intent in ['greeting', 'general_question'] or not any(needs.values()):
            needs['general_info'] = True
        
        return needs
    
    async def _get_contextual_business_info(self, info_needs: Dict[str, bool]) -> Dict[str, Any]:
        """
        Get contextual business information based on identified needs
        """
        try:
            # Get comprehensive business info
            full_business_info = get_business_info_summary()
            contextual_info = {}
            
            # Add requested information sections
            if info_needs['working_hours']:
                contextual_info['working_hours'] = {
                    'schedule': get_business_hours(),
                    'note': 'Program poate varia în zilele de sărbătoare'
                }
            
            if info_needs['contact_info'] or info_needs['location']:
                contact_info = get_contact_info()
                contextual_info['contact'] = {
                    'phone': contact_info.get('phone', ''),
                    'email': contact_info.get('email', ''),
                    'website': contact_info.get('website', ''),
                    'name': contact_info.get('name', 'XOFlowers'),
                    'tagline': contact_info.get('tagline', '')
                }
                
                if info_needs['location']:
                    contextual_info['location'] = {
                        'address': contact_info.get('location', ''),
                        'area': 'Chișinău, Moldova',
                        'accessibility': 'Ușor accesibil cu transportul public'
                    }
            
            if info_needs['services']:
                contextual_info['services'] = {
                    'main_services': full_business_info.get('services', []),
                    'specialties': [
                        'Consultanță florală personalizată',
                        'Aranjamente pentru evenimente speciale',
                        'Flori proaspete zilnic'
                    ]
                }
            
            if info_needs['delivery_info']:
                delivery_info = full_business_info.get('delivery', {})
                contextual_info['delivery'] = {
                    'standard_fee': delivery_info.get('standard_fee', 100),
                    'free_threshold': delivery_info.get('free_threshold', 500),
                    'express_available': delivery_info.get('express_available', True),
                    'express_fee': delivery_info.get('express_fee', 200),
                    'coverage_area': delivery_info.get('coverage_area', 'Chișinău și împrejurimi'),
                    'delivery_time': 'În aceeași zi pentru comenzile până la 15:00'
                }
            
            if info_needs['payment_methods']:
                contextual_info['payment'] = {
                    'methods': full_business_info.get('payment_methods', []),
                    'preferred': 'Acceptăm toate metodele de plată populare',
                    'security': 'Plăți securizate și protejate'
                }
            
            if info_needs['pricing_info']:
                contextual_info['pricing'] = {
                    'range': 'Prețuri de la 150 MDL pentru buchete simple',
                    'premium': 'Aranjamente premium de la 400 MDL',
                    'custom': 'Prețuri personalizate pentru evenimente speciale',
                    'consultation': 'Consultanță gratuită pentru alegerea perfectă'
                }
            
            if info_needs['social_media']:
                contextual_info['social_media'] = full_business_info.get('social_media', {})
            
            if info_needs['general_info']:
                contextual_info['general'] = {
                    'name': full_business_info['basic_info']['name'],
                    'tagline': full_business_info['basic_info']['tagline'],
                    'description': 'Florăria premium din Chișinău cu flori proaspete și servicii profesionale',
                    'experience': 'Ani de experiență în crearea momentelor speciale',
                    'commitment': 'Calitate superioară și satisfacția clientului'
                }
            
            return contextual_info
            
        except Exception as e:
            self.logger.error(f"Error getting contextual business info: {e}")
            return self._get_basic_fallback_info()
    
    def _find_relevant_faq_matches(self, user_message: str, info_needs: Dict[str, bool]) -> List[Dict[str, str]]:
        """
        Find relevant FAQ matches for the user's query
        """
        try:
            faq_matches = []
            
            # Direct FAQ search
            direct_match = search_faq(user_message)
            if direct_match:
                faq_matches.append(direct_match)
            
            # Search for FAQ items based on identified needs
            all_faq = get_faq_responses()
            
            for need, is_needed in info_needs.items():
                if is_needed and len(faq_matches) < 3:  # Limit to 3 matches
                    need_keywords = self._get_keywords_for_need(need)
                    
                    for faq_item in all_faq:
                        if faq_item not in faq_matches:  # Avoid duplicates
                            question_lower = faq_item['question'].lower()
                            if any(keyword in question_lower for keyword in need_keywords):
                                faq_matches.append(faq_item)
                                break
            
            self.logger.debug(f"Found {len(faq_matches)} relevant FAQ matches")
            return faq_matches
            
        except Exception as e:
            self.logger.error(f"Error finding FAQ matches: {e}")
            return []
    
    def _get_keywords_for_need(self, need: str) -> List[str]:
        """
        Get keywords associated with each business information need
        """
        keyword_map = {
            'working_hours': ['orar', 'program', 'ore', 'deschis'],
            'contact_info': ['contact', 'telefon', 'email'],
            'location': ['unde', 'adresa', 'locație'],
            'services': ['servicii', 'faceți', 'oferiți'],
            'delivery_info': ['livrare', 'transport'],
            'payment_methods': ['plată', 'plătesc', 'card'],
            'pricing_info': ['preț', 'cost', 'cât'],
            'social_media': ['instagram', 'facebook', 'social'],
            'general_info': ['despre', 'cine', 'ce']
        }
        
        return keyword_map.get(need, [])
    
    def _calculate_info_confidence(self, relevant_info: Dict[str, Any], 
                                 faq_matches: List[Dict[str, str]]) -> float:
        """
        Calculate confidence in the completeness of business information
        """
        confidence = 0.0
        
        # Base confidence from having relevant info
        if relevant_info:
            confidence += 0.5
        
        # Bonus for FAQ matches
        if faq_matches:
            confidence += min(len(faq_matches) * 0.15, 0.3)
        
        # Bonus for comprehensive info sections
        info_sections = len(relevant_info.keys())
        confidence += min(info_sections * 0.05, 0.2)
        
        return min(confidence, 1.0)
    
    def _check_fallback_usage(self, relevant_info: Dict[str, Any]) -> bool:
        """
        Check if fallback information was used
        """
        # Simple heuristic: if we have very basic info, likely using fallback
        if not relevant_info:
            return True
        
        # Check for fallback indicators in the data
        for section in relevant_info.values():
            if isinstance(section, dict):
                for value in section.values():
                    if isinstance(value, str) and 'XX XXX XXX' in value:
                        return True
        
        return False
    
    def _get_fallback_context(self) -> BusinessInfoContext:
        """
        Get fallback business context when main system fails
        """
        return BusinessInfoContext(
            relevant_info=self._get_basic_fallback_info(),
            faq_matches=[{
                'question': 'Cum pot comanda?',
                'answer': 'Puteți comanda scriindu-ne direct în chat sau apelând la telefon.'
            }],
            quick_responses={
                'greeting': 'Bună ziua! Bun venit la XOFlowers!',
                'error': 'Îmi pare rău, a apărut o problemă tehnică.'
            },
            info_confidence=0.3,
            fallback_used=True
        )
    
    def _get_basic_fallback_info(self) -> Dict[str, Any]:
        """
        Get basic fallback business information
        """
        return {
            'general': {
                'name': 'XOFlowers',
                'tagline': 'Cele mai frumoase flori din Chișinău',
                'description': 'Florăria premium din Chișinău',
                'commitment': 'Calitate superioară și satisfacția clientului'
            },
            'contact': {
                'phone': '+373 XX XXX XXX',
                'email': 'contact@xoflowers.md',
                'name': 'XOFlowers'
            },
            'working_hours': {
                'schedule': 'Luni-Duminică: 09:00-21:00',
                'note': 'Contactați-ne pentru detalii exacte'
            }
        }
    
    def format_business_context_for_ai(self, context: BusinessInfoContext) -> Dict[str, Any]:
        """
        Format business context for AI response generation
        """
        formatted = {
            'has_business_info': bool(context.relevant_info),
            'info_confidence': context.info_confidence,
            'fallback_used': context.fallback_used,
            'sections': []
        }
        
        # Format each information section
        for section_name, section_data in context.relevant_info.items():
            formatted_section = {
                'type': section_name,
                'data': section_data,
                'presentation_priority': self._get_section_priority(section_name)
            }
            formatted['sections'].append(formatted_section)
        
        # Add FAQ matches
        if context.faq_matches:
            formatted['faq_matches'] = context.faq_matches
            formatted['has_faq_matches'] = True
        else:
            formatted['has_faq_matches'] = False
        
        # Add quick responses
        formatted['quick_responses'] = context.quick_responses
        
        return formatted
    
    def _get_section_priority(self, section_name: str) -> int:
        """
        Get presentation priority for business information sections
        """
        priority_map = {
            'contact': 1,
            'working_hours': 2,
            'location': 3,
            'services': 4,
            'delivery': 5,
            'payment': 6,
            'pricing': 7,
            'social_media': 8,
            'general': 9
        }
        
        return priority_map.get(section_name, 10)

# Global instance
business_info_integrator = BusinessInfoIntegrator()

# Convenience functions
async def get_business_context(user_message: str, intent_data: Dict[str, Any]) -> BusinessInfoContext:
    """Get comprehensive business information context"""
    return await business_info_integrator.get_business_context(user_message, intent_data)

def format_business_context_for_ai(context: BusinessInfoContext) -> Dict[str, Any]:
    """Format business context for AI response generation"""
    return business_info_integrator.format_business_context_for_ai(context)