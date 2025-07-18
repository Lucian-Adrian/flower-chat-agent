"""
Product Recommendation System for XOFlowers AI Agent
Connects ChromaDB search results to AI response generation
Implements natural product presentation and alternative suggestions
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.utils.utils import setup_logger
from src.data.chromadb_client import search_products, search_products_with_filters, is_chromadb_available

logger = setup_logger(__name__)

@dataclass
class ProductRecommendation:
    """Product recommendation with context and reasoning"""
    product: Dict[str, Any]
    relevance_score: float
    recommendation_reason: str
    alternative_to: Optional[str] = None

class ProductRecommender:
    """
    Advanced product recommendation system that provides:
    - Intelligent product matching based on user intent
    - Natural product presentation within conversation flow
    - Alternative suggestions when exact matches aren't found
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.logger.info("Product Recommender initialized")
    
    async def get_product_recommendations(self, user_message: str, intent_data: Dict[str, Any], 
                                        user_preferences: Dict[str, Any], 
                                        max_recommendations: int = 3) -> List[ProductRecommendation]:
        """
        Get intelligent product recommendations based on user message and context
        
        Args:
            user_message: User's message text
            intent_data: Intent analysis results
            user_preferences: User's stored preferences
            max_recommendations: Maximum number of recommendations to return
            
        Returns:
            List of ProductRecommendation objects
        """
        try:
            # Extract search parameters
            search_params = self._extract_search_parameters(user_message, intent_data, user_preferences)
            
            # Get products from ChromaDB
            products = await self._search_products_intelligently(search_params, max_recommendations * 2)
            
            # Score and rank products
            recommendations = self._score_and_rank_products(products, search_params, max_recommendations)
            
            # Add alternative suggestions if needed
            if len(recommendations) < max_recommendations:
                alternatives = await self._get_alternative_suggestions(search_params, recommendations)
                recommendations.extend(alternatives[:max_recommendations - len(recommendations)])
            
            self.logger.info(f"Generated {len(recommendations)} product recommendations")
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting product recommendations: {e}")
            return []
    
    def _extract_search_parameters(self, user_message: str, intent_data: Dict[str, Any], 
                                 user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract comprehensive search parameters from all available sources
        """
        entities = intent_data.get('entities', {})
        message_lower = user_message.lower()
        
        search_params = {
            'query': user_message,
            'intent': intent_data.get('intent'),
            'confidence': intent_data.get('confidence', 0.0),
            'language': intent_data.get('language', 'ro')
        }
        
        # Extract flower types
        flowers = entities.get('flowers', [])
        if not flowers:
            # Fallback keyword detection
            flower_keywords = {
                'trandafiri': ['trandafir', 'rose', 'roses'],
                'lalele': ['lalea', 'tulip', 'tulips'],
                'bujori': ['bujor', 'peony', 'peonies'],
                'crizanteme': ['crizantema', 'chrysanthemum'],
                'garoafe': ['garoafa', 'carnation'],
                'gerbera': ['gerbera'],
                'orhidee': ['orhidee', 'orchid']
            }
            
            for flower_type, keywords in flower_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    flowers.append(flower_type)
        
        search_params['flowers'] = flowers
        
        # Extract colors with preference priority
        colors = entities.get('colors', [])
        if not colors and 'preferred_colors' in user_preferences:
            colors = user_preferences['preferred_colors'][:2]  # Top 2 preferred colors
        search_params['colors'] = colors
        
        # Extract occasions
        occasions = entities.get('occasions', [])
        if not occasions and 'occasions' in user_preferences:
            occasions = user_preferences['occasions'][:2]
        search_params['occasions'] = occasions
        
        # Extract budget with user preference fallback
        budget_range = entities.get('budget_range')
        if not budget_range and 'budget_range' in user_preferences:
            budget_range = user_preferences['budget_range']
        search_params['budget_range'] = budget_range
        
        # Extract style preferences
        style_keywords = {
            'elegant': ['elegant', 'sofisticat', 'rafinat'],
            'romantic': ['romantic', 'romantice', 'dragoste'],
            'modern': ['modern', 'contemporan', 'minimalist'],
            'clasic': ['clasic', 'traditional', 'conventional'],
            'colorat': ['colorat', 'vibrant', 'viu']
        }
        
        styles = entities.get('style_preferences', [])
        if not styles:
            for style, keywords in style_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    styles.append(style)
        search_params['styles'] = styles
        
        # Extract urgency
        urgency = entities.get('urgency')
        if not urgency:
            if any(word in message_lower for word in ['urgent', 'azi', 'acum', 'repede']):
                urgency = 'urgent'
            elif any(word in message_lower for word in ['mâine', 'tomorrow']):
                urgency = 'tomorrow'
        search_params['urgency'] = urgency
        
        # Extract recipient information
        recipient = entities.get('recipient')
        if not recipient:
            recipient_keywords = {
                'soție': ['soție', 'soția', 'wife'],
                'mamă': ['mamă', 'mama', 'mother', 'mom'],
                'prietenă': ['prietenă', 'prietena', 'girlfriend', 'friend'],
                'colegă': ['colegă', 'colega', 'colleague'],
                'iubită': ['iubită', 'iubita', 'beloved']
            }
            
            for recip_type, keywords in recipient_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    recipient = recip_type
                    break
        search_params['recipient'] = recipient
        
        return search_params
    
    async def _search_products_intelligently(self, search_params: Dict[str, Any], 
                                           max_results: int) -> List[Dict[str, Any]]:
        """
        Perform intelligent product search using multiple strategies
        """
        if not is_chromadb_available():
            self.logger.warning("ChromaDB not available, using fallback products")
            return self._get_fallback_products(search_params)
        
        try:
            # Build search filters
            filters = {}
            
            # Budget filter
            if search_params.get('budget_range'):
                budget = search_params['budget_range']
                if len(budget) >= 2:
                    filters['price_min'] = budget[0]
                    filters['price_max'] = budget[1]
            
            # Color filter
            if search_params.get('colors'):
                filters['color'] = search_params['colors'][0]
            
            # Occasion filter
            if search_params.get('occasions'):
                filters['occasion'] = search_params['occasions'][0]
            
            # Perform search
            if filters:
                products = await search_products_with_filters(search_params['query'], filters, max_results)
            else:
                products = await search_products(search_params['query'], max_results)
            
            # If no results, try broader search
            if not products and filters:
                self.logger.info("No results with filters, trying broader search")
                products = await search_products(search_params['query'], max_results)
            
            return products
            
        except Exception as e:
            self.logger.error(f"Error in intelligent product search: {e}")
            return self._get_fallback_products(search_params)
    
    def _score_and_rank_products(self, products: List[Dict[str, Any]], 
                               search_params: Dict[str, Any], 
                               max_results: int) -> List[ProductRecommendation]:
        """
        Score and rank products based on relevance to user requirements
        """
        recommendations = []
        
        for product in products:
            score, reason = self._calculate_relevance_score(product, search_params)
            
            if score > 0.3:  # Minimum relevance threshold
                recommendation = ProductRecommendation(
                    product=product,
                    relevance_score=score,
                    recommendation_reason=reason
                )
                recommendations.append(recommendation)
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:max_results]
    
    def _calculate_relevance_score(self, product: Dict[str, Any], 
                                 search_params: Dict[str, Any]) -> Tuple[float, str]:
        """
        Calculate relevance score and generate recommendation reason
        """
        score = 0.0
        reasons = []
        
        # Base similarity score from ChromaDB
        base_score = product.get('similarity_score', 0.5)
        score += base_score * 0.4
        
        # Flower type match
        if search_params.get('flowers'):
            product_category = product.get('category', '').lower()
            for flower in search_params['flowers']:
                if flower.lower() in product_category:
                    score += 0.3
                    reasons.append(f"potrivit pentru {flower}")
                    break
        
        # Color match
        if search_params.get('colors'):
            product_colors = [c.lower() for c in product.get('colors', [])]
            for color in search_params['colors']:
                if color.lower() in product_colors:
                    score += 0.2
                    reasons.append(f"în culoarea {color}")
                    break
        
        # Occasion match
        if search_params.get('occasions'):
            product_occasions = [o.lower() for o in product.get('occasions', [])]
            for occasion in search_params['occasions']:
                if occasion.lower() in product_occasions:
                    score += 0.2
                    reasons.append(f"perfect pentru {occasion}")
                    break
        
        # Budget match
        if search_params.get('budget_range'):
            budget = search_params['budget_range']
            product_price = product.get('price', 0)
            if len(budget) >= 2 and budget[0] <= product_price <= budget[1]:
                score += 0.15
                reasons.append("în bugetul tău")
            elif len(budget) >= 2 and product_price < budget[0]:
                score += 0.1  # Slightly lower score for under-budget items
                reasons.append("sub buget")
        
        # Availability bonus
        if product.get('availability', True):
            score += 0.1
        else:
            score -= 0.2
            reasons.append("disponibilitate limitată")
        
        # Style match
        if search_params.get('styles'):
            product_name_lower = product.get('name', '').lower()
            product_desc_lower = product.get('description', '').lower()
            
            for style in search_params['styles']:
                if style.lower() in product_name_lower or style.lower() in product_desc_lower:
                    score += 0.1
                    reasons.append(f"stil {style}")
                    break
        
        # Generate recommendation reason
        if reasons:
            reason = "Recomandat pentru că este " + ", ".join(reasons[:3])
        else:
            reason = "Opțiune populară pentru florile tale"
        
        return min(score, 1.0), reason
    
    async def _get_alternative_suggestions(self, search_params: Dict[str, Any], 
                                         existing_recommendations: List[ProductRecommendation]) -> List[ProductRecommendation]:
        """
        Get alternative suggestions when exact matches aren't found
        """
        alternatives = []
        existing_ids = {rec.product.get('id') for rec in existing_recommendations}
        
        try:
            # Try broader searches for alternatives
            alternative_queries = self._generate_alternative_queries(search_params)
            
            for alt_query in alternative_queries:
                alt_products = await search_products(alt_query, 3)
                
                for product in alt_products:
                    if product.get('id') not in existing_ids:
                        score, reason = self._calculate_relevance_score(product, search_params)
                        
                        if score > 0.2:  # Lower threshold for alternatives
                            alternative = ProductRecommendation(
                                product=product,
                                relevance_score=score * 0.8,  # Slightly lower score for alternatives
                                recommendation_reason=f"Alternativă: {reason}",
                                alternative_to=search_params.get('query', 'cererea ta')
                            )
                            alternatives.append(alternative)
                            existing_ids.add(product.get('id'))
                
                if len(alternatives) >= 3:
                    break
            
            return alternatives
            
        except Exception as e:
            self.logger.error(f"Error getting alternative suggestions: {e}")
            return []
    
    def _generate_alternative_queries(self, search_params: Dict[str, Any]) -> List[str]:
        """
        Generate alternative search queries for broader recommendations
        """
        alternatives = []
        
        # If looking for specific flowers, suggest similar ones
        if search_params.get('flowers'):
            flower_alternatives = {
                'trandafiri': ['buchete romantice', 'flori roșii', 'aranjamente elegante'],
                'lalele': ['flori de primăvară', 'buchete colorate', 'flori proaspete'],
                'bujori': ['flori mari', 'buchete voluminoase', 'aranjamente luxoase'],
                'crizanteme': ['flori de toamnă', 'buchete durabile', 'aranjamente clasice']
            }
            
            for flower in search_params['flowers']:
                if flower in flower_alternatives:
                    alternatives.extend(flower_alternatives[flower])
        
        # If looking for specific occasions, suggest general categories
        if search_params.get('occasions'):
            occasion_alternatives = {
                'valentine': ['buchete romantice', 'flori roșii', 'cadouri dragoste'],
                'aniversare': ['buchete festive', 'aranjamente speciale', 'flori cadou'],
                'nunta': ['buchete mireasa', 'aranjamente nunta', 'flori albe'],
                'mama': ['buchete mamă', 'flori delicate', 'aranjamente frumoase']
            }
            
            for occasion in search_params['occasions']:
                if occasion in occasion_alternatives:
                    alternatives.extend(occasion_alternatives[occasion])
        
        # General alternatives based on budget
        if search_params.get('budget_range'):
            budget = search_params['budget_range']
            if len(budget) >= 2:
                if budget[1] <= 200:
                    alternatives.extend(['buchete mici', 'flori simple', 'cadouri accesibile'])
                elif budget[1] <= 500:
                    alternatives.extend(['buchete medii', 'aranjamente frumoase', 'flori calitate'])
                else:
                    alternatives.extend(['buchete premium', 'aranjamente luxoase', 'flori exclusive'])
        
        # Default alternatives
        if not alternatives:
            alternatives = [
                'buchete populare',
                'flori de sezon',
                'aranjamente frumoase',
                'cadouri florale',
                'buchete proaspete'
            ]
        
        return alternatives[:3]  # Limit to 3 alternative queries
    
    def _get_fallback_products(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate fallback products when ChromaDB is unavailable
        """
        # Enhanced fallback based on search parameters
        fallback_products = []
        
        # Flower-specific fallbacks
        if search_params.get('flowers'):
            for flower in search_params['flowers']:
                if flower == 'trandafiri':
                    fallback_products.append({
                        'id': f'fallback_{flower}',
                        'name': 'Trandafiri roșii premium',
                        'price': 350,
                        'category': 'trandafiri',
                        'description': 'Trandafiri roșii proaspeți, perfecti pentru ocazii speciale',
                        'availability': True,
                        'colors': ['roșu'],
                        'occasions': ['romantic', 'valentine'],
                        'similarity_score': 0.8
                    })
                elif flower == 'lalele':
                    fallback_products.append({
                        'id': f'fallback_{flower}',
                        'name': 'Lalele colorate de primăvară',
                        'price': 200,
                        'category': 'lalele',
                        'description': 'Lalele proaspete în culori vibrante',
                        'availability': True,
                        'colors': ['galben', 'roz', 'roșu'],
                        'occasions': ['primăvară', 'cadou'],
                        'similarity_score': 0.75
                    })
        
        # Budget-based fallbacks
        budget_range = search_params.get('budget_range')
        if budget_range and len(budget_range) >= 2:
            if budget_range[1] <= 300:
                fallback_products.append({
                    'id': 'fallback_budget_low',
                    'name': 'Buchet accesibil de sezon',
                    'price': 180,
                    'category': 'buchete',
                    'description': 'Buchet frumos și accesibil cu flori de sezon',
                    'availability': True,
                    'colors': ['mixt'],
                    'occasions': ['universal'],
                    'similarity_score': 0.6
                })
            else:
                fallback_products.append({
                    'id': 'fallback_budget_high',
                    'name': 'Aranjament premium exclusiv',
                    'price': 450,
                    'category': 'aranjamente',
                    'description': 'Aranjament luxos cu flori premium selectate',
                    'availability': True,
                    'colors': ['mixt'],
                    'occasions': ['special'],
                    'similarity_score': 0.7
                })
        
        # Default fallbacks if nothing specific
        if not fallback_products:
            fallback_products = [
                {
                    'id': 'fallback_default_1',
                    'name': 'Buchet clasic mixt',
                    'price': 250,
                    'category': 'buchete',
                    'description': 'Buchet elegant cu flori proaspete de sezon',
                    'availability': True,
                    'colors': ['mixt'],
                    'occasions': ['universal'],
                    'similarity_score': 0.6
                },
                {
                    'id': 'fallback_default_2',
                    'name': 'Aranjament floral special',
                    'price': 320,
                    'category': 'aranjamente',
                    'description': 'Aranjament profesional pentru orice ocazie',
                    'availability': True,
                    'colors': ['mixt'],
                    'occasions': ['universal'],
                    'similarity_score': 0.5
                }
            ]
        
        return fallback_products
    
    def format_recommendations_for_ai(self, recommendations: List[ProductRecommendation]) -> Dict[str, Any]:
        """
        Format recommendations for AI response generation
        """
        if not recommendations:
            return {
                'has_recommendations': False,
                'message': 'Nu am găsit produse potrivite, dar pot să îți sugerez să ne contactezi direct pentru recomandări personalizate.'
            }
        
        formatted = {
            'has_recommendations': True,
            'count': len(recommendations),
            'recommendations': []
        }
        
        for i, rec in enumerate(recommendations, 1):
            product = rec.product
            formatted_rec = {
                'rank': i,
                'name': product.get('name', 'Produs floral'),
                'price': product.get('price', 0),
                'description': product.get('description', ''),
                'reason': rec.recommendation_reason,
                'relevance_score': rec.relevance_score,
                'colors': product.get('colors', []),
                'occasions': product.get('occasions', []),
                'availability': product.get('availability', True),
                'is_alternative': rec.alternative_to is not None
            }
            
            if rec.alternative_to:
                formatted_rec['alternative_to'] = rec.alternative_to
            
            formatted['recommendations'].append(formatted_rec)
        
        return formatted

# Global instance
product_recommender = ProductRecommender()

# Convenience functions
async def get_product_recommendations(user_message: str, intent_data: Dict[str, Any], 
                                    user_preferences: Dict[str, Any], 
                                    max_recommendations: int = 3) -> List[ProductRecommendation]:
    """Get intelligent product recommendations"""
    return await product_recommender.get_product_recommendations(
        user_message, intent_data, user_preferences, max_recommendations
    )

def format_recommendations_for_ai(recommendations: List[ProductRecommendation]) -> Dict[str, Any]:
    """Format recommendations for AI response generation"""
    return product_recommender.format_recommendations_for_ai(recommendations)