"""
ChromaDB Manager for XOFlowers Conversational AI
Handles vector database operations for semantic product search
"""

import os
import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    HAS_CHROMADB = True
except ImportError:
    chromadb = None
    SentenceTransformer = None
    HAS_CHROMADB = False


@dataclass
class Product:
    """Product data model for ChromaDB storage"""
    id: str
    name: str
    description: str
    price: float
    category: str
    colors: List[str]
    occasions: List[str]
    availability: bool = True
    image_url: Optional[str] = None
    
    def to_search_document(self) -> str:
        """Convert product to rich document for vectorization"""
        colors_text = ", ".join(self.colors) if self.colors else "diverse culori"
        occasions_text = ", ".join(self.occasions) if self.occasions else "orice ocazie"
        
        return f"""
        {self.name}
        Descriere: {self.description}
        Categorie: {self.category}
        Culori disponibile: {colors_text}
        Perfect pentru: {occasions_text}
        Preț: {self.price} MDL
        Disponibilitate: {"Disponibil" if self.availability else "Indisponibil"}
        Context: Flori proaspete de la XOFlowers Chișinău, Moldova
        """.strip()


class ChromaDBManager:
    """
    Advanced ChromaDB manager for conversational AI
    Handles semantic search and product vectorization
    """
    
    def __init__(self, db_path: str = "./chroma_db_flowers"):
        """
        Initialize ChromaDB manager
        
        Args:
            db_path: Path to ChromaDB database
        """
        self.db_path = db_path
        self.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        # Initialize components
        self.client = None
        self.embedding_model = None
        self.collections = {}
        self.initialized = False
        
        # Collection names for different product types
        self.collection_names = {
            'products_main': 'products_main',
            'products_bouquets': 'products_bouquets', 
            'products_boxes': 'products_boxes',
            'products_plants': 'products_plants',
            'products_occasions': 'products_occasions'
        }
        
        if HAS_CHROMADB:
            self._initialize()
        else:
            logger.error("❌ ChromaDB not available. Install with: pip install chromadb sentence-transformers")
    
    def _initialize(self):
        """Initialize ChromaDB client and embedding model"""
        try:
            # Initialize ChromaDB client with proper settings
            self.client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            # Initialize collections
            self._initialize_collections()
            
            self.initialized = True
            logger.info(f"✅ ChromaDB initialized successfully at {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            self.initialized = False
    
    def _initialize_collections(self):
        """Initialize all required collections"""
        for collection_key, collection_name in self.collection_names.items():
            try:
                # Try to get existing collection
                collection = self.client.get_collection(name=collection_name)
                self.collections[collection_key] = collection
                logger.info(f"✅ Loaded existing collection: {collection_name}")
            except Exception:
                # Create new collection if it doesn't exist
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": f"XOFlowers {collection_key} collection"}
                )
                self.collections[collection_key] = collection
                logger.info(f"✅ Created new collection: {collection_name}")
    
    def add_products(self, products: List[Product], collection_key: str = 'products_main'):
        """
        Add products to a specific collection
        
        Args:
            products: List of Product objects
            collection_key: Collection to add products to
        """
        if not self.initialized:
            logger.error("❌ ChromaDB not initialized")
            return False
        
        if collection_key not in self.collections:
            logger.error(f"❌ Collection {collection_key} not found")
            return False
        
        collection = self.collections[collection_key]
        
        try:
            # Prepare data for insertion
            ids = []
            documents = []
            metadatas = []
            
            for product in products:
                ids.append(product.id)
                documents.append(product.to_search_document())
                metadatas.append({
                    'name': product.name,
                    'price': product.price,
                    'category': product.category,
                    'colors': json.dumps(product.colors),
                    'occasions': json.dumps(product.occasions),
                    'availability': product.availability,
                    'image_url': product.image_url or ""
                })
            
            # Add to collection
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ Added {len(products)} products to {collection_key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding products to {collection_key}: {e}")
            return False
    
    def search_products(self, 
                       query: str, 
                       collection_key: str = 'products_main',
                       n_results: int = 5,
                       filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for products using semantic similarity
        
        Args:
            query: Natural language search query
            collection_key: Collection to search in
            n_results: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of matching products with similarity scores
        """
        if not self.initialized:
            logger.warning("❌ ChromaDB not initialized, returning empty results")
            return []
        
        if collection_key not in self.collections:
            logger.error(f"❌ Collection {collection_key} not found")
            return []
        
        collection = self.collections[collection_key]
        
        try:
            # Prepare where clause for filters
            where_clause = None
            if filters:
                where_clause = {}
                if 'max_price' in filters:
                    where_clause['price'] = {"$lte": filters['max_price']}
                if 'min_price' in filters:
                    if 'price' not in where_clause:
                        where_clause['price'] = {}
                    where_clause['price']['$gte'] = filters['min_price']
                if 'category' in filters:
                    where_clause['category'] = filters['category']
                if 'availability' in filters:
                    where_clause['availability'] = filters['availability']
            
            # Perform semantic search
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            if results['metadatas'] and results['metadatas'][0]:
                for i in range(len(results['metadatas'][0])):
                    metadata = results['metadatas'][0][i]
                    
                    # Parse JSON fields
                    try:
                        colors = json.loads(metadata.get('colors', '[]'))
                        occasions = json.loads(metadata.get('occasions', '[]'))
                    except:
                        colors = []
                        occasions = []
                    
                    product_result = {
                        'id': results['ids'][0][i],
                        'name': metadata.get('name', ''),
                        'price': metadata.get('price', 0),
                        'category': metadata.get('category', ''),
                        'colors': colors,
                        'occasions': occasions,
                        'availability': metadata.get('availability', True),
                        'image_url': metadata.get('image_url', ''),
                        'similarity_score': 1.0 - results['distances'][0][i] if results.get('distances') else 0.9,
                        'document': results['documents'][0][i] if results.get('documents') else ''
                    }
                    formatted_results.append(product_result)
            
            logger.info(f"🔍 Found {len(formatted_results)} products for query: '{query}'")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Search error in {collection_key}: {e}")
            return []
    
    def search_by_occasion(self, occasion: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search products suitable for a specific occasion"""
        return self.search_products(
            query=f"flori pentru {occasion}",
            collection_key='products_occasions',
            n_results=n_results
        )
    
    def search_by_budget(self, min_price: float, max_price: float, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search products within a budget range"""
        return self.search_products(
            query="flori frumoase",
            filters={'min_price': min_price, 'max_price': max_price},
            n_results=n_results
        )
    
    def get_similar_products(self, product_id: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Find products similar to a given product"""
        # First get the product document
        for collection_key, collection in self.collections.items():
            try:
                result = collection.get(ids=[product_id])
                if result['documents']:
                    # Use the product document as query to find similar ones
                    return self.search_products(
                        query=result['documents'][0],
                        collection_key=collection_key,
                        n_results=n_results + 1  # +1 to exclude the original product
                    )[1:]  # Skip the first result (original product)
            except:
                continue
        
        return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections"""
        stats = {
            'initialized': self.initialized,
            'db_path': self.db_path,
            'embedding_model': self.embedding_model_name,
            'collections': {}
        }
        
        if self.initialized:
            for collection_key, collection in self.collections.items():
                try:
                    count = collection.count()
                    stats['collections'][collection_key] = {
                        'name': self.collection_names[collection_key],
                        'count': count,
                        'status': 'active'
                    }
                except Exception as e:
                    stats['collections'][collection_key] = {
                        'name': self.collection_names[collection_key],
                        'count': 0,
                        'status': f'error: {e}'
                    }
        
        return stats
    
    def reset_collection(self, collection_key: str):
        """Reset a specific collection (delete all data)"""
        if not self.initialized:
            logger.error("❌ ChromaDB not initialized")
            return False
        
        if collection_key not in self.collection_names:
            logger.error(f"❌ Unknown collection key: {collection_key}")
            return False
        
        try:
            collection_name = self.collection_names[collection_key]
            
            # Delete existing collection
            try:
                self.client.delete_collection(name=collection_name)
                logger.info(f"🗑️ Deleted collection: {collection_name}")
            except:
                pass  # Collection might not exist
            
            # Create new empty collection
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": f"XOFlowers {collection_key} collection"}
            )
            self.collections[collection_key] = collection
            
            logger.info(f"✅ Reset collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resetting collection {collection_key}: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on ChromaDB"""
        health = {
            'status': 'healthy' if self.initialized else 'unhealthy',
            'chromadb_available': HAS_CHROMADB,
            'initialized': self.initialized,
            'db_path': self.db_path,
            'embedding_model': self.embedding_model_name,
            'collections_count': len(self.collections),
            'timestamp': str(os.times())
        }
        
        if self.initialized:
            try:
                # Test basic functionality
                test_collection = self.collections.get('products_main')
                if test_collection:
                    count = test_collection.count()
                    health['test_collection_count'] = count
                    health['test_status'] = 'passed'
                else:
                    health['test_status'] = 'no_collections'
            except Exception as e:
                health['test_status'] = f'failed: {e}'
                health['status'] = 'degraded'
        
        return health


# Global ChromaDB manager instance
_chromadb_manager = None

def get_chromadb_manager() -> ChromaDBManager:
    """Get the global ChromaDB manager instance"""
    global _chromadb_manager
    if _chromadb_manager is None:
        _chromadb_manager = ChromaDBManager()
    return _chromadb_manager