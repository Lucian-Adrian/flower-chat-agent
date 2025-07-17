"""
Semantic Product Search Engine for XOFlowers Conversational AI
Advanced search with context awareness and natural language understanding
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import re

from .chromadb_manager import ChromaDBManager, get_chromadb_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchIntent:
    """Represents user's search intent extracted from conversation"""
    query: str
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    colors: List[str] = None
    occasions: List[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    style_preferences: List[str] = None
    recipient: Optional[str] = None
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = []
        if self.occasions is None:
            self.occasions = []
        if self.style_preferences is None:
            self.style_preferences = []


@dataclass
class SearchResult:
    """Enhanced search result with conversation context"""
    product: Dict[str, Any]
    similarity_score: float
    relevance_explanation: str
    price_match: bool
    color_match: bool
    occasion_match: bool
    
    def to_conversational_description(self) -> str:
        """Convert to natural description for conversation"""
        product = self.product
        
        description = f"**{product['name']}**\n"
        description += f"💰 {product['price']} MDL\n"
        
        if product.get('colors'):
            colors_text = ", ".join(product['colors'])
            description += f"🎨 Culori: {colors_text}\n"
        
        if product.get('occasions'):
            occasions_text = ", ".join(product['occasions'])
            description += f"🎉 Perfect pentru: {occasions_text}\n"
        
        description += f"✨ {self.relevance_explanation}"
        
        return description


class SemanticSearchEngine:
    """
    Advanced semantic search engine for conversational AI
    Understands natural language queries and provides contextual results
    """
    
    def __init__(self, chromadb_manager: ChromaDBManager = None):
        """
        Initialize semantic search engine
        
        Args:
            chromadb_manager: ChromaDB manager instance
        """
        self.chromadb_manager = chromadb_manager or get_chromadb_manager()
        
        # Romanian search patterns
        self.budget_patterns = [
            r'sub (\d+)',
            r'până la (\d+)',
            r'maxim (\d+)',
            r'între (\d+) și (\d+)',
            r'de la (\d+) la (\d+)',
            r'(\d+)-(\d+) lei',
            r'(\d+) lei'
        ]
        
        self.color_patterns = {
            'roșu': ['roșu', 'rosu', 'red', 'crimson', 'scarlet'],
            'roz': ['roz', 'pink', 'rosa', 'blush'],
            'alb': ['alb', 'white', 'ivory', 'cream'],
            'galben': ['galben', 'yellow', 'gold', 'golden'],
            'violet': ['violet', 'purple', 'lilac', 'lavender'],
            'portocaliu': ['portocaliu', 'orange', 'coral', 'peach'],
            'albastru': ['albastru', 'blue', 'navy'],
            'verde': ['verde', 'green']
        }
        
        self.occasion_patterns = {
            'valentine': ['valentine', 'dragobete', 'iubire', 'romantic', 'dragoste'],
            'anniversary': ['aniversare', 'anniversary', 'sărbătoare'],
            'birthday': ['zi de naștere', 'birthday', 'naștere', 'aniversare'],
            'wedding': ['nuntă', 'wedding', 'căsătorie', 'mireasă'],
            'mother_day': ['mama', 'mother', 'mamă', 'pentru mama'],
            'graduation': ['absolvire', 'graduation', 'diplomă'],
            'sympathy': ['condoleanțe', 'sympathy', 'tristețe', 'înmormântare'],
            'congratulations': ['felicitări', 'congratulations', 'succes'],
            'apology': ['scuze', 'apology', 'iertare', 'să mă ierți']
        }
        
        self.category_patterns = {
            'bouquets': ['buchet', 'buchete', 'bouquet'],
            'boxes': ['cutie', 'cutii', 'box'],
            'baskets': ['coș', 'coșuri', 'basket'],
            'plants': ['plantă', 'plante', 'plant']
        }
        
        self.quantity_patterns = [
            r'(\d+) (flori|trandafiri|bujori)',
            r'un buchet de (\d+)',
            r'(\d+) bucăți'
        ]
    
    def extract_search_intent(self, query: str, conversation_context: Optional[Dict] = None) -> SearchIntent:
        """
        Extract structured search intent from natural language query
        
        Args:
            query: Natural language search query
            conversation_context: Previous conversation context
            
        Returns:
            Structured search intent
        """
        query_lower = query.lower()
        
        # Extract budget
        budget_min, budget_max = self._extract_budget(query_lower)
        
        # Extract colors
        colors = self._extract_colors(query_lower)
        
        # Extract occasions
        occasions = self._extract_occasions(query_lower)
        
        # Extract category
        category = self._extract_category(query_lower)
        
        # Extract quantity
        quantity = self._extract_quantity(query_lower)
        
        # Extract style preferences
        style_preferences = self._extract_style_preferences(query_lower)
        
        # Extract recipient
        recipient = self._extract_recipient(query_lower)
        
        # Clean query for semantic search
        clean_query = self._clean_query_for_search(query)
        
        search_intent = SearchIntent(
            query=clean_query,
            budget_min=budget_min,
            budget_max=budget_max,
            colors=colors,
            occasions=occasions,
            category=category,
            quantity=quantity,
            style_preferences=style_preferences,
            recipient=recipient
        )
        
        logger.info(f"🎯 Extracted search intent: {search_intent}")
        return search_intent
    
    def _extract_budget(self, query: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract budget range from query"""
        for pattern in self.budget_patterns:
            match = re.search(pattern, query)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    # Single budget limit
                    budget = float(groups[0])
                    if 'sub' in pattern or 'până' in pattern or 'maxim' in pattern:
                        return None, budget
                    else:
                        return budget, None
                elif len(groups) == 2:
                    # Budget range
                    return float(groups[0]), float(groups[1])
        
        return None, None
    
    def _extract_colors(self, query: str) -> List[str]:
        """Extract colors mentioned in query"""
        colors = []
        for color_ro, patterns in self.color_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    colors.append(color_ro)
                    break
        return colors
    
    def _extract_occasions(self, query: str) -> List[str]:
        """Extract occasions mentioned in query"""
        occasions = []
        for occasion, patterns in self.occasion_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    occasions.append(occasion)
                    break
        return occasions
    
    def _extract_category(self, query: str) -> Optional[str]:
        """Extract product category from query"""
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    return category
        return None
    
    def _extract_quantity(self, query: str) -> Optional[int]:
        """Extract quantity from query"""
        for pattern in self.quantity_patterns:
            match = re.search(pattern, query)
            if match:
                return int(match.group(1))
        return None
    
    def _extract_style_preferences(self, query: str) -> List[str]:
        """Extract style preferences from query"""
        styles = []
        style_keywords = {
            'elegant': ['elegant', 'rafinat', 'sofisticat'],
            'romantic': ['romantic', 'tandru', 'dulce'],
            'modern': ['modern', 'contemporan', 'stylish'],
            'classic': ['clasic', 'tradițional', 'timeless'],
            'luxury': ['luxury', 'premium', 'scump', 'luxos'],
            'simple': ['simplu', 'minimalist', 'modest']
        }
        
        for style, keywords in style_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    styles.append(style)
                    break
        
        return styles
    
    def _extract_recipient(self, query: str) -> Optional[str]:
        """Extract recipient information from query"""
        recipients = {
            'soție': ['soție', 'soția', 'nevastă'],
            'mamă': ['mamă', 'mama', 'mother'],
            'prietenă': ['prietenă', 'girlfriend', 'iubită'],
            'colegă': ['colegă', 'colleague'],
            'fiică': ['fiică', 'fata'],
            'general': ['ea', 'pentru ea', 'femeia']
        }
        
        for recipient, keywords in recipients.items():
            for keyword in keywords:
                if keyword in query:
                    return recipient
        
        return None
    
    def _clean_query_for_search(self, query: str) -> str:
        """Clean query for better semantic search"""
        # Remove budget mentions
        cleaned = re.sub(r'\b\d+\s*(lei|mdl)\b', '', query, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bsub \d+\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bpână la \d+\b', '', cleaned, flags=re.IGNORECASE)
        
        # Remove common stop words but keep important ones
        stop_words = ['vreau', 'caut', 'îmi', 'trebuie', 'pentru', 'să', 'cu']
        words = cleaned.split()
        words = [word for word in words if word.lower() not in stop_words]
        
        # Join and clean up
        cleaned = ' '.join(words)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned if cleaned else query
    
    def search_products(self, search_intent: SearchIntent, n_results: int = 5) -> List[SearchResult]:
        """
        Perform semantic search based on search intent
        
        Args:
            search_intent: Structured search intent
            n_results: Number of results to return
            
        Returns:
            List of enhanced search results
        """
        try:
            # Prepare filters
            filters = {}
            
            if search_intent.budget_min is not None:
                filters['min_price'] = search_intent.budget_min
            if search_intent.budget_max is not None:
                filters['max_price'] = search_intent.budget_max
            
            if search_intent.category:
                # Map category to collection
                collection_key = self._get_collection_for_category(search_intent.category)
            else:
                collection_key = 'products_main'
            
            # Perform semantic search
            raw_results = self.chromadb_manager.search_products(
                query=search_intent.query,
                collection_key=collection_key,
                n_results=n_results * 2,  # Get more results for filtering
                filters=filters
            )
            
            # Enhance results with context
            enhanced_results = []
            for result in raw_results:
                enhanced_result = self._enhance_search_result(result, search_intent)
                if enhanced_result:
                    enhanced_results.append(enhanced_result)
            
            # Sort by relevance and return top results
            enhanced_results.sort(key=lambda x: x.similarity_score, reverse=True)
            
            logger.info(f"🔍 Found {len(enhanced_results)} relevant products")
            return enhanced_results[:n_results]
            
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return []
    
    def _get_collection_for_category(self, category: str) -> str:
        """Map category to ChromaDB collection"""
        category_mapping = {
            'bouquets': 'products_bouquets',
            'boxes': 'products_boxes',
            'baskets': 'products_boxes',
            'plants': 'products_plants'
        }
        return category_mapping.get(category, 'products_main')
    
    def _enhance_search_result(self, raw_result: Dict, search_intent: SearchIntent) -> Optional[SearchResult]:
        """
        Enhance raw search result with context and relevance explanation
        
        Args:
            raw_result: Raw result from ChromaDB
            search_intent: Original search intent
            
        Returns:
            Enhanced search result or None if not relevant
        """
        try:
            # Check relevance
            relevance_score = raw_result.get('similarity_score', 0)
            
            # Check price match
            price = raw_result.get('price', 0)
            price_match = True
            if search_intent.budget_min and price < search_intent.budget_min:
                price_match = False
            if search_intent.budget_max and price > search_intent.budget_max:
                price_match = False
            
            # Check color match
            product_colors = raw_result.get('colors', [])
            color_match = not search_intent.colors or any(
                color in product_colors for color in search_intent.colors
            )
            
            # Check occasion match
            product_occasions = raw_result.get('occasions', [])
            occasion_match = not search_intent.occasions or any(
                occasion in product_occasions for occasion in search_intent.occasions
            )
            
            # Generate relevance explanation
            explanation = self._generate_relevance_explanation(
                raw_result, search_intent, price_match, color_match, occasion_match
            )
            
            # Calculate final relevance score
            final_score = relevance_score
            if price_match:
                final_score += 0.1
            if color_match:
                final_score += 0.1
            if occasion_match:
                final_score += 0.1
            
            return SearchResult(
                product=raw_result,
                similarity_score=final_score,
                relevance_explanation=explanation,
                price_match=price_match,
                color_match=color_match,
                occasion_match=occasion_match
            )
            
        except Exception as e:
            logger.warning(f"Error enhancing result: {e}")
            return None
    
    def _generate_relevance_explanation(self, 
                                     product: Dict, 
                                     search_intent: SearchIntent,
                                     price_match: bool,
                                     color_match: bool,
                                     occasion_match: bool) -> str:
        """Generate natural explanation of why this product is relevant"""
        explanations = []
        
        if price_match and (search_intent.budget_min or search_intent.budget_max):
            explanations.append("se încadrează în bugetul dumneavoastră")
        
        if color_match and search_intent.colors:
            matching_colors = [c for c in search_intent.colors if c in product.get('colors', [])]
            if matching_colors:
                explanations.append(f"disponibil în {', '.join(matching_colors)}")
        
        if occasion_match and search_intent.occasions:
            matching_occasions = [o for o in search_intent.occasions if o in product.get('occasions', [])]
            if matching_occasions:
                explanations.append(f"perfect pentru {', '.join(matching_occasions)}")
        
        if search_intent.style_preferences:
            explanations.append("potrivit cu stilul preferat")
        
        if not explanations:
            explanations.append("potrivit pentru cererea dumneavoastră")
        
        return "Acest produs " + " și ".join(explanations) + "."
    
    def find_similar_products(self, product_id: str, n_results: int = 3) -> List[SearchResult]:
        """Find products similar to a given product"""
        try:
            similar_products = self.chromadb_manager.get_similar_products(product_id, n_results)
            
            results = []
            for product in similar_products:
                result = SearchResult(
                    product=product,
                    similarity_score=product.get('similarity_score', 0.8),
                    relevance_explanation="Similar cu produsul selectat anterior.",
                    price_match=True,
                    color_match=True,
                    occasion_match=True
                )
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error finding similar products: {e}")
            return []
    
    def search_by_budget_range(self, min_price: float, max_price: float, n_results: int = 5) -> List[SearchResult]:
        """Search products within a specific budget range"""
        search_intent = SearchIntent(
            query="flori frumoase",
            budget_min=min_price,
            budget_max=max_price
        )
        
        return self.search_products(search_intent, n_results)
    
    def search_by_occasion(self, occasion: str, n_results: int = 5) -> List[SearchResult]:
        """Search products suitable for a specific occasion"""
        search_intent = SearchIntent(
            query=f"flori pentru {occasion}",
            occasions=[occasion]
        )
        
        return self.search_products(search_intent, n_results)
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []
        
        # Common search patterns
        common_searches = [
            "buchete roșii pentru Valentine's Day",
            "trandafiri albi pentru nuntă",
            "flori pentru mama",
            "cadou sub 500 lei",
            "bujori roz pentru aniversare",
            "cutie cu flori elegante",
            "coș cu flori mixte"
        ]
        
        partial_lower = partial_query.lower()
        for search in common_searches:
            if any(word in search.lower() for word in partial_lower.split()):
                suggestions.append(search)
        
        return suggestions[:5]


# Global search engine instance
_search_engine = None

def get_search_engine() -> SemanticSearchEngine:
    """Get the global search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SemanticSearchEngine()
    return _search_engine