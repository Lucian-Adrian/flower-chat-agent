import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv
from config import CHROMA_DB_PATH, EMBEDDING_MODEL, CATEGORIES, DEFAULT_SEARCH_RESULTS

# Load environment variables from .env
load_dotenv()

class XoFlowersDB:
    """
    Simple database for flower search using ChromaDB and local embeddings
    """
    def __init__(self):
        # Create ChromaDB client
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        
        # Load embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Create collections for categories
        self.collections = self._create_collections()
        
    def _create_collections(self):
        """
        Create collections for each product category
        """
        collections = {}
        for category in CATEGORIES.keys():
            collection_name = f"xoflowers_{category}"
            
            # Create collection with our embedding function
            collections[category] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"category": category}
            )
            print(f"   ✅ {category}")
            
        return collections
    
    def _get_category(self, product_data):
        """
        Determine which category to place the product in
        """
        # Safely get strings (protection from NaN)
        category = str(product_data.get('category', '')).lower()
        flower_type = str(product_data.get('flower_type', '')).lower()
        
        # Check each category
        for main_category, keywords in CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in category or keyword.lower() in flower_type:
                    return main_category
        
        # Default to flowers
        return 'flowers'
    
    def _prepare_text(self, product_data):
        """
        Prepare text for search embedding
        """
        text_parts = []
        
        # Primary text (protection from NaN)
        primary_text = product_data.get('primary_text')
        if primary_text and str(primary_text) != 'nan':
            text_parts.append(str(primary_text))
        
        # Category
        category = product_data.get('category')
        if category and str(category) != 'nan':
            text_parts.append(f"Category: {category}")
            
        # Flower type
        flower_type = product_data.get('flower_type')
        if flower_type and str(flower_type) != 'nan':
            text_parts.append(f"Type: {flower_type}")
            
        # Price
        price = product_data.get('price')
        if price and str(price) != 'nan' and price > 0:
            text_parts.append(f"Price: {price} lei")
        
        # If no text at all, add basic information
        if not text_parts:
            text_parts.append(f"Product {product_data.get('chunk_id', 'without ID')}")
        
        return " | ".join(text_parts)
    
    def _prepare_metadata(self, product_data):
        """
        Prepare metadata for storage
        """
        return {
            "chunk_id": str(product_data.get('chunk_id', '')),
            "category": str(product_data.get('category', '')),
            "price": float(product_data.get('price', 0)) if product_data.get('price') else 0.0,
            "flower_type": str(product_data.get('flower_type', '')),
            "url": str(product_data.get('url', '')),
        }
    
    def load_products_from_csv(self, csv_file="data/chunks_data.csv"):
        """
        MAIN FUNCTION: Load products from CSV file
        """
        print(f"📂 Loading products from {csv_file}...")
        
        # Read CSV
        df = pd.read_csv(csv_file)
        print(f"📊 Found {len(df)} products")
        
        # Clear old data
        print("🧹 Clearing old data...")
        for collection in self.collections.values():
            try:
                # Get all IDs and delete
                all_data = collection.get()
                if all_data['ids']:
                    collection.delete(ids=all_data['ids'])
            except:
                pass
        
        # Load new data
        stats = {}
        
        for index, row in df.iterrows():
            try:
                # Determine category
                category = self._get_category(row)
                
                # Prepare data
                text = self._prepare_text(row)
                metadata = self._prepare_metadata(row)
                
                # Create embedding
                embedding = self.embedding_model.encode([text])[0].tolist()
                
                # Add to collection
                self.collections[category].add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[metadata],
                    ids=[str(row['chunk_id'])]
                )
                
                # Statistics
                if category not in stats:
                    stats[category] = 0
                stats[category] += 1
                
                # Progress
                if index % 100 == 0:
                    print(f"   Processed {index} products...")
                    
            except Exception as e:
                print(f"❌ Error with product {index}: {e}")
                continue
        
        print("\n✅ Loading completed!")
        print("📈 Statistics by categories:")
        for category, count in stats.items():
            print(f"   {category}: {count} products")
        
        return stats
    
    def search_products(self, query, category=None, n_results=None):
        """
        MAIN FUNCTION: Search products by query
        """
        if n_results is None:
            n_results = DEFAULT_SEARCH_RESULTS
            
        print(f"🔍 Searching: '{query}'")
        
        # Create embedding for query
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        results = []
        
        if category and category in self.collections:
            # Search in specific category
            collection_results = self.collections[category].query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            results.extend(self._format_results(collection_results, category))
            
        else:
            # Search in all categories
            for cat_name, collection in self.collections.items():
                try:
                    collection_results = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=n_results
                    )
                    results.extend(self._format_results(collection_results, cat_name))
                except Exception as e:
                    print(f"❌ Search error in {cat_name}: {e}")
                    continue
            
            # Sort by relevance and take the best
            results.sort(key=lambda x: x['distance'])
            results = results[:n_results]
        
        print(f"✅ Found {len(results)} products")
        return results
    
    def _format_results(self, results, category):
        """
        Format search results
        """
        formatted = []
        
        if not results['documents'][0]:
            return formatted
            
        for i in range(len(results['documents'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'category': category,
                'relevance': 1 - results['distances'][0][i]  # Closer to 1 is better
            })
            
        return formatted
    
    def search_by_price(self, min_price=0, max_price=float('inf')):
        """
        Search products by price range
        """
        print(f"💰 Searching products from {min_price} to {max_price} lei")
        
        all_results = []
        
        for category, collection in self.collections.items():
            try:
                # Get all products from category
                data = collection.get()
                
                for i, metadata in enumerate(data['metadatas']):
                    price = metadata.get('price', 0)
                    if min_price <= price <= max_price:
                        all_results.append({
                            'id': data['ids'][i],
                            'text': data['documents'][i],
                            'metadata': metadata,
                            'category': category,
                            'price': price
                        })
            except Exception as e:
                print(f"❌ Price search error in {category}: {e}")
                continue
        
        # Sort by price
        all_results.sort(key=lambda x: x['price'])
        
        print(f"✅ Found {len(all_results)} products")
        return all_results
    
    def get_stats(self):
        """
        Get database statistics
        """
        stats = {}
        total = 0
        
        for category, collection in self.collections.items():
            try:
                count = collection.count()
                stats[category] = count
                total += count
            except:
                stats[category] = 0
        
        stats['total'] = total
        return stats
    
    def get_product_by_id(self, product_id):
        """
        Get product by ID
        """
        for category, collection in self.collections.items():
            try:
                result = collection.get(ids=[product_id])
                if result['documents']:
                    return {
                        'id': product_id,
                        'text': result['documents'][0],
                        'metadata': result['metadatas'][0],
                        'category': category
                    }
            except:
                continue
        return None

# SIMPLE TEST FUNCTION
def test_database():
    """
    Quick database test
    """
    print("🧪 TESTING DATABASE")
    print("=" * 50)
    
    # Create database
    db = XoFlowersDB()
    
    # Load data
    stats = db.load_products_from_csv()
    
    # Statistics
    print(f"\n📊 STATISTICS:")
    for category, count in stats.items():
        print(f"   {category}: {count} products")
    
    # Test searches
    test_queries = [
        "beautiful roses",
        "gift for mom", 
        "wedding bouquet",
        "aromatic diffuser"
    ]
    
    print(f"\n🔍 TEST SEARCHES:")
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        results = db.search_products(query, n_results=2)
        
        for i, result in enumerate(results, 1):
            price = result['metadata'].get('price', 'N/A')
            category = result['metadata'].get('category', 'N/A')
            relevance = result['relevance']
            print(f"     {i}. {category} - {price} lei (relevance: {relevance:.3f})")
    
    # Price search
    print(f"\n💰 PRICE SEARCH (1000-3000 lei):")
    price_results = db.search_by_price(1000, 3000)
    for result in price_results[:3]:
        print(f"   - {result['metadata']['category']}: {result['price']} lei")
    
    print(f"\n✅ TEST COMPLETED!")

if __name__ == "__main__":
    test_database()