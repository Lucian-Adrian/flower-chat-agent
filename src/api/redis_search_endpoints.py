"""
Redis Search API Endpoints
Provides API endpoints to demonstrate and use Redis search functionality
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from src.data.redis_enhanced_search import (
    get_enhanced_search_manager,
    search_products_cached,
    search_flowers_cached,
    search_files_cached,
    get_search_suggestions,
    get_search_stats,
    clear_search_caches
)
from src.data.redis_file_search import get_project_structure, get_file_info
from src.utils.utils import setup_logger

logger = setup_logger(__name__)

# Create router for search endpoints
search_router = APIRouter(prefix="/search", tags=["Redis Search"])


# Response models
class SearchResult(BaseModel):
    """Search result response model"""
    results: List[Dict[str, Any]]
    total_found: int
    search_time_ms: float
    cache_hit: bool
    query: str


class FileSearchResult(BaseModel):
    """File search result response model"""
    file_path: str
    filename: str
    file_type: str
    file_size: int
    total_matches: int
    matches: Dict[str, Any]


class SearchSuggestion(BaseModel):
    """Search suggestion response model"""
    suggestions: List[str]
    query: str


class SearchStats(BaseModel):
    """Search statistics response model"""
    cache_statistics: Dict[str, Any]
    popular_search_terms: List[Dict[str, Any]]
    search_engines_status: Dict[str, bool]
    redis_cache_available: bool


@search_router.get("/products", response_model=SearchResult)
async def search_products_endpoint(
    query: str = Query(..., description="Search query for products"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    budget: Optional[float] = Query(None, ge=0, description="Budget constraint in MDL"),
    category: Optional[str] = Query(None, description="Product category filter"),
    use_cache: bool = Query(True, description="Whether to use Redis cache")
):
    """
    Search for products with Redis caching
    
    This endpoint searches for flower products using the enhanced search system
    with Redis caching for improved performance.
    """
    try:
        import time
        start_time = time.time()
        
        # Get search manager
        search_manager = get_enhanced_search_manager()
        
        # Check if we can use cache to determine cache hit
        cache_hit = False
        if use_cache:
            cached_results = search_manager.redis_cache.get_cached_search(
                "products", query, {'limit': limit, 'budget': budget, 'category': category}
            )
            cache_hit = cached_results is not None
        
        # Perform search
        results = search_manager.search_products(
            query=query,
            limit=limit,
            budget=budget,
            category=category,
            use_cache=use_cache
        )
        
        search_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return SearchResult(
            results=results,
            total_found=len(results),
            search_time_ms=round(search_time, 2),
            cache_hit=cache_hit,
            query=query
        )
        
    except Exception as e:
        logger.error(f"Error in product search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@search_router.get("/flowers", response_model=SearchResult)
async def search_flowers_endpoint(
    query: str = Query(..., description="Search query for flowers"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    budget: Optional[float] = Query(None, ge=0, description="Budget constraint in MDL"),
    use_cache: bool = Query(True, description="Whether to use Redis cache")
):
    """
    Search for flowers only with Redis caching
    
    This endpoint searches specifically for flower products using Redis caching.
    """
    try:
        import time
        start_time = time.time()
        
        search_manager = get_enhanced_search_manager()
        
        # Check cache hit
        cache_hit = False
        if use_cache:
            cached_results = search_manager.redis_cache.get_cached_search(
                "flowers", query, {'limit': limit, 'budget': budget}
            )
            cache_hit = cached_results is not None
        
        results = search_manager.search_flowers_only(
            query=query,
            limit=limit,
            budget=budget,
            use_cache=use_cache
        )
        
        search_time = (time.time() - start_time) * 1000
        
        return SearchResult(
            results=results,
            total_found=len(results),
            search_time_ms=round(search_time, 2),
            cache_hit=cache_hit,
            query=query
        )
        
    except Exception as e:
        logger.error(f"Error in flower search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@search_router.get("/files")
async def search_files_endpoint(
    query: str = Query(..., description="Search query for files"),
    file_types: Optional[str] = Query(None, description="Comma-separated file extensions (e.g., '.py,.js')"),
    case_sensitive: bool = Query(False, description="Case sensitive search"),
    max_results: int = Query(50, ge=1, le=200, description="Maximum number of results"),
    use_cache: bool = Query(True, description="Whether to use Redis cache")
):
    """
    Search for files in the project with Redis caching
    
    This endpoint searches through project files and caches results in Redis.
    """
    try:
        import time
        start_time = time.time()
        
        # Parse file types
        parsed_file_types = None
        if file_types:
            parsed_file_types = [ext.strip() for ext in file_types.split(',') if ext.strip()]
        
        search_manager = get_enhanced_search_manager()
        
        # Check cache hit
        cache_hit = False
        if use_cache:
            filters = {
                'file_types': parsed_file_types,
                'case_sensitive': case_sensitive,
                'max_results': max_results
            }
            cached_results = search_manager.redis_cache.get_cached_search("files", query, filters)
            cache_hit = cached_results is not None
        
        results = search_manager.search_files(
            query=query,
            file_types=parsed_file_types,
            case_sensitive=case_sensitive,
            max_results=max_results,
            use_cache=use_cache
        )
        
        search_time = (time.time() - start_time) * 1000
        
        return {
            "results": results,
            "total_found": len(results),
            "search_time_ms": round(search_time, 2),
            "cache_hit": cache_hit,
            "query": query,
            "file_types_searched": parsed_file_types,
            "case_sensitive": case_sensitive
        }
        
    except Exception as e:
        logger.error(f"Error in file search endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@search_router.get("/suggestions", response_model=SearchSuggestion)
async def get_search_suggestions_endpoint(
    query: str = Query(..., min_length=1, description="Partial search query"),
    search_type: str = Query("products", description="Type of search (products, flowers, files)")
):
    """
    Get search suggestions based on popular terms
    
    Returns search suggestions based on popular search terms and the partial query.
    """
    try:
        search_manager = get_enhanced_search_manager()
        suggestions = search_manager.get_search_suggestions(query, search_type)
        
        return SearchSuggestion(
            suggestions=suggestions,
            query=query
        )
        
    except Exception as e:
        logger.error(f"Error in search suggestions endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@search_router.get("/stats", response_model=SearchStats)
async def get_search_statistics():
    """
    Get comprehensive search statistics
    
    Returns detailed statistics about search performance, cache hit rates,
    and popular search terms.
    """
    try:
        search_manager = get_enhanced_search_manager()
        stats = search_manager.get_comprehensive_search_stats()
        
        return SearchStats(**stats)
        
    except Exception as e:
        logger.error(f"Error in search statistics endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@search_router.get("/project-structure")
async def get_project_structure_endpoint(
    max_depth: int = Query(3, ge=1, le=10, description="Maximum directory depth")
):
    """
    Get project directory structure
    
    Returns the hierarchical structure of the project directories and files.
    """
    try:
        structure = get_project_structure(max_depth)
        return {
            "structure": structure,
            "max_depth": max_depth
        }
        
    except Exception as e:
        logger.error(f"Error in project structure endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get structure: {str(e)}")


@search_router.get("/file-info")
async def get_file_info_endpoint(
    file_path: str = Query(..., description="Path to file (relative to project root)")
):
    """
    Get detailed information about a specific file
    
    Returns detailed information about a file including size, content preview, etc.
    """
    try:
        file_info = get_file_info(file_path)
        
        if file_info is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in file info endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")


@search_router.post("/cache/clear")
async def clear_cache_endpoint(
    search_type: Optional[str] = Query(None, description="Specific search type to clear (optional)")
):
    """
    Clear search cache
    
    Clears the Redis search cache. Can clear all caches or specific search type.
    """
    try:
        search_manager = get_enhanced_search_manager()
        
        if search_type:
            success = search_manager.redis_cache.clear_cache(search_type)
            message = f"Cache cleared for search type: {search_type}"
        else:
            success = search_manager.clear_all_caches()
            message = "All search caches cleared"
        
        return {
            "success": success,
            "message": message
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@search_router.post("/cache/invalidate")
async def invalidate_cache_endpoint(
    query: str = Query(..., description="Search query to invalidate"),
    search_type: Optional[str] = Query(None, description="Specific search type (optional)")
):
    """
    Invalidate cache for specific search query
    
    Removes cached results for a specific search query.
    """
    try:
        search_manager = get_enhanced_search_manager()
        success = search_manager.invalidate_search(query, search_type)
        
        return {
            "success": success,
            "message": f"Cache invalidated for query: {query}",
            "search_type": search_type
        }
        
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to invalidate cache: {str(e)}")


# Health check endpoint for Redis search functionality
@search_router.get("/health")
async def redis_search_health_check():
    """
    Health check for Redis search functionality
    
    Returns the status of Redis search components and their availability.
    """
    try:
        search_manager = get_enhanced_search_manager()
        
        health_status = {
            "redis_cache_available": search_manager.redis_cache.redis_client.is_available(),
            "search_engines": {
                "vector_search": search_manager.vector_search is not None,
                "simplified_search": search_manager.simplified_search is not None,
                "product_search_engine": search_manager.product_search_engine is not None,
                "file_search_engine": search_manager.file_search_engine is not None
            },
            "status": "healthy"
        }
        
        # Check if core functionality is available
        if not any(health_status["search_engines"].values()):
            health_status["status"] = "degraded"
            health_status["warning"] = "No search engines available"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "redis_cache_available": False
        }