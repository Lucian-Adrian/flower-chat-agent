"""
ChromaDB Client for XOFlowers AI Agent
Simplified product search interface with AI-enhanced parameter extraction
Automatically initializes with product data from database/products.csv
"""

import logging
import asyncio
import time
import csv
from typing import List, Dict, Optional, Any
from pathlib import Path
from functools import lru_cache

from src.utils.system_definitions import get_service_config
from src.utils.utils import setup_logger

logger = setup_logger(__name__)

# Try to import ChromaDB dependencies
try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    HAS_CHROMADB = True
    logger.info("ChromaDB dependencies available")
except ImportError:
    chromadb = None
    HAS_CHROMADB = False
    logger.warning("ChromaDB dependencies not available - using fallback mode")

class ChromaDBClient:
    """
    Optimized ChromaDB client for product search with caching and connection pooling
    Provides AI-enhanced search with graceful fallback when unavailable
    """
    
    def __init__(self):
        """Initialize ChromaDB client with performance optimizations"""
        self.config = get_service_config()['chromadb']
        self.db_path = Path(self.config['path'])
        self.collection_name = self.config['collection_name']
        
        # Client state
        self.client = None
        self.collection = None
        self.initialized = False
        
        # Performance optimizations: Query result caching
        self._query_cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL for search results
        
        # Performance optimizations: Connection pooling with semaphore
        self._query_semaphore = asyncio.Semaphore(5)  # Limit concurrent queries
        
        # Initialize with graceful degradation
        if HAS_CHROMADB:
            self._initialize_client()
        else:
            logger.warning("ChromaDB dependencies not available - using graceful degradation mode")
            self.initialized = False
    
    def _initialize_client(self) -> None:
        """
        Initialize ChromaDB client and collection with automatic data loading
        """
        try:
            # Ensure database directory exists
            self.db_path.mkdir(parents=True, exist_ok=True)
            
            # Create ChromaDB client with proper settings
            self.client = chromadb.PersistentClient(path=str(self.db_path))
            logger.info(f"ChromaDB client created at: {self.db_path}")
            
            # Create embedding function for product search (optimized for faster loading)
            embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2",
                device="cpu",  # Force CPU to avoid GPU detection delays
                normalize_embeddings=True  # Normalize for better similarity scores
            )
            logger.info("Embedding function initialized with optimizations")
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
                logger.info(f"Connected to existing ChromaDB collection: {self.collection_name}")
                
                # Check if collection has data
                collection_count = self.collection.count()
                if collection_count == 0:
                    logger.info("Collection is empty - loading product data...")
                    self._load_product_data()
                else:
                    logger.info(f"Collection has {collection_count} products loaded")
                    
            except Exception as collection_error:
                # Collection doesn't exist - create it and load data
                logger.info(f"Collection not found: {collection_error}")
                logger.info(f"Creating new ChromaDB collection: {self.collection_name}")
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_function
                )
                logger.info("Collection created successfully")
                self._load_product_data()
            
            self.initialized = True
            logger.info(f"ChromaDB client initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            logger.error(f"Error details: {type(e).__name__}: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            self.initialized = False
            
    def _load_product_data(self) -> None:
        """Load product data from src/database/products.csv into ChromaDB"""
        try:
            # Try multiple possible locations for the products file
            possible_paths = [
                Path("src/database/products.csv"),
                Path("database/products.csv"),
                Path("../database/products.csv")
            ]
            
            products_file = None
            for path in possible_paths:
                if path.exists():
                    products_file = path
                    break
                    
            if not products_file:
                logger.error(f"Products file not found in any of: {[str(p) for p in possible_paths]}")
                logger.info("Expected file structure: CSV with product data")
                return
                
            logger.info(f"Loading product data from: {products_file}")
            products_data = []
            
            with open(products_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                headers = reader.fieldnames
                logger.info(f"CSV headers found: {headers}")
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Skip non-product entries
                        if row.get('chunk_type') != 'product':
                            continue
                            
                        # Skip products that don't exist
                        if row.get('product_exists', 'True').lower() != 'true':
                            continue
                            
                        # Extract product information from the current CSV structure
                        chunk_id = row.get('chunk_id', f'product_{row_num}')
                        primary_text = row.get('primary_text', '')
                        category = row.get('category', 'flori')
                        price_str = row.get('price', '0')
                        flower_type = row.get('flower_type', '')
                        url = row.get('url', '')
                        
                        # Parse price safely
                        try:
                            price = float(price_str) if price_str else 0.0
                        except (ValueError, TypeError):
                            price = 0.0
                            
                        # Create searchable text from available data
                        searchable_text = f"{primary_text} {category} {flower_type}".strip()
                        
                        # Extract product name from primary_text (first part before comma or dash)
                        name_parts = primary_text.split(' - ')
                        product_name = name_parts[0].strip() if name_parts else primary_text[:50]
                        
                        # Extract description (remaining part)
                        description = name_parts[1].strip() if len(name_parts) > 1 else primary_text
                        
                        products_data.append({
                            'id': chunk_id,
                            'document': searchable_text,
                            'metadata': {
                                'id': chunk_id,
                                'nume': product_name,
                                'descriere': description,
                                'pret': price,
                                'categorie': category,
                                'culoare': '',  # Not available in current CSV
                                'material': '',  # Not available in current CSV
                                'disponibil': True,  # Assume available if product exists
                                'imagine_url': '',  # Not available in current CSV
                                'flower_type': flower_type,
                                'url': url,
                                'primary_text': primary_text
                            }
                        })
                    except Exception as row_error:
                        logger.warning(f"Error processing row {row_num}: {row_error}")
                        continue
                    
            if products_data:
                logger.info(f"Processed {len(products_data)} valid products")
                
                # Add products to ChromaDB collection in batches
                batch_size = 100
                for i in range(0, len(products_data), batch_size):
                    batch = products_data[i:i + batch_size]
                    ids = [item['id'] for item in batch]
                    documents = [item['document'] for item in batch]
                    metadatas = [item['metadata'] for item in batch]
                    
                    self.collection.add(
                        ids=ids,
                        documents=documents,
                        metadatas=metadatas
                    )
                    logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} products")
                
                logger.info(f"Successfully loaded {len(products_data)} products into ChromaDB")
            else:
                logger.warning("No valid product data found in CSV file")
                
        except Exception as e:
            logger.error(f"Error loading product data: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _generate_cache_key(self, query: str, filters: Dict[str, Any] = None, max_results: int = 5) -> str:
        """Generate cache key for query results"""
        content = f"{query}:{max_results}"
        if filters:
            content += f":{str(sorted(filters.items()))}"
        return f"chromadb:{hash(content)}"
    
    def _get_cached_results(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached query results if available and not expired"""
        if cache_key in self._query_cache:
            cached_item = self._query_cache[cache_key]
            if time.time() - cached_item['timestamp'] < self._cache_ttl:
                return cached_item['results']
            else:
                # Remove expired cache entry
                del self._query_cache[cache_key]
        return None
    
    def _cache_results(self, cache_key: str, results: List[Dict[str, Any]]) -> None:
        """Cache query results with timestamp"""
        self._query_cache[cache_key] = {
            'results': results,
            'timestamp': time.time()
        }
        
        # Clean up old cache entries periodically
        if len(self._query_cache) > 50:  # Limit cache size
            self._cleanup_cache()
    
    def _cleanup_cache(self) -> None:
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self._query_cache.items()
            if current_time - value['timestamp'] > self._cache_ttl
        ]
        
        for key in expired_keys:
            del self._query_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired ChromaDB cache entries")

    async def search_products(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for products using natural language query with caching and connection pooling
        
        Args:
            query: Natural language search query
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of product results with metadata
        """
        # Check cache first
        cache_key = self._generate_cache_key(query, None, max_results)
        cached_results = self._get_cached_results(cache_key)
        if cached_results:
            logger.debug(f"Using cached results for query: {query}")
            return cached_results
        
        async with self._query_semaphore:  # Connection pooling
            try:
                # Check if ChromaDB is available and collection is initialized
                if not self.is_available() or not self.collection:
                    logger.warning("ChromaDB not available - initializing fallback")
                    return self._get_fallback_products(query, max_results)
                
                # Perform vector search
                results = await asyncio.to_thread(
                    self.collection.query,
                    query_texts=[query],
                    n_results=max_results
                )
                
                # Format results
                formatted_results = self._format_search_results(results)
                
                # Cache results
                self._cache_results(cache_key, formatted_results)
                
                logger.info(f"ChromaDB search completed: {len(formatted_results)} results for query '{query}'")
                return formatted_results
                
            except Exception as e:
                logger.error(f"Error during ChromaDB search: {e}")
                # Return fallback results instead of raising exception
                logger.info("Falling back to mock product data")
                return self._get_fallback_products(query, max_results)
    
    async def search_products_with_filters(self, query: str, filters: Dict[str, Any], max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for products with additional filters using caching and connection pooling
        
        Args:
            query: Natural language search query
            filters: Dictionary of filters (e.g., {'category': 'roses', 'price_max': 500})
            max_results: Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: List of filtered product results
        """
        # Check cache first
        cache_key = self._generate_cache_key(query, filters, max_results)
        cached_results = self._get_cached_results(cache_key)
        if cached_results:
            logger.debug(f"Using cached filtered results for query: {query}")
            return cached_results
        
        async with self._query_semaphore:  # Connection pooling
            try:
                # ChromaDB is REQUIRED - no fallback allowed
                if not self.is_available():
                    raise Exception("ChromaDB not available - system requires ChromaDB for product search")
                
                # Extract price filters for application-level filtering
                price_min = filters.get('price_min')
                price_max = filters.get('price_max')
                
                # Build where clause without complex price filters
                simple_filters = {k: v for k, v in filters.items() if k not in ['price_min', 'price_max']}
                where_clause = self._build_where_clause(simple_filters) if simple_filters else None
                
                # Get more results for filtering
                search_limit = max_results * 3 if price_min or price_max else max_results
                
                # Perform search
                if where_clause:
                    results = await asyncio.to_thread(
                        self.collection.query,
                        query_texts=[query],
                        n_results=search_limit,
                        where=where_clause
                    )
                else:
                    results = await asyncio.to_thread(
                        self.collection.query,
                        query_texts=[query],
                        n_results=search_limit
                    )
                
                formatted_results = self._format_search_results(results)
                
                # Apply price filtering at application level
                if price_min is not None or price_max is not None:
                    filtered_results = []
                    for result in formatted_results:
                        price = result.get('price', 0)
                        if price_min is not None and price < price_min:
                            continue
                        if price_max is not None and price > price_max:
                            continue
                        filtered_results.append(result)
                    formatted_results = filtered_results[:max_results]
                
                # Cache results
                self._cache_results(cache_key, formatted_results)
                
                logger.info(f"ChromaDB filtered search completed: {len(formatted_results)} results")
                return formatted_results
                
            except Exception as e:
                logger.error(f"Error during filtered ChromaDB search: {e}")
                raise Exception(f"ChromaDB filtered search failed - system requires ChromaDB: {e}")
    
    def _format_search_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format ChromaDB search results into standardized format
        
        Args:
            results: Raw ChromaDB query results
            
        Returns:
            List[Dict[str, Any]]: Formatted results
        """
        formatted_results = []
        
        if not results['documents'] or not results['documents'][0]:
            return formatted_results
        
        for i in range(len(results['documents'][0])):
            result = {
                'id': results['ids'][0][i] if results['ids'] else f"result_{i}",
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'similarity_score': 1 - results['distances'][0][i] if results.get('distances') else 0.0
            }
            
            # Extract product information from metadata (matching CSV structure)
            metadata = result['metadata']
            result.update({
                'name': metadata.get('nume', 'Produs floral'),
                'price': metadata.get('pret', 0),
                'category': metadata.get('categorie', 'flori'),
                'description': metadata.get('descriere', result['text']),
                'availability': metadata.get('disponibil', True),
                'image_url': metadata.get('imagine_url', ''),
                'color': metadata.get('culoare', ''),
                'material': metadata.get('material', ''),
                'url': metadata.get('url', '')  # Add URL to formatted results
            })
            
            formatted_results.append(result)
        
        return formatted_results
    
    def _get_fallback_products(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get fallback products from CSV data when ChromaDB is not available
        """
        try:
            # Try multiple possible locations for the products file
            possible_paths = [
                Path("src/database/products.csv"),
                Path("database/products.csv"),
                Path("../database/products.csv")
            ]
            
            products_file = None
            for path in possible_paths:
                if path.exists():
                    products_file = path
                    break
                    
            if not products_file:
                logger.warning(f"Products file not found in any of: {[str(p) for p in possible_paths]}")
                return []
                
            fallback_products = []
            with open(products_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Skip non-product entries
                    if row.get('chunk_type') != 'product':
                        continue
                        
                    # Skip products that don't exist
                    if row.get('product_exists', 'True').lower() != 'true':
                        continue
                    
                    # Simple text matching for fallback
                    primary_text = row.get('primary_text', '')
                    category = row.get('category', '')
                    flower_type = row.get('flower_type', '')
                    searchable_text = f"{primary_text} {category} {flower_type}".lower()
                    query_lower = query.lower()
                    
                    if any(word in searchable_text for word in query_lower.split()):
                        # Extract product information
                        chunk_id = row.get('chunk_id', '')
                        price_str = row.get('price', '0')
                        url = row.get('url', '')
                        
                        try:
                            price = float(price_str) if price_str else 0.0
                        except (ValueError, TypeError):
                            price = 0.0
                            
                        # Extract product name from primary_text
                        name_parts = primary_text.split(' - ')
                        product_name = name_parts[0].strip() if name_parts else primary_text[:50]
                        description = name_parts[1].strip() if len(name_parts) > 1 else primary_text
                        
                        fallback_products.append({
                            'id': chunk_id,
                            'name': product_name,
                            'price': price,
                            'category': category,
                            'description': description,
                            'availability': True,
                            'image_url': '',
                            'color': '',
                            'material': '',
                            'flower_type': flower_type,
                            'url': url,
                            'similarity_score': 0.5,  # Default fallback score
                            'text': primary_text,
                            'metadata': {
                                'id': chunk_id,
                                'nume': product_name,
                                'pret': price,
                                'categorie': category,
                                'descriere': description,
                                'disponibil': True,
                                'imagine_url': '',
                                'culoare': '',
                                'material': '',
                                'flower_type': flower_type,
                                'url': url,
                                'primary_text': primary_text
                            }
                        })
                        
                        if len(fallback_products) >= max_results:
                            break
                            
            logger.info(f"Fallback search returned {len(fallback_products)} products for query '{query}'")
            return fallback_products
            
        except Exception as e:
            logger.error(f"Error in fallback product search: {e}")
            return []
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Build ChromaDB where clause from filters
        
        Args:
            filters: Dictionary of filters
            
        Returns:
            Optional[Dict[str, Any]]: ChromaDB where clause or None
        """
        where_clause = {}
        
        # Handle filters one by one - ChromaDB doesn't support complex $and operations
        for filter_key, filter_value in filters.items():
            if filter_key == 'price_min':
                where_clause['pret'] = {"$gte": filter_value}
            elif filter_key == 'price_max':
                # If both min and max are specified, we need to handle this differently
                if 'pret' in where_clause:
                    # For range queries, we need to use multiple where clauses
                    # ChromaDB limitation: combine min/max in application logic
                    existing_min = where_clause['pret'].get("$gte", 0)
                    where_clause['pret'] = {"$gte": existing_min, "$lte": filter_value}
                else:
                    where_clause['pret'] = {"$lte": filter_value}
            elif filter_key == 'category':
                where_clause['categorie'] = filter_value
            elif filter_key == 'color':
                where_clause['culoare'] = {"$contains": filter_value}
            elif filter_key == 'available':
                where_clause['disponibil'] = filter_value
        
        return where_clause if where_clause else None
    

    
    def is_available(self) -> bool:
        """
        Check if ChromaDB is available and properly initialized
        
        Returns:
            bool: True if ChromaDB is available, False otherwise
        """
        return HAS_CHROMADB and self.initialized and self.collection is not None
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the product collection
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        if not self.is_available():
            return {
                'available': False,
                'reason': 'ChromaDB not available or not initialized',
                'fallback_mode': True
            }
        
        try:
            count = self.collection.count()
            return {
                'available': True,
                'collection_name': self.collection_name,
                'document_count': count,
                'db_path': str(self.db_path),
                'fallback_mode': False
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                'available': False,
                'error': str(e),
                'fallback_mode': True
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on ChromaDB connection
        
        Returns:
            Dict[str, Any]: Health check results
        """
        health_status = {
            'chromadb_available': HAS_CHROMADB,
            'client_initialized': self.initialized,
            'collection_available': self.collection is not None,
            'db_path': str(self.db_path),
            'collection_name': self.collection_name
        }
        
        if self.is_available():
            try:
                # Test a simple query
                test_results = self.collection.query(
                    query_texts=["test"],
                    n_results=1
                )
                health_status['status'] = 'healthy'
                health_status['test_query_success'] = True
            except Exception as e:
                health_status['status'] = 'error'
                health_status['error'] = str(e)
                health_status['test_query_success'] = False
        else:
            health_status['status'] = 'unavailable'
            health_status['fallback_mode'] = True
        
        return health_status

# Global instance for easy access
chromadb_client = ChromaDBClient()

# Convenience functions for direct access
async def search_products(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Search for products using natural language query"""
    return await chromadb_client.search_products(query, max_results)

async def search_products_with_filters(query: str, filters: Dict[str, Any], max_results: int = 5) -> List[Dict[str, Any]]:
    """Search for products with additional filters"""
    return await chromadb_client.search_products_with_filters(query, filters, max_results)

def is_chromadb_available() -> bool:
    """Check if ChromaDB is available"""
    return chromadb_client.is_available()

def get_product_search_stats() -> Dict[str, Any]:
    """Get ChromaDB collection statistics"""
    return chromadb_client.get_collection_stats()

def health_check_chromadb() -> Dict[str, Any]:
    """Perform ChromaDB health check"""
    return chromadb_client.health_check()

async def test_chromadb_connection() -> bool:
    """Test ChromaDB connection for health checks"""
    try:
        return chromadb_client.is_available()
    except Exception:
        return False