"""
Redis Search Functionality Demo
Demonstrates the Redis-based search capabilities for the XOFlowers chat agent
"""

import json
from pathlib import Path

from src.data.redis_search_cache import RedisSearchCache
from src.data.redis_file_search import FileSearchEngine
from src.data.redis_enhanced_search import EnhancedSearchManager
from src.utils.utils import setup_logger

logger = setup_logger(__name__)


def demo_redis_search_functionality():
    """Demonstrate the Redis search functionality"""
    
    print("🔍 Redis Search Functionality Demo")
    print("=" * 50)
    
    # 1. Demo Redis Search Cache
    print("\n1. Redis Search Cache Demo")
    print("-" * 30)
    
    cache = RedisSearchCache()
    print(f"✓ Redis available: {cache.redis_client.is_available()}")
    
    # Test caching some sample search results
    sample_results = [
        {"name": "Red Roses Bouquet", "price": 450, "category": "flowers"},
        {"name": "White Roses", "price": 380, "category": "flowers"},
        {"name": "Mixed Flowers", "price": 320, "category": "bouquets"}
    ]
    
    # Cache the results
    cache_success = cache.cache_search_results(
        search_type="products",
        query="roses",
        results=sample_results,
        filters={"budget": 500}
    )
    print(f"✓ Cached sample results: {cache_success}")
    
    # Try to retrieve from cache
    cached_results = cache.get_cached_search(
        search_type="products",
        query="roses",
        filters={"budget": 500}
    )
    
    if cached_results:
        print(f"✓ Retrieved {len(cached_results)} cached results")
    else:
        print("○ No cached results (Redis unavailable - using fallback)")
    
    # Get cache statistics
    stats = cache.get_cache_statistics()
    print(f"✓ Cache stats: {json.dumps(stats, indent=2)}")
    
    # 2. Demo File Search Engine
    print("\n2. File Search Engine Demo")
    print("-" * 30)
    
    file_search = FileSearchEngine()
    print(f"✓ Base path: {file_search.base_path}")
    
    # Search for Python files containing "redis"
    redis_files = file_search.search_files("redis", file_types=[".py"], max_results=5)
    print(f"✓ Found {len(redis_files)} Python files containing 'redis':")
    
    for file in redis_files[:3]:  # Show first 3
        print(f"  - {file['file_path']} ({file['total_matches']} matches)")
    
    # Search for all Python files
    python_files = file_search.search_by_file_type(".py", limit=5)
    print(f"✓ Found {len(python_files)} Python files in total")
    
    # Get info about a specific file
    if python_files:
        file_info = file_search.get_file_info(python_files[0]['file_path'])
        if file_info:
            print(f"✓ File info for {file_info['filename']}: {file_info['file_size']} bytes")
    
    # 3. Demo Enhanced Search Manager
    print("\n3. Enhanced Search Manager Demo")
    print("-" * 30)
    
    search_manager = EnhancedSearchManager()
    print("✓ Enhanced Search Manager initialized")
    
    # Test search suggestions
    suggestions = search_manager.get_search_suggestions("search", "files")
    print(f"✓ Search suggestions for 'search': {suggestions}")
    
    # Test file search through enhanced manager
    enhanced_file_results = search_manager.search_files("function", file_types=[".py"], max_results=3)
    print(f"✓ Enhanced file search found {len(enhanced_file_results)} files with 'function'")
    
    # Get comprehensive stats
    comprehensive_stats = search_manager.get_comprehensive_search_stats()
    print(f"✓ Search engines status:")
    if 'search_engines_status' in comprehensive_stats:
        for engine, status in comprehensive_stats['search_engines_status'].items():
            print(f"  - {engine}: {'✓' if status else '○'}")
    
    # 4. Demo Search Performance
    print("\n4. Search Performance Demo")
    print("-" * 30)
    
    import time
    
    # Time file search
    start_time = time.time()
    performance_results = file_search.search_files("import", file_types=[".py"], max_results=10)
    search_time = time.time() - start_time
    
    print(f"✓ File search for 'import' took {search_time:.3f}s")
    print(f"✓ Found {len(performance_results)} files with 'import'")
    
    # Show cache effectiveness
    if cache.redis_client.is_available():
        print("✓ Redis caching is active - subsequent searches will be faster")
    else:
        print("○ Redis unavailable - searches use direct file system access")
    
    print("\n" + "=" * 50)
    print("🎉 Redis Search Demo completed successfully!")
    print("\nKey Features Demonstrated:")
    print("• Redis-based search result caching")
    print("• File content and filename searching")
    print("• Search performance optimization")
    print("• Graceful fallback when Redis unavailable")
    print("• Search analytics and popular terms tracking")
    print("• Multiple search engine integration")


if __name__ == "__main__":
    demo_redis_search_functionality()