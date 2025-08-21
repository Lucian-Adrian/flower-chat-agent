"""
Redis Search Cache Manager for XOFlowers AI Agent
Provides caching layer for search results to improve performance
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from src.utils.utils import setup_logger
from .redis_client import RedisClient

logger = setup_logger(__name__)


class RedisSearchCache:
    """
    Redis-based search cache manager for improved search performance
    Caches search results, popular terms, and search analytics
    """
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        """Initialize Redis search cache"""
        self.redis_client = redis_client or RedisClient()
        
        # Cache key prefixes
        self.search_cache_prefix = "xoflowers:search:"
        self.analytics_prefix = "xoflowers:search_analytics:"
        self.popular_terms_key = "xoflowers:popular_search_terms"
        
        # Cache settings
        self.default_ttl = 3600  # 1 hour default TTL
        self.popular_terms_ttl = 86400  # 24 hours for popular terms
        self.max_cache_size = 1000  # Maximum cached searches
        
        logger.info("Redis Search Cache initialized")
    
    def _generate_cache_key(self, search_type: str, query: str, filters: Optional[Dict] = None) -> str:
        """
        Generate a unique cache key for a search query
        
        Args:
            search_type: Type of search (products, flowers, files, etc.)
            query: Search query string
            filters: Additional search filters
            
        Returns:
            Unique cache key
        """
        # Create a fingerprint of the search parameters
        search_data = {
            'type': search_type,
            'query': query.lower().strip(),
            'filters': filters or {}
        }
        
        search_string = json.dumps(search_data, sort_keys=True, ensure_ascii=False)
        search_hash = hashlib.md5(search_string.encode('utf-8')).hexdigest()
        
        return f"{self.search_cache_prefix}{search_type}:{search_hash}"
    
    def get_cached_search(self, search_type: str, query: str, filters: Optional[Dict] = None) -> Optional[List[Dict]]:
        """
        Retrieve cached search results
        
        Args:
            search_type: Type of search
            query: Search query
            filters: Search filters
            
        Returns:
            Cached search results or None if not found
        """
        if not self.redis_client.is_available():
            return None
            
        try:
            cache_key = self._generate_cache_key(search_type, query, filters)
            cached_data = self.redis_client.client.get(cache_key)
            
            if cached_data:
                # Track cache hit
                self._record_cache_hit(search_type, query)
                
                # Parse and return results
                result = json.loads(cached_data)
                logger.debug(f"Cache HIT for search: {search_type} - {query}")
                return result.get('results', [])
            else:
                # Track cache miss
                self._record_cache_miss(search_type, query)
                logger.debug(f"Cache MISS for search: {search_type} - {query}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving cached search: {e}")
            return None
    
    def cache_search_results(self, search_type: str, query: str, results: List[Dict], 
                           filters: Optional[Dict] = None, ttl: Optional[int] = None) -> bool:
        """
        Cache search results in Redis
        
        Args:
            search_type: Type of search
            query: Search query
            results: Search results to cache
            filters: Search filters used
            ttl: Time to live in seconds
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis_client.is_available() or not results:
            return False
            
        try:
            cache_key = self._generate_cache_key(search_type, query, filters)
            cache_ttl = ttl or self.default_ttl
            
            # Prepare cache data
            cache_data = {
                'results': results,
                'query': query,
                'search_type': search_type,
                'filters': filters,
                'cached_at': datetime.now().isoformat(),
                'result_count': len(results)
            }
            
            # Store in Redis with TTL
            serialized_data = json.dumps(cache_data, ensure_ascii=False)
            success = self.redis_client.client.setex(cache_key, cache_ttl, serialized_data)
            
            if success:
                # Record popular search term
                self._record_search_term(query)
                logger.debug(f"Cached search results: {search_type} - {query} ({len(results)} results)")
                return True
            else:
                logger.warning(f"Failed to cache search results: {search_type} - {query}")
                return False
                
        except Exception as e:
            logger.error(f"Error caching search results: {e}")
            return False
    
    def _record_search_term(self, query: str) -> None:
        """Record a search term for popularity tracking"""
        if not self.redis_client.is_available():
            return
            
        try:
            # Increment search count for this term
            self.redis_client.client.zincrby(self.popular_terms_key, 1, query.lower().strip())
            
            # Set expiry for the popular terms set
            self.redis_client.client.expire(self.popular_terms_key, self.popular_terms_ttl)
            
        except Exception as e:
            logger.error(f"Error recording search term: {e}")
    
    def _record_cache_hit(self, search_type: str, query: str) -> None:
        """Record cache hit for analytics"""
        if not self.redis_client.is_available():
            return
            
        try:
            analytics_key = f"{self.analytics_prefix}hits:{search_type}"
            self.redis_client.client.incr(analytics_key)
            self.redis_client.client.expire(analytics_key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Error recording cache hit: {e}")
    
    def _record_cache_miss(self, search_type: str, query: str) -> None:
        """Record cache miss for analytics"""
        if not self.redis_client.is_available():
            return
            
        try:
            analytics_key = f"{self.analytics_prefix}misses:{search_type}"
            self.redis_client.client.incr(analytics_key)
            self.redis_client.client.expire(analytics_key, 86400)  # 24 hours
            
        except Exception as e:
            logger.error(f"Error recording cache miss: {e}")
    
    def get_popular_search_terms(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular search terms
        
        Args:
            limit: Maximum number of terms to return
            
        Returns:
            List of popular search terms with counts
        """
        if not self.redis_client.is_available():
            return []
            
        try:
            # Get top search terms with scores (search counts)
            popular_terms = self.redis_client.client.zrevrange(
                self.popular_terms_key, 0, limit - 1, withscores=True
            )
            
            return [
                {
                    'term': term.decode('utf-8') if isinstance(term, bytes) else term,
                    'search_count': int(score)
                }
                for term, score in popular_terms
            ]
            
        except Exception as e:
            logger.error(f"Error getting popular search terms: {e}")
            return []
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get cache performance statistics
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.redis_client.is_available():
            return {'status': 'redis_unavailable'}
            
        try:
            stats = {
                'redis_available': True,
                'cache_hit_rate': 0.0,
                'total_searches': 0,
                'popular_terms_count': 0,
                'search_types': {}
            }
            
            # Get cache hits and misses for different search types
            search_types = ['products', 'flowers', 'files', 'all']
            total_hits = 0
            total_misses = 0
            
            for search_type in search_types:
                hits_key = f"{self.analytics_prefix}hits:{search_type}"
                misses_key = f"{self.analytics_prefix}misses:{search_type}"
                
                hits = int(self.redis_client.client.get(hits_key) or 0)
                misses = int(self.redis_client.client.get(misses_key) or 0)
                
                total_hits += hits
                total_misses += misses
                
                stats['search_types'][search_type] = {
                    'hits': hits,
                    'misses': misses,
                    'total': hits + misses,
                    'hit_rate': hits / (hits + misses) if (hits + misses) > 0 else 0.0
                }
            
            # Calculate overall statistics
            stats['total_searches'] = total_hits + total_misses
            stats['cache_hit_rate'] = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0.0
            
            # Get popular terms count
            stats['popular_terms_count'] = self.redis_client.client.zcard(self.popular_terms_key) or 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def clear_cache(self, search_type: Optional[str] = None) -> bool:
        """
        Clear search cache
        
        Args:
            search_type: Specific search type to clear, or None for all
            
        Returns:
            True if cleared successfully
        """
        if not self.redis_client.is_available():
            return False
            
        try:
            if search_type:
                # Clear cache for specific search type
                pattern = f"{self.search_cache_prefix}{search_type}:*"
            else:
                # Clear all search cache
                pattern = f"{self.search_cache_prefix}*"
            
            # Get keys matching pattern
            keys = self.redis_client.client.keys(pattern)
            
            if keys:
                self.redis_client.client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries for pattern: {pattern}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def invalidate_search_cache(self, query: str, search_type: Optional[str] = None) -> bool:
        """
        Invalidate cache for a specific query
        
        Args:
            query: Search query to invalidate
            search_type: Specific search type, or None for all types
            
        Returns:
            True if invalidated successfully
        """
        if not self.redis_client.is_available():
            return False
            
        try:
            if search_type:
                # Invalidate for specific search type
                cache_key = self._generate_cache_key(search_type, query)
                self.redis_client.client.delete(cache_key)
            else:
                # Invalidate for all search types
                search_types = ['products', 'flowers', 'files', 'all']
                for stype in search_types:
                    cache_key = self._generate_cache_key(stype, query)
                    self.redis_client.client.delete(cache_key)
            
            logger.debug(f"Invalidated cache for query: {query}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False


# Global instance for easy access
_search_cache = None

def get_search_cache() -> RedisSearchCache:
    """Get the global search cache instance"""
    global _search_cache
    if _search_cache is None:
        _search_cache = RedisSearchCache()
    return _search_cache


# Convenience functions for direct access
def cache_search_results(search_type: str, query: str, results: List[Dict], 
                        filters: Optional[Dict] = None, ttl: Optional[int] = None) -> bool:
    """Cache search results"""
    return get_search_cache().cache_search_results(search_type, query, results, filters, ttl)


def get_cached_search(search_type: str, query: str, filters: Optional[Dict] = None) -> Optional[List[Dict]]:
    """Get cached search results"""
    return get_search_cache().get_cached_search(search_type, query, filters)


def get_popular_search_terms(limit: int = 10) -> List[Dict[str, Any]]:
    """Get popular search terms"""
    return get_search_cache().get_popular_search_terms(limit)


def get_cache_statistics() -> Dict[str, Any]:
    """Get cache statistics"""
    return get_search_cache().get_cache_statistics()


def clear_search_cache(search_type: Optional[str] = None) -> bool:
    """Clear search cache"""
    return get_search_cache().clear_cache(search_type)