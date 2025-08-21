"""
Enhanced Search Integration with Redis Caching
Integrates Redis caching with existing search systems for improved performance
"""

from typing import Dict, List, Optional, Any, Union
import time

from src.utils.utils import setup_logger
from .redis_search_cache import RedisSearchCache, get_search_cache

logger = setup_logger(__name__)


class EnhancedSearchManager:
    """
    Enhanced search manager that adds Redis caching to existing search systems
    Provides a unified interface for all search operations with caching
    """
    
    def __init__(self, redis_cache: Optional[RedisSearchCache] = None):
        """Initialize enhanced search manager"""
        self.redis_cache = redis_cache or get_search_cache()
        
        # Lazy load search engines to avoid circular imports
        self._product_search_engine = None
        self._vector_search = None
        self._simplified_search = None
        self._file_search_engine = None
        
        logger.info("Enhanced Search Manager initialized with Redis caching")
    
    @property
    def product_search_engine(self):
        """Lazy load product search engine"""
        if self._product_search_engine is None:
            try:
                from src.intelligence.product_search import get_search_engine
                self._product_search_engine = get_search_engine()
            except ImportError as e:
                logger.warning(f"Could not import product search engine: {e}")
        return self._product_search_engine
    
    @property
    def vector_search(self):
        """Lazy load vector search"""
        if self._vector_search is None:
            try:
                from src.database.vector_search import universal_search
                self._vector_search = universal_search
            except ImportError as e:
                logger.warning(f"Could not import vector search: {e}")
        return self._vector_search
    
    @property
    def simplified_search(self):
        """Lazy load simplified search"""
        if self._simplified_search is None:
            try:
                from src.database.simplified_search import db as simplified_db
                self._simplified_search = simplified_db
            except ImportError as e:
                logger.warning(f"Could not import simplified search: {e}")
        return self._simplified_search
    
    @property
    def file_search_engine(self):
        """Lazy load file search engine"""
        if self._file_search_engine is None:
            try:
                from .redis_file_search import get_file_search_engine
                self._file_search_engine = get_file_search_engine()
            except ImportError as e:
                logger.warning(f"Could not import file search engine: {e}")
        return self._file_search_engine
    
    def search_products(self, query: str, limit: int = 10, budget: Optional[float] = None, 
                       category: Optional[str] = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search products with Redis caching
        
        Args:
            query: Search query
            limit: Maximum number of results
            budget: Budget constraint
            category: Product category filter
            use_cache: Whether to use Redis cache
            
        Returns:
            List of product search results
        """
        search_type = "products"
        filters = {'limit': limit, 'budget': budget, 'category': category}
        
        # Check cache first if enabled
        if use_cache:
            cached_results = self.redis_cache.get_cached_search(search_type, query, filters)
            if cached_results:
                return cached_results[:limit]
        
        # Perform actual search using available search engines
        results = []
        start_time = time.time()
        
        try:
            # Try vector search first (most comprehensive)
            if self.vector_search:
                if budget:
                    results = self.vector_search.search_budget_flowers(budget, query, limit)
                elif category:
                    # Map category to appropriate search method
                    if category.lower() in ['flowers', 'bouquets', 'roses']:
                        results = self.vector_search.search_flowers_only(query, limit)
                    else:
                        results = self.vector_search.search_all_products(query, limit)
                else:
                    results = self.vector_search.smart_search(query, limit)
            
            # Fallback to simplified search if vector search unavailable
            elif self.simplified_search:
                if budget:
                    results = self.simplified_search.search_with_budget(query, budget, limit)
                else:
                    results = self.simplified_search.search(query, limit)
            
            # Fallback to product search engine
            elif self.product_search_engine:
                from src.intelligence.product_search import SearchIntent
                search_intent = SearchIntent(
                    query=query,
                    budget_max=budget,
                    category=category
                )
                search_results = self.product_search_engine.search_products(search_intent, limit)
                # Convert SearchResult objects to dictionaries
                results = [result.product for result in search_results]
            
            search_duration = time.time() - start_time
            logger.debug(f"Product search completed in {search_duration:.3f}s, found {len(results)} results")
            
            # Cache results if caching is enabled and we have results
            if use_cache and results:
                self.redis_cache.cache_search_results(search_type, query, results, filters)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in product search: {e}")
            return []
    
    def search_flowers_only(self, query: str, limit: int = 10, budget: Optional[float] = None, 
                           use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search only flowers with Redis caching
        
        Args:
            query: Search query
            limit: Maximum number of results
            budget: Budget constraint
            use_cache: Whether to use Redis cache
            
        Returns:
            List of flower search results
        """
        search_type = "flowers"
        filters = {'limit': limit, 'budget': budget}
        
        # Check cache first if enabled
        if use_cache:
            cached_results = self.redis_cache.get_cached_search(search_type, query, filters)
            if cached_results:
                return cached_results[:limit]
        
        # Perform actual search
        results = []
        start_time = time.time()
        
        try:
            if self.vector_search:
                if budget:
                    results = self.vector_search.search_budget_flowers(budget, query, limit)
                else:
                    results = self.vector_search.search_flowers_only(query, limit)
            elif self.simplified_search:
                results = self.simplified_search.search_flowers(query, limit)
            
            search_duration = time.time() - start_time
            logger.debug(f"Flower search completed in {search_duration:.3f}s, found {len(results)} results")
            
            # Cache results
            if use_cache and results:
                self.redis_cache.cache_search_results(search_type, query, results, filters)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in flower search: {e}")
            return []
    
    def search_files(self, query: str, file_types: Optional[List[str]] = None, 
                    case_sensitive: bool = False, max_results: int = 50, 
                    use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search files with Redis caching
        
        Args:
            query: Search query
            file_types: List of file extensions to search
            case_sensitive: Whether search should be case sensitive
            max_results: Maximum number of results
            use_cache: Whether to use Redis cache
            
        Returns:
            List of file search results
        """
        if not self.file_search_engine:
            return []
        
        search_type = "files"
        filters = {
            'file_types': file_types,
            'case_sensitive': case_sensitive,
            'max_results': max_results
        }
        
        # Check cache first if enabled
        if use_cache:
            cached_results = self.redis_cache.get_cached_search(search_type, query, filters)
            if cached_results:
                return cached_results[:max_results]
        
        # Perform actual search
        try:
            results = self.file_search_engine.search_files(query, file_types, case_sensitive, max_results)
            
            # Cache results
            if use_cache and results:
                self.redis_cache.cache_search_results(search_type, query, results, filters)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in file search: {e}")
            return []
    
    def search_by_price_range(self, min_price: float, max_price: float, 
                             query: str = "", limit: int = 10, flowers_only: bool = False,
                             use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Search products by price range with Redis caching
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            query: Additional search query
            limit: Maximum number of results
            flowers_only: Search only flowers
            use_cache: Whether to use Redis cache
            
        Returns:
            List of search results
        """
        search_type = "price_range" if not flowers_only else "price_range_flowers"
        filters = {
            'min_price': min_price,
            'max_price': max_price,
            'limit': limit,
            'flowers_only': flowers_only
        }
        
        # Check cache first
        if use_cache:
            cached_results = self.redis_cache.get_cached_search(search_type, query, filters)
            if cached_results:
                return cached_results[:limit]
        
        # Perform search
        results = []
        try:
            if self.vector_search:
                results = self.vector_search.search_by_price_range(
                    min_price, max_price, query, limit, flowers_only
                )
            
            # Cache results
            if use_cache and results:
                self.redis_cache.cache_search_results(search_type, query, results, filters)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in price range search: {e}")
            return []
    
    def get_search_suggestions(self, partial_query: str, search_type: str = "products") -> List[str]:
        """
        Get search suggestions based on popular terms and partial query
        
        Args:
            partial_query: Partial search query
            search_type: Type of search for suggestions
            
        Returns:
            List of search suggestions
        """
        suggestions = []
        
        try:
            # Get popular search terms from cache
            popular_terms = self.redis_cache.get_popular_search_terms(20)
            
            # Filter popular terms that match partial query
            partial_lower = partial_query.lower()
            for term_data in popular_terms:
                term = term_data['term']
                if partial_lower in term.lower() and term not in suggestions:
                    suggestions.append(term)
            
            # Add some default suggestions based on search type
            if search_type == "products" and len(suggestions) < 5:
                default_suggestions = [
                    "buchete roșii", "trandafiri albi", "flori pentru mama",
                    "cadou sub 500 lei", "bujori roz", "cutie cu flori"
                ]
                for suggestion in default_suggestions:
                    if partial_lower in suggestion.lower() and suggestion not in suggestions:
                        suggestions.append(suggestion)
            
            elif search_type == "files" and len(suggestions) < 5:
                default_suggestions = [
                    "redis", "search", "function", "class", "import", "def"
                ]
                for suggestion in default_suggestions:
                    if partial_lower in suggestion.lower() and suggestion not in suggestions:
                        suggestions.append(suggestion)
            
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []
    
    def get_comprehensive_search_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive search statistics across all search types
        
        Returns:
            Dictionary with detailed search statistics
        """
        try:
            cache_stats = self.redis_cache.get_cache_statistics()
            popular_terms = self.redis_cache.get_popular_search_terms(10)
            
            # Add additional statistics
            stats = {
                'cache_statistics': cache_stats,
                'popular_search_terms': popular_terms,
                'search_engines_status': {
                    'vector_search': self.vector_search is not None,
                    'simplified_search': self.simplified_search is not None,
                    'product_search_engine': self.product_search_engine is not None,
                    'file_search_engine': self.file_search_engine is not None
                },
                'redis_cache_available': self.redis_cache.redis_client.is_available()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting search statistics: {e}")
            return {'error': str(e)}
    
    def clear_all_caches(self) -> bool:
        """
        Clear all search caches
        
        Returns:
            True if cleared successfully
        """
        try:
            success = self.redis_cache.clear_cache()
            if success:
                logger.info("All search caches cleared successfully")
            return success
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")
            return False
    
    def invalidate_search(self, query: str, search_type: Optional[str] = None) -> bool:
        """
        Invalidate cache for a specific search query
        
        Args:
            query: Search query to invalidate
            search_type: Specific search type to invalidate
            
        Returns:
            True if invalidated successfully
        """
        try:
            success = self.redis_cache.invalidate_search_cache(query, search_type)
            if success:
                logger.info(f"Cache invalidated for query: {query}")
            return success
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False


# Global instance for easy access
_enhanced_search_manager = None

def get_enhanced_search_manager() -> EnhancedSearchManager:
    """Get the global enhanced search manager instance"""
    global _enhanced_search_manager
    if _enhanced_search_manager is None:
        _enhanced_search_manager = EnhancedSearchManager()
    return _enhanced_search_manager


# Convenience functions for direct access
def search_products_cached(query: str, limit: int = 10, budget: Optional[float] = None, 
                          category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search products with Redis caching"""
    return get_enhanced_search_manager().search_products(query, limit, budget, category)


def search_flowers_cached(query: str, limit: int = 10, budget: Optional[float] = None) -> List[Dict[str, Any]]:
    """Search flowers with Redis caching"""
    return get_enhanced_search_manager().search_flowers_only(query, limit, budget)


def search_files_cached(query: str, file_types: Optional[List[str]] = None, 
                       case_sensitive: bool = False, max_results: int = 50) -> List[Dict[str, Any]]:
    """Search files with Redis caching"""
    return get_enhanced_search_manager().search_files(query, file_types, case_sensitive, max_results)


def get_search_suggestions(partial_query: str, search_type: str = "products") -> List[str]:
    """Get search suggestions"""
    return get_enhanced_search_manager().get_search_suggestions(partial_query, search_type)


def get_search_stats() -> Dict[str, Any]:
    """Get comprehensive search statistics"""
    return get_enhanced_search_manager().get_comprehensive_search_stats()


def clear_search_caches() -> bool:
    """Clear all search caches"""
    return get_enhanced_search_manager().clear_all_caches()