"""
FAQ and Business Information Manager for XOFlowers AI Agent
Provides access to FAQ data, business hours, contact info, and quick responses
with fallback to system_definitions when JSON files are unavailable
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from pathlib import Path
from functools import lru_cache

from src.utils.system_definitions import get_business_info
from src.utils.utils import setup_logger

logger = setup_logger(__name__)

class FAQManager:
    """
    Manages access to FAQ data and business information with caching
    Provides fallback to system_definitions when JSON files are unavailable
    """
    
    def __init__(self, faq_data_path: str = "data/faq_data.json"):
        """
        Initialize FAQ Manager with caching
        
        Args:
            faq_data_path: Path to the FAQ data JSON file
        """
        self.faq_data_path = Path(faq_data_path)
        self._faq_data: Optional[Dict[str, Any]] = None
        self._cache = {}
        self._cache_ttl = 600  # 10 minutes cache TTL for business info
        self._load_faq_data()
    
    def _load_faq_data(self) -> None:
        """
        Load FAQ data from JSON file with error handling
        """
        try:
            if self.faq_data_path.exists():
                with open(self.faq_data_path, 'r', encoding='utf-8') as file:
                    self._faq_data = json.load(file)
                logger.info(f"Successfully loaded FAQ data from {self.faq_data_path}")
            else:
                logger.warning(f"FAQ data file not found at {self.faq_data_path}")
                self._faq_data = None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in FAQ data file: {e}")
            self._faq_data = None
        except Exception as e:
            logger.error(f"Error loading FAQ data: {e}")
            self._faq_data = None
    
    def _get_cached_data(self, cache_key: str):
        """Get cached data if available and not expired"""
        if cache_key in self._cache:
            cached_item = self._cache[cache_key]
            if time.time() - cached_item['timestamp'] < self._cache_ttl:
                return cached_item['data']
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
        return None
    
    def _cache_data(self, cache_key: str, data) -> None:
        """Cache data with timestamp"""
        self._cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
        
        # Clean up old cache entries periodically
        if len(self._cache) > 20:  # Limit cache size
            self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._cache.items()
            if current_time - value['timestamp'] > self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired FAQ cache entries")
    
    def get_business_hours(self) -> str:
        """
        Get business working hours with caching
        
        Returns:
            str: Formatted business hours string
        """
        cache_key = "business_hours"
        cached_result = self._get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Try to get from FAQ data first
            if self._faq_data and 'business_info' in self._faq_data:
                hours = self._faq_data['business_info'].get('working_hours')
                if hours:
                    logger.debug("Retrieved business hours from FAQ data")
                    self._cache_data(cache_key, hours)
                    return hours
            
            # Fallback to system_definitions
            business_info = get_business_info()
            hours = business_info['working_hours']['display']
            logger.debug("Retrieved business hours from system_definitions fallback")
            self._cache_data(cache_key, hours)
            return hours
            
        except Exception as e:
            logger.error(f"Error retrieving business hours: {e}")
            default_hours = "Luni-Duminică: 09:00-21:00"  # Safe default
            self._cache_data(cache_key, default_hours)
            return default_hours
    
    def get_contact_info(self) -> Dict[str, str]:
        """
        Get contact information (phone, email, location, website) with caching
        
        Returns:
            Dict[str, str]: Contact information dictionary
        """
        cache_key = "contact_info"
        cached_result = self._get_cached_data(cache_key)
        if cached_result:
            return cached_result
        
        try:
            # Try to get from FAQ data first
            if self._faq_data and 'business_info' in self._faq_data:
                business_info = self._faq_data['business_info']
                contact_info = {
                    'phone': business_info.get('phone', ''),
                    'email': business_info.get('email', ''),
                    'location': business_info.get('location', ''),
                    'website': business_info.get('website', ''),
                    'name': business_info.get('name', 'XOFlowers'),
                    'tagline': business_info.get('tagline', '')
                }
                logger.debug("Retrieved contact info from FAQ data")
                self._cache_data(cache_key, contact_info)
                return contact_info
            
            # Fallback to system_definitions
            business_info = get_business_info()
            contact_info = {
                'phone': business_info['phone'],
                'email': business_info['email'],
                'location': business_info['location'],
                'website': business_info['website'],
                'name': business_info['name'],
                'tagline': business_info['tagline']
            }
            logger.debug("Retrieved contact info from system_definitions fallback")
            self._cache_data(cache_key, contact_info)
            return contact_info
            
        except Exception as e:
            logger.error(f"Error retrieving contact info: {e}")
            # Safe default fallback
            default_contact = {
                'phone': '+373 XX XXX XXX',
                'email': 'contact@xoflowers.md',
                'location': 'Chișinău, Moldova',
                'website': 'https://xoflowers.md',
                'name': 'XOFlowers',
                'tagline': 'Cele mai frumoase flori din Chișinău'
            }
            self._cache_data(cache_key, default_contact)
            return default_contact
    
    def get_faq_responses(self) -> List[Dict[str, str]]:
        """
        Get all FAQ question-answer pairs
        
        Returns:
            List[Dict[str, str]]: List of FAQ items with 'question' and 'answer' keys
        """
        try:
            # Try to get from FAQ data first
            if self._faq_data and 'faq' in self._faq_data:
                faq_list = self._faq_data['faq']
                logger.debug(f"Retrieved {len(faq_list)} FAQ items from FAQ data")
                return faq_list
            
            # Fallback to basic FAQ from system_definitions
            logger.warning("FAQ data unavailable, using system_definitions fallback")
            business_info = get_business_info()
            
            # Create basic FAQ from business info
            basic_faq = [
                {
                    "question": "Care sunt orele de lucru?",
                    "answer": f"🕒 Orele noastre de lucru:\n{business_info['working_hours']['display']}"
                },
                {
                    "question": "Unde vă aflați?",
                    "answer": f"📍 Locația XOFlowers:\n• {business_info['location']}\n• Telefon: {business_info['phone']}"
                },
                {
                    "question": "Cum pot comanda?",
                    "answer": f"📱 Cum să comandați:\n• Scrieți-ne direct în chat\n• Apelați la {business_info['phone']}\n• Vizitați {business_info['website']}"
                },
                {
                    "question": "Ce servicii oferiți?",
                    "answer": f"🌸 Serviciile noastre:\n" + "\n".join([f"• {service}" for service in business_info['services']])
                }
            ]
            
            logger.debug(f"Generated {len(basic_faq)} basic FAQ items from system_definitions")
            return basic_faq
            
        except Exception as e:
            logger.error(f"Error retrieving FAQ responses: {e}")
            # Minimal safe fallback
            return [
                {
                    "question": "Cum pot comanda?",
                    "answer": "📱 Puteți comanda scriindu-ne direct în chat sau apelând la +373 XX XXX XXX"
                }
            ]
    
    def search_faq(self, query: str) -> Optional[Dict[str, str]]:
        """
        Search for FAQ item that matches the query
        
        Args:
            query: Search query string
            
        Returns:
            Optional[Dict[str, str]]: Matching FAQ item or None if not found
        """
        try:
            faq_items = self.get_faq_responses()
            query_lower = query.lower()
            
            # Simple keyword matching for FAQ search
            for item in faq_items:
                question_lower = item['question'].lower()
                if any(word in question_lower for word in query_lower.split()):
                    logger.debug(f"Found FAQ match for query: {query}")
                    return item
            
            logger.debug(f"No FAQ match found for query: {query}")
            return None
            
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
            return None
    
    def get_quick_responses(self) -> Dict[str, str]:
        """
        Get quick response templates
        
        Returns:
            Dict[str, str]: Quick response templates
        """
        try:
            # Try to get from FAQ data first
            if self._faq_data and 'quick_responses' in self._faq_data:
                quick_responses = self._faq_data['quick_responses']
                logger.debug("Retrieved quick responses from FAQ data")
                return quick_responses
            
            # Fallback to basic quick responses
            logger.debug("Using fallback quick responses")
            return {
                "greeting": "Bună ziua! 🌸 Bun venit la XOFlowers! Cum vă pot ajuta astăzi?",
                "farewell": "Mulțumim că ați ales XOFlowers! 🌺 O zi frumoasă!",
                "processing": "Un moment, vă caut cele mai frumoase opțiuni... 🌸",
                "error": "Îmi pare rău, a apărut o problemă tehnică. Vă rugăm să încercați din nou sau contactați-ne direct."
            }
            
        except Exception as e:
            logger.error(f"Error retrieving quick responses: {e}")
            return {
                "greeting": "Bună ziua! Bun venit la XOFlowers!",
                "error": "Îmi pare rău, a apărut o problemă. Vă rugăm să încercați din nou."
            }
    
    def get_business_info_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive business information summary
        
        Returns:
            Dict[str, Any]: Complete business information
        """
        try:
            contact_info = self.get_contact_info()
            business_hours = self.get_business_hours()
            
            # Get additional info from system_definitions
            business_info = get_business_info()
            
            summary = {
                'basic_info': contact_info,
                'working_hours': business_hours,
                'services': business_info.get('services', []),
                'delivery': business_info.get('delivery', {}),
                'payment_methods': business_info.get('payment_methods', []),
                'social_media': business_info.get('social_media', {})
            }
            
            logger.debug("Generated comprehensive business info summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating business info summary: {e}")
            # Minimal fallback
            return {
                'basic_info': self.get_contact_info(),
                'working_hours': self.get_business_hours(),
                'services': ['Buchete personalizate', 'Livrare în aceeași zi'],
                'delivery': {'free_threshold': 500, 'standard_fee': 100},
                'payment_methods': ['Card bancar', 'Numerar']
            }
    
    def reload_data(self) -> bool:
        """
        Reload FAQ data from file
        
        Returns:
            bool: True if reload successful, False otherwise
        """
        try:
            self._load_faq_data()
            logger.info("FAQ data reloaded successfully")
            return self._faq_data is not None
        except Exception as e:
            logger.error(f"Error reloading FAQ data: {e}")
            return False

# Global instance for easy access
faq_manager = FAQManager()

# Convenience functions for direct access
def get_business_hours() -> str:
    """Get business working hours"""
    return faq_manager.get_business_hours()

def get_contact_info() -> Dict[str, str]:
    """Get contact information"""
    return faq_manager.get_contact_info()

def get_faq_responses() -> List[Dict[str, str]]:
    """Get all FAQ responses"""
    return faq_manager.get_faq_responses()

def search_faq(query: str) -> Optional[Dict[str, str]]:
    """Search FAQ for matching item"""
    return faq_manager.search_faq(query)

def get_quick_responses() -> Dict[str, str]:
    """Get quick response templates"""
    return faq_manager.get_quick_responses()

def get_business_info_summary() -> Dict[str, Any]:
    """Get comprehensive business information"""
    return faq_manager.get_business_info_summary()