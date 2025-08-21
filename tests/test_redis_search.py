"""
Tests for Redis-based search functionality
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.data.redis_search_cache import RedisSearchCache, get_search_cache
from src.data.redis_file_search import FileSearchEngine, get_file_search_engine
from src.data.redis_enhanced_search import EnhancedSearchManager, get_enhanced_search_manager


class TestRedisSearchCache:
    """Test Redis search cache functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Mock Redis client for testing
        self.mock_redis_client = Mock()
        self.mock_redis_client.is_available.return_value = True
        self.mock_redis_client.client = Mock()
        
        self.cache = RedisSearchCache(redis_client=self.mock_redis_client)
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        key1 = self.cache._generate_cache_key("products", "flowers", {"budget": 100})
        key2 = self.cache._generate_cache_key("products", "flowers", {"budget": 100})
        key3 = self.cache._generate_cache_key("products", "flowers", {"budget": 200})
        
        # Same parameters should generate same key
        assert key1 == key2
        # Different parameters should generate different keys
        assert key1 != key3
        # Key should contain type and prefix
        assert "xoflowers:search:products:" in key1
    
    def test_cache_search_results(self):
        """Test caching search results"""
        self.mock_redis_client.client.setex.return_value = True
        self.mock_redis_client.client.zincrby.return_value = 1
        self.mock_redis_client.client.expire.return_value = True
        
        results = [{"name": "Red Roses", "price": 100}]
        success = self.cache.cache_search_results("products", "roses", results)
        
        assert success
        self.mock_redis_client.client.setex.assert_called_once()
        self.mock_redis_client.client.zincrby.assert_called_once()
    
    def test_get_cached_search_hit(self):
        """Test cache hit scenario"""
        cached_data = {
            "results": [{"name": "Red Roses", "price": 100}],
            "query": "roses",
            "cached_at": "2024-01-01T00:00:00"
        }
        self.mock_redis_client.client.get.return_value = json.dumps(cached_data)
        self.mock_redis_client.client.incr.return_value = 1
        
        results = self.cache.get_cached_search("products", "roses")
        
        assert results is not None
        assert len(results) == 1
        assert results[0]["name"] == "Red Roses"
        self.mock_redis_client.client.get.assert_called_once()
    
    def test_get_cached_search_miss(self):
        """Test cache miss scenario"""
        self.mock_redis_client.client.get.return_value = None
        self.mock_redis_client.client.incr.return_value = 1
        
        results = self.cache.get_cached_search("products", "roses")
        
        assert results is None
        self.mock_redis_client.client.get.assert_called_once()
    
    def test_redis_unavailable(self):
        """Test behavior when Redis is unavailable"""
        self.mock_redis_client.is_available.return_value = False
        
        # Should return None when Redis unavailable
        results = self.cache.get_cached_search("products", "roses")
        assert results is None
        
        # Should return False when trying to cache
        success = self.cache.cache_search_results("products", "roses", [])
        assert success is False
    
    def test_popular_search_terms(self):
        """Test popular search terms functionality"""
        mock_terms = [
            (b"roses", 10.0),
            (b"flowers", 8.0),
            (b"wedding", 5.0)
        ]
        self.mock_redis_client.client.zrevrange.return_value = mock_terms
        
        popular_terms = self.cache.get_popular_search_terms(3)
        
        assert len(popular_terms) == 3
        assert popular_terms[0]["term"] == "roses"
        assert popular_terms[0]["search_count"] == 10
    
    def test_cache_statistics(self):
        """Test cache statistics collection"""
        # Mock Redis responses for statistics
        self.mock_redis_client.client.get.side_effect = lambda key: {
            "xoflowers:search_analytics:hits:products": "50",
            "xoflowers:search_analytics:misses:products": "10",
            "xoflowers:search_analytics:hits:flowers": "30",
            "xoflowers:search_analytics:misses:flowers": "5"
        }.get(key, "0")
        
        self.mock_redis_client.client.zcard.return_value = 25
        
        stats = self.cache.get_cache_statistics()
        
        assert stats["redis_available"] is True
        assert stats["total_searches"] == 95  # 50+10+30+5
        assert stats["cache_hit_rate"] > 0.8  # Should be around 0.84
        assert stats["popular_terms_count"] == 25
    
    def test_clear_cache(self):
        """Test cache clearing functionality"""
        self.mock_redis_client.client.keys.return_value = ["key1", "key2", "key3"]
        self.mock_redis_client.client.delete.return_value = 3
        
        success = self.cache.clear_cache("products")
        
        assert success is True
        self.mock_redis_client.client.keys.assert_called_once()
        self.mock_redis_client.client.delete.assert_called_once()


class TestFileSearchEngine:
    """Test file search engine functionality"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary directory with test files
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        
        # Create test files
        (self.test_dir / "test.py").write_text("def search_function():\n    return 'hello world'\n")
        (self.test_dir / "test.js").write_text("function search() {\n    console.log('hello');\n}")
        (self.test_dir / "README.md").write_text("# Search Documentation\nThis is a test file")
        
        # Create subdirectory
        sub_dir = self.test_dir / "subdir"
        sub_dir.mkdir()
        (sub_dir / "nested.py").write_text("class SearchClass:\n    pass")
        
        # Mock Redis cache
        self.mock_cache = Mock()
        self.mock_cache.get_cached_search.return_value = None
        self.mock_cache.cache_search_results.return_value = True
        
        self.file_search = FileSearchEngine(base_path=str(self.test_dir), redis_cache=self.mock_cache)
    
    def teardown_method(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_search_files_content(self):
        """Test searching file content"""
        results = self.file_search.search_files("hello", max_results=10)
        
        assert len(results) >= 2  # Should find in test.py and test.js
        
        # Check that results contain expected information
        for result in results:
            assert "file_path" in result
            assert "matches" in result
            assert "total_matches" in result
            
        # Verify cache was called
        self.mock_cache.get_cached_search.assert_called_once()
        self.mock_cache.cache_search_results.assert_called_once()
    
    def test_search_files_filename(self):
        """Test searching filenames"""
        results = self.file_search.search_files("README", max_results=10)
        
        assert len(results) >= 1
        
        # Should find README.md
        readme_result = next((r for r in results if "README" in r["filename"]), None)
        assert readme_result is not None
        assert readme_result["matches"]["filename"] is not None
    
    def test_search_by_file_type(self):
        """Test searching by file type"""
        results = self.file_search.search_by_file_type(".py", limit=10)
        
        assert len(results) >= 2  # test.py and nested.py
        
        for result in results:
            assert result["file_type"] == ".py"
            assert result["filename"].endswith(".py")
    
    def test_get_file_info(self):
        """Test getting file information"""
        file_info = self.file_search.get_file_info("test.py")
        
        assert file_info is not None
        assert file_info["filename"] == "test.py"
        assert file_info["file_type"] == ".py"
        assert file_info["line_count"] > 0
        assert "content_preview" in file_info
    
    def test_get_project_structure(self):
        """Test getting project structure"""
        structure = self.file_search.get_project_structure(max_depth=2)
        
        assert structure["type"] == "directory"
        assert "children" in structure
        assert len(structure["children"]) > 0
        
        # Should contain our test files
        children_names = list(structure["children"].keys())
        assert "test.py" in children_names or any("test.py" in name for name in children_names)
    
    def test_case_sensitive_search(self):
        """Test case sensitive search"""
        # Create a file with mixed case content
        (self.test_dir / "case_test.txt").write_text("Hello WORLD hello")
        
        # Case insensitive search (default)
        results_insensitive = self.file_search.search_files("HELLO", case_sensitive=False)
        
        # Case sensitive search
        results_sensitive = self.file_search.search_files("HELLO", case_sensitive=True)
        
        # Should find the file in both cases, but different number of matches
        assert len(results_insensitive) > 0
        assert len(results_sensitive) > 0


class TestEnhancedSearchManager:
    """Test enhanced search manager"""
    
    def setup_method(self):
        """Set up test environment"""
        self.mock_cache = Mock()
        self.mock_cache.get_cached_search.return_value = None
        self.mock_cache.cache_search_results.return_value = True
        self.mock_cache.get_popular_search_terms.return_value = [
            {"term": "roses", "search_count": 10},
            {"term": "flowers", "search_count": 8}
        ]
        
        self.search_manager = EnhancedSearchManager(redis_cache=self.mock_cache)
    
    @patch('src.data.redis_enhanced_search.universal_search')
    def test_search_products_with_vector_search(self, mock_vector_search):
        """Test product search using vector search"""
        mock_vector_search.smart_search.return_value = [
            {"name": "Red Roses", "price": 100},
            {"name": "White Roses", "price": 120}
        ]
        
        # Mock the property to return our mock
        with patch.object(self.search_manager, 'vector_search', mock_vector_search):
            results = self.search_manager.search_products("roses", limit=5)
        
        assert len(results) == 2
        assert results[0]["name"] == "Red Roses"
        mock_vector_search.smart_search.assert_called_once_with("roses", 5)
    
    @patch('src.data.redis_enhanced_search.universal_search')
    def test_search_with_budget(self, mock_vector_search):
        """Test search with budget constraint"""
        mock_vector_search.search_budget_flowers.return_value = [
            {"name": "Budget Roses", "price": 80}
        ]
        
        with patch.object(self.search_manager, 'vector_search', mock_vector_search):
            results = self.search_manager.search_products("roses", budget=100)
        
        assert len(results) == 1
        mock_vector_search.search_budget_flowers.assert_called_once_with(100, "roses", 10)
    
    def test_search_suggestions(self):
        """Test search suggestions functionality"""
        suggestions = self.search_manager.get_search_suggestions("ros", "products")
        
        assert isinstance(suggestions, list)
        # Should include "roses" from popular terms
        assert "roses" in suggestions
    
    def test_cache_integration(self):
        """Test cache integration"""
        # Mock cached results
        cached_results = [{"name": "Cached Roses", "price": 90}]
        self.mock_cache.get_cached_search.return_value = cached_results
        
        results = self.search_manager.search_products("roses")
        
        assert results == cached_results
        self.mock_cache.get_cached_search.assert_called_once()
        # Should not call cache_search_results since we got cached results
        self.mock_cache.cache_search_results.assert_not_called()
    
    def test_comprehensive_stats(self):
        """Test comprehensive statistics"""
        self.mock_cache.get_cache_statistics.return_value = {
            "redis_available": True,
            "cache_hit_rate": 0.85,
            "total_searches": 100
        }
        self.mock_cache.redis_client.is_available.return_value = True
        
        stats = self.search_manager.get_comprehensive_search_stats()
        
        assert "cache_statistics" in stats
        assert "popular_search_terms" in stats
        assert "search_engines_status" in stats
        assert stats["redis_cache_available"] is True


@pytest.mark.asyncio
class TestRedisSearchIntegration:
    """Integration tests for Redis search functionality"""
    
    def setup_method(self):
        """Set up integration test environment"""
        # Use real Redis client but mock the actual Redis server calls
        from src.data.redis_client import RedisClient
        
        self.redis_client = RedisClient()
        # Mock the client to avoid needing actual Redis server
        self.redis_client.client = Mock()
        self.redis_client.initialized = True
        
    def test_end_to_end_search_flow(self):
        """Test complete search flow from query to cached results"""
        # Mock Redis responses
        self.redis_client.client.get.return_value = None  # Cache miss first
        self.redis_client.client.setex.return_value = True
        self.redis_client.client.zincrby.return_value = 1
        self.redis_client.client.expire.return_value = True
        self.redis_client.client.incr.return_value = 1
        
        # Create cache with mocked Redis client
        cache = RedisSearchCache(redis_client=self.redis_client)
        
        # Test cache miss -> search -> cache store
        results = cache.get_cached_search("products", "test_query")
        assert results is None  # Cache miss
        
        # Simulate storing results
        test_results = [{"name": "Test Product", "price": 100}]
        success = cache.cache_search_results("products", "test_query", test_results)
        assert success is True
        
        # Verify Redis calls
        self.redis_client.client.get.assert_called()
        self.redis_client.client.setex.assert_called()
        self.redis_client.client.zincrby.assert_called()
    
    def test_fallback_when_redis_unavailable(self):
        """Test system behavior when Redis is unavailable"""
        self.redis_client.is_available = Mock(return_value=False)
        
        cache = RedisSearchCache(redis_client=self.redis_client)
        
        # Should handle gracefully when Redis unavailable
        results = cache.get_cached_search("products", "test")
        assert results is None
        
        success = cache.cache_search_results("products", "test", [])
        assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])