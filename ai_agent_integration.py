#!/usr/bin/env python3
"""
XOFlowers AI Agent - ChromaDB ULTRA Integration
Integrare completă cu Flask app pentru performanță maximă
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import chromadb
from chromadb_ultra_optimizer import XOFlowersUltraDB, SearchResult, UltraPerformanceConfig

logger = logging.getLogger(__name__)

@dataclass 
class ProductRecommendation:
    """Rezultat optimizat pentru agent AI"""
    id: str
    title: str
    description: str
    price: float
    price_tier: str
    category: str
    flower_type: str
    colors: List[str]
    occasions: List[str]
    similarity_score: float
    confidence: float
    search_time: float

class XOFlowersAIAgent:
    """
    AI Agent cu ChromaDB ULTRA Integration
    Pentru Instagram chatbot XOFlowers
    """
    
    def __init__(self, ultra_db_path: str = "./chroma_ultra_db"):
        self.ultra_db = XOFlowersUltraDB(persist_directory=ultra_db_path)
        self.conversation_context = {}
        self.user_preferences = {}
        
        # Check if database exists and is loaded
        if not self._verify_database():
            logger.warning("🔄 Database not found or empty. Loading products...")
            self.ultra_db.ultra_load_products()
        
        logger.info("🤖 XOFlowers AI Agent initialized with ULTRA ChromaDB")
    
    def _verify_database(self) -> bool:
        """Verifică dacă baza de date este încărcată"""
        try:
            if self.ultra_db.collection is None:
                # Try to get existing collection
                collections = self.ultra_db.client.list_collections()
                for collection in collections:
                    if collection.name == self.ultra_db.collection_name:
                        self.ultra_db.collection = collection
                        count = collection.count()
                        logger.info(f"✅ Found existing database with {count} products")
                        return count > 0
                return False
            return True
        except Exception as e:
            logger.error(f"❌ Database verification failed: {e}")
            return False
    
    def intelligent_search(self, 
                          user_query: str, 
                          max_results: int = 5,
                          user_id: Optional[str] = None,
                          conversation_context: Optional[Dict] = None) -> List[ProductRecommendation]:
        """
        Căutare inteligentă cu context și preferințe utilizator
        """
        start_time = time.time()
        
        # Analyze user query
        query_analysis = self._analyze_user_query(user_query)
        
        # Apply user context if available
        if user_id and user_id in self.user_preferences:
            preferences = self.user_preferences[user_id]
            query_analysis.update(preferences)
        
        # Apply conversation context
        if conversation_context:
            self._update_context(query_analysis, conversation_context)
        
        # Execute ULTRA search
        search_results = self.ultra_db.ultra_search(
            query=user_query,
            max_results=max_results * 2,  # Get more for better filtering
            price_min=query_analysis.get('price_min'),
            price_max=query_analysis.get('price_max'),
            category=query_analysis.get('category'),
            flower_type=query_analysis.get('flower_type'),
            has_roses=query_analysis.get('has_roses'),
            occasion=query_analysis.get('occasion'),
            color=query_analysis.get('color')
        )
        
        # Convert to AI Agent format
        recommendations = []
        for result in search_results[:max_results]:
            recommendation = self._convert_to_recommendation(result, query_analysis)
            recommendations.append(recommendation)
        
        # Update user preferences based on search
        if user_id:
            self._update_user_preferences(user_id, query_analysis, recommendations)
        
        search_time = time.time() - start_time
        logger.info(f"🧠 Intelligent search completed in {search_time:.3f}s - {len(recommendations)} recommendations")
        
        return recommendations
    
    def _analyze_user_query(self, query: str) -> Dict[str, Any]:
        """Analizează query-ul utilizatorului pentru extragerea de informații"""
        analysis = {}
        query_lower = query.lower()
        
        # Price analysis
        if any(term in query_lower for term in ['cheap', 'ieftin', 'буджет']):
            analysis['price_max'] = 800
            analysis['price_preference'] = 'budget'
        elif any(term in query_lower for term in ['expensive', 'luxury', 'premium', 'scump']):
            analysis['price_min'] = 1500
            analysis['price_preference'] = 'luxury'
        elif any(term in query_lower for term in ['medium', 'mediu', 'standard']):
            analysis['price_min'] = 600
            analysis['price_max'] = 1500
            analysis['price_preference'] = 'standard'
        
        # Occasion analysis
        occasions = []
        if any(term in query_lower for term in ['wedding', 'nunta', 'свадьба']):
            occasions.append('wedding')
            analysis['occasion'] = 'wedding'
        if any(term in query_lower for term in ['birthday', 'aniversare', 'день рождения']):
            occasions.append('birthday')
            analysis['occasion'] = 'birthday'
        if any(term in query_lower for term in ['love', 'iubire', 'dragoste', 'любовь']):
            occasions.append('love')
            analysis['occasion'] = 'love'
        if any(term in query_lower for term in ['anniversary', 'aniversar']):
            occasions.append('anniversary')
            analysis['occasion'] = 'anniversary'
        
        analysis['detected_occasions'] = occasions
        
        # Flower type analysis
        if any(term in query_lower for term in ['rose', 'trandafir', 'роза']):
            analysis['has_roses'] = True
            analysis['flower_preference'] = 'roses'
        if any(term in query_lower for term in ['peony', 'bujor', 'пион']):
            analysis['flower_preference'] = 'peonies'
        if any(term in query_lower for term in ['hydrangea', 'hortensie']):
            analysis['flower_preference'] = 'hydrangea'
        
        # Color analysis
        colors = []
        if any(term in query_lower for term in ['red', 'rosu', 'roșu', 'красный']):
            colors.append('red')
            analysis['color'] = 'red'
        if any(term in query_lower for term in ['white', 'alb', 'белый']):
            colors.append('white')
            analysis['color'] = 'white'
        if any(term in query_lower for term in ['pink', 'roz', 'розовый']):
            colors.append('pink')
            analysis['color'] = 'pink'
        
        analysis['detected_colors'] = colors
        
        # Intent analysis
        if any(term in query_lower for term in ['recommend', 'suggest', 'recomanda', 'propune']):
            analysis['intent'] = 'recommendation'
        elif any(term in query_lower for term in ['show', 'find', 'cauta', 'arata']):
            analysis['intent'] = 'search'
        elif any(term in query_lower for term in ['help', 'ajutor', 'asist']):
            analysis['intent'] = 'help'
        
        return analysis
    
    def _update_context(self, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Actualizează analiza cu contextul conversației"""
        # Apply previous preferences
        if 'previous_price_range' in context:
            analysis.setdefault('price_preference', context['previous_price_range'])
        
        if 'previous_flower_type' in context:
            analysis.setdefault('flower_preference', context['previous_flower_type'])
        
        if 'previous_occasion' in context:
            analysis.setdefault('occasion', context['previous_occasion'])
    
    def _convert_to_recommendation(self, result: SearchResult, query_analysis: Dict[str, Any]) -> ProductRecommendation:
        """Convertește rezultatul de căutare în recomandare AI"""
        
        # Extract title from text
        title = result.text.split(' - ')[0] if ' - ' in result.text else result.text[:100]
        
        # Extract description
        description = result.text
        if ' | ' in description:
            description = description.split(' | ')[0]
        
        # Parse colors and occasions from metadata
        colors = []
        if result.metadata.get('colors'):
            colors = result.metadata['colors'].split(',') if isinstance(result.metadata['colors'], str) else []
        
        occasions = []
        if result.metadata.get('occasions'):
            occasions = result.metadata['occasions'].split(',') if isinstance(result.metadata['occasions'], str) else []
        
        # Calculate confidence based on query match
        confidence = self._calculate_confidence(result, query_analysis)
        
        return ProductRecommendation(
            id=result.id,
            title=title,
            description=description,
            price=float(result.metadata.get('price', 0)),
            price_tier=result.metadata.get('price_tier', 'unknown'),
            category=result.metadata.get('category', 'Unknown'),
            flower_type=result.metadata.get('flower_type', 'Unknown'),
            colors=colors,
            occasions=occasions,
            similarity_score=result.similarity,
            confidence=confidence,
            search_time=result.search_time
        )
    
    def _calculate_confidence(self, result: SearchResult, query_analysis: Dict[str, Any]) -> float:
        """Calculează confidence score pentru recomandare"""
        confidence = result.similarity * 0.6  # Base confidence from similarity
        
        # Boost based on query analysis match
        metadata = result.metadata
        
        # Price match
        if 'price_preference' in query_analysis:
            if metadata.get('price_tier') == query_analysis['price_preference']:
                confidence += 0.15
        
        # Occasion match  
        if 'detected_occasions' in query_analysis:
            result_occasions = metadata.get('occasions', '').split(',')
            if any(occ in result_occasions for occ in query_analysis['detected_occasions']):
                confidence += 0.1
        
        # Flower type match
        if 'flower_preference' in query_analysis:
            if query_analysis['flower_preference'] in metadata.get('flower_type', '').lower():
                confidence += 0.1
        
        # Color match
        if 'detected_colors' in query_analysis:
            result_colors = metadata.get('colors', '').split(',')
            if any(color in result_colors for color in query_analysis['detected_colors']):
                confidence += 0.05
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _update_user_preferences(self, user_id: str, query_analysis: Dict[str, Any], recommendations: List[ProductRecommendation]):
        """Actualizează preferințele utilizatorului bazat pe căutări"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                'search_count': 0,
                'preferred_price_tier': None,
                'preferred_flowers': [],
                'preferred_colors': [],
                'preferred_occasions': []
            }
        
        prefs = self.user_preferences[user_id]
        prefs['search_count'] += 1
        
        # Update price preference
        if 'price_preference' in query_analysis:
            prefs['preferred_price_tier'] = query_analysis['price_preference']
        
        # Update flower preferences
        if 'flower_preference' in query_analysis:
            if query_analysis['flower_preference'] not in prefs['preferred_flowers']:
                prefs['preferred_flowers'].append(query_analysis['flower_preference'])
        
        # Update color preferences
        if 'detected_colors' in query_analysis:
            for color in query_analysis['detected_colors']:
                if color not in prefs['preferred_colors']:
                    prefs['preferred_colors'].append(color)
        
        # Update occasion preferences
        if 'detected_occasions' in query_analysis:
            for occasion in query_analysis['detected_occasions']:
                if occasion not in prefs['preferred_occasions']:
                    prefs['preferred_occasions'].append(occasion)
    
    def get_personalized_recommendations(self, user_id: str, max_results: int = 3) -> List[ProductRecommendation]:
        """Obține recomandări personalizate bazate pe istoricul utilizatorului"""
        if user_id not in self.user_preferences:
            # Return popular items for new users
            return self.intelligent_search("popular flowers beautiful bouquet", max_results=max_results)
        
        prefs = self.user_preferences[user_id]
        
        # Build personalized query
        query_parts = []
        
        if prefs.get('preferred_flowers'):
            query_parts.extend(prefs['preferred_flowers'])
        
        if prefs.get('preferred_colors'):
            query_parts.extend(prefs['preferred_colors'])
        
        if prefs.get('preferred_occasions'):
            query_parts.extend(prefs['preferred_occasions'])
        
        if not query_parts:
            query_parts = ["beautiful", "flowers", "bouquet"]
        
        personalized_query = " ".join(query_parts)
        
        return self.intelligent_search(
            personalized_query, 
            max_results=max_results,
            user_id=user_id
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obține statistici de performanță"""
        ultra_stats = self.ultra_db.get_performance_stats()
        
        return {
            **ultra_stats,
            "ai_agent_stats": {
                "total_users": len(self.user_preferences),
                "total_conversations": sum(prefs.get('search_count', 0) for prefs in self.user_preferences.values()),
                "database_status": "active" if self._verify_database() else "inactive"
            }
        }

# Flask Integration Helper
def create_ai_agent(ultra_db_path: str = "./chroma_ultra_db") -> XOFlowersAIAgent:
    """
    Factory function pentru crearea AI Agent-ului
    Pentru integrare cu Flask app
    """
    return XOFlowersAIAgent(ultra_db_path=ultra_db_path)

# Quick test function
def test_ai_agent():
    """Test rapid pentru AI Agent"""
    print("🤖 Testing XOFlowers AI Agent...")
    
    agent = XOFlowersAIAgent()
    
    test_queries = [
        "vreau trandafiri roșii pentru iubire",
        "buchet elegant pentru nuntă",
        "ceva ieftin pentru aniversare",
        "luxury roses premium"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        recommendations = agent.intelligent_search(query, max_results=3)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec.title}")
            print(f"     Price: {rec.price} MDL ({rec.price_tier})")
            print(f"     Confidence: {rec.confidence:.2f}")
            print(f"     Colors: {', '.join(rec.colors) if rec.colors else 'N/A'}")
    
    # Performance stats
    stats = agent.get_performance_stats()
    print(f"\n📊 Performance Stats:")
    print(f"  Database size: {stats['database_size']} products")
    print(f"  Average query time: {stats['avg_query_time']:.3f}s")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1f}%")

if __name__ == "__main__":
    test_ai_agent()
