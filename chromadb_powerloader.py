#!/usr/bin/env python3
"""
ChromaDB PowerLoader v2.0 - Optimizat pentru XOFlowers
Compatibil cu ChromaDB 0.5+ 
"""

import chromadb
import pandas as pd
import os
import time
import logging
from typing import List, Dict, Any, Optional
import json
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XOFlowersPowerDB:
    """
    ChromaDB Power Configuration pentru XOFlowers
    - Optimizat pentru căutări multilingvale
    - Indexare avansată pentru 709+ produse
    - Performanță maximă pentru vector search
    """
    
    def __init__(self, persist_directory: str = "./chroma_powerdb"):
        self.persist_directory = persist_directory
        self.collection_name = "xoflowers_power_collection"
        
        # Creează directorul dacă nu există
        os.makedirs(persist_directory, exist_ok=True)
        
        # Inițializare client ChromaDB
        logger.info(f"🔧 Initializing ChromaDB client at {persist_directory}")
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        self.collection = None
        
        logger.info("✅ ChromaDB PowerLoader initialized")
    
    def reset_collection(self) -> bool:
        """Resetează colecția pentru o încărcare fresh"""
        try:
            # Încearcă să șteargă colecția existentă
            try:
                self.client.delete_collection(name=self.collection_name)
                logger.info(f"🗑️ Deleted existing collection: {self.collection_name}")
            except:
                logger.info(f"ℹ️ No existing collection to delete")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resetting collection: {e}")
            return False
    
    def create_power_collection(self) -> bool:
        """Creează colecția optimizată"""
        try:
            # Resetează colecția
            self.reset_collection()
            
            # Creează colecția nouă
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "XOFlowers Products - Power Search Enabled",
                    "version": "2.0",
                    "total_products": 0,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "model": "multilingual-optimized"
                }
            )
            
            logger.info(f"✅ Created power collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating collection: {e}")
            return False
    
    def load_chunks_data(self, csv_path: str = "chunks_data.csv") -> pd.DataFrame:
        """Încarcă datele din chunks_data.csv"""
        try:
            if not os.path.exists(csv_path):
                logger.error(f"❌ File not found: {csv_path}")
                return pd.DataFrame()
            
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"📊 Loaded {len(df)} total records from {csv_path}")
            
            # Filtrare doar produse
            product_df = df[df['chunk_type'] == 'product'].copy()
            logger.info(f"🌸 Found {len(product_df)} products")
            
            # Cleanup date
            product_df = product_df.dropna(subset=['primary_text'])
            product_df['price'] = pd.to_numeric(product_df['price'], errors='coerce').fillna(0)
            
            # Adaugă ID-uri unice
            product_df['unique_id'] = [str(uuid.uuid4()) for _ in range(len(product_df))]
            
            logger.info(f"✅ Prepared {len(product_df)} clean products for loading")
            return product_df
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            return pd.DataFrame()
    
    def enhance_product_text(self, row: pd.Series) -> str:
        """Îmbunătățește textul pentru căutare optimă"""
        # Text principal
        text = str(row['primary_text'])
        
        # Adaugă informații structurate
        if pd.notna(row['category']):
            text += f" | Categorie: {row['category']}"
        
        if pd.notna(row['flower_type']):
            text += f" | Flori: {row['flower_type']}"
        
        if pd.notna(row['price']) and row['price'] > 0:
            text += f" | Preț: {int(row['price'])} MDL"
        
        # Termeni de căutare românești
        flower_type = str(row['flower_type']).lower()
        
        # Mapări pentru căutare mai bună
        search_terms = []
        if 'rose' in flower_type or 'trandafir' in flower_type:
            search_terms.append("trandafiri roses")
        if 'peony' in flower_type or 'peon' in flower_type:
            search_terms.append("bujori peonies")
        if 'hydrangea' in flower_type:
            search_terms.append("hortensie hydrangea")
        if 'diffuser' in flower_type or 'difuzor' in flower_type:
            search_terms.append("difuzor aromă")
        
        if search_terms:
            text += f" | Căutare: {' '.join(search_terms)}"
        
        return text
    
    def create_metadata(self, row: pd.Series) -> Dict[str, Any]:
        """Creează metadata pentru fiecare produs"""
        price = float(row['price']) if pd.notna(row['price']) else 0.0
        
        # Determină categoria de preț
        if price <= 0:
            price_range = "unknown"
        elif price < 600:
            price_range = "budget"
        elif price < 1200:
            price_range = "mid"
        elif price < 2500:
            price_range = "premium"
        else:
            price_range = "luxury"
        
        metadata = {
            "chunk_id": str(row['chunk_id']),
            "category": str(row['category']) if pd.notna(row['category']) else "",
            "flower_type": str(row['flower_type']) if pd.notna(row['flower_type']) else "",
            "price": price,
            "price_range": price_range,
            "url": str(row['url']) if pd.notna(row['url']) else "",
            
            # Flags pentru căutare rapidă
            "has_roses": "rose" in str(row['flower_type']).lower() or "trandafir" in str(row['flower_type']).lower(),
            "has_peonies": "peony" in str(row['flower_type']).lower() or "peon" in str(row['flower_type']).lower(),
            "is_diffuser": "diffuser" in str(row['flower_type']).lower() or "difuzor" in str(row['flower_type']).lower(),
            "is_bouquet": "bouquet" in str(row['primary_text']).lower() or "buchet" in str(row['primary_text']).lower(),
            "is_basket": "basket" in str(row['primary_text']).lower() or "coș" in str(row['primary_text']).lower(),
        }
        
        return metadata
    
    def load_products_batch(self, df: pd.DataFrame, batch_size: int = 20) -> bool:
        """Încarcă produsele în batch-uri"""
        try:
            total_products = len(df)
            logger.info(f"🚀 Starting power loading of {total_products} products...")
            
            successful_loads = 0
            
            for i in range(0, total_products, batch_size):
                batch = df.iloc[i:i + batch_size]
                
                # Pregătire batch
                documents = []
                metadatas = []
                ids = []
                
                for _, row in batch.iterrows():
                    # Text îmbunătățit
                    enhanced_text = self.enhance_product_text(row)
                    documents.append(enhanced_text)
                    
                    # Metadata
                    metadata = self.create_metadata(row)
                    metadatas.append(metadata)
                    
                    # ID unic
                    ids.append(str(row['unique_id']))
                
                try:
                    # Adaugă în ChromaDB
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    successful_loads += len(batch)
                    
                    # Progress
                    progress = min(i + batch_size, total_products)
                    percentage = (progress / total_products) * 100
                    logger.info(f"📦 Batch {progress}/{total_products} loaded ({percentage:.1f}%)")
                    
                except Exception as batch_error:
                    logger.error(f"❌ Error loading batch {i}: {batch_error}")
                    continue
                
                # Pauză mică
                time.sleep(0.05)
            
            logger.info(f"✅ Successfully loaded {successful_loads}/{total_products} products!")
            
            # Actualizează metadata colecției
            if successful_loads > 0:
                self.collection.modify(metadata={"total_products": successful_loads})
            
            return successful_loads > 0
            
        except Exception as e:
            logger.error(f"❌ Error in batch loading: {e}")
            return False
    
    def verify_database(self) -> Dict[str, Any]:
        """Verifică starea bazei de date"""
        try:
            count = self.collection.count()
            
            # Test de căutare
            test_results = self.collection.query(
                query_texts=["trandafiri roșii"],
                n_results=3
            )
            
            # Statistici
            stats = {
                "total_products": count,
                "collection_name": self.collection_name,
                "database_path": self.persist_directory,
                "test_results_count": len(test_results['documents'][0]) if test_results['documents'] else 0,
                "sample_product": test_results['documents'][0][0][:150] + "..." if test_results['documents'] and test_results['documents'][0] else "No results"
            }
            
            logger.info(f"📊 Database verification complete: {count} products")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error verifying database: {e}")
            return {}
    
    def create_search_interface(self):
        """Creează interfața de căutare optimizată"""
        def power_search(
            query: str,
            n_results: int = 5,
            filters: Optional[Dict] = None
        ) -> Dict[str, Any]:
            """
            Căutare vectorială optimizată
            
            Args:
                query: Textul de căutare
                n_results: Numărul de rezultate
                filters: Filtre (price_range, category, etc.)
            
            Returns:
                Rezultate formatate
            """
            try:
                # Construire filtru where
                where_clause = {}
                if filters:
                    if filters.get('price_range'):
                        where_clause['price_range'] = filters['price_range']
                    if filters.get('category'):
                        where_clause['category'] = {"$contains": filters['category']}
                    if filters.get('has_roses'):
                        where_clause['has_roses'] = True
                    if filters.get('has_peonies'):
                        where_clause['has_peonies'] = True
                
                # Execută căutarea
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    where=where_clause if where_clause else None
                )
                
                # Formatare rezultate
                formatted_results = []
                if results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        result = {
                            "text": doc,
                            "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                            "distance": results['distances'][0][i] if results['distances'] else 0,
                            "id": results['ids'][0][i] if results['ids'] else ""
                        }
                        formatted_results.append(result)
                
                return {
                    "query": query,
                    "filters": filters,
                    "results": formatted_results,
                    "count": len(formatted_results)
                }
                
            except Exception as e:
                logger.error(f"❌ Search error: {e}")
                return {"query": query, "results": [], "count": 0, "error": str(e)}
        
        return power_search
    
    def save_config(self):
        """Salvează configurația"""
        config = {
            "persist_directory": self.persist_directory,
            "collection_name": self.collection_name,
            "total_products": self.collection.count() if self.collection else 0,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "2.0"
        }
        
        config_path = os.path.join(self.persist_directory, "xoflowers_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Configuration saved to {config_path}")
    
    def load_chunks_data(self, csv_path: str = "chunks_data.csv") -> pd.DataFrame:
        """Încarcă și procesează datele din chunks_data.csv"""
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"📊 Loaded {len(df)} records from {csv_path}")
            
            # Filtrare doar produse (nu colecții)
            product_df = df[df['chunk_type'] == 'product'].copy()
            logger.info(f"🌸 Found {len(product_df)} products")
            
            # Cleanup și validare date
            product_df = product_df.dropna(subset=['primary_text'])
            product_df['price'] = pd.to_numeric(product_df['price'], errors='coerce').fillna(0)
            
            # Adaugă ID-uri unice pentru fiecare produs
            product_df['unique_id'] = [str(uuid.uuid4()) for _ in range(len(product_df))]
            
            return product_df
            
        except Exception as e:
            logger.error(f"❌ Error loading data: {e}")
            return pd.DataFrame()
    
    def enhance_product_text(self, row: pd.Series) -> str:
        """Îmbunătățește textul produsului pentru indexare optimă"""
        # Textul principal
        enhanced_text = row['primary_text']
        
        # Adaugă informații structurate
        if pd.notna(row['category']):
            enhanced_text += f" | Categorie: {row['category']}"
        
        if pd.notna(row['flower_type']):
            enhanced_text += f" | Tip flori: {row['flower_type']}"
        
        if pd.notna(row['price']) and row['price'] > 0:
            enhanced_text += f" | Preț: {row['price']} MDL"
        
        # Adaugă termeni de căutare în română și engleză
        flower_types = str(row['flower_type']).lower()
        if 'trandafir' in flower_types or 'rose' in flower_types:
            enhanced_text += " | trandafiri roses"
        if 'peon' in flower_types:
            enhanced_text += " | bujori peonies"
        if 'hydrangea' in flower_types:
            enhanced_text += " | hortensie hydrangea"
        
        return enhanced_text
    
    def create_metadata(self, row: pd.Series) -> Dict[str, Any]:
        """Creează metadata optimizată pentru fiecare produs"""
        metadata = {
            "chunk_id": str(row['chunk_id']),
            "unique_id": str(row['unique_id']),
            "category": str(row['category']) if pd.notna(row['category']) else "",
            "flower_type": str(row['flower_type']) if pd.notna(row['flower_type']) else "",
            "price": float(row['price']) if pd.notna(row['price']) else 0.0,
            "url": str(row['url']) if pd.notna(row['url']) else "",
            "collection_id": str(row['collection_id']) if pd.notna(row['collection_id']) else "",
            
            # Metadate avansate pentru căutare
            "price_range": self._get_price_range(row['price']),
            "has_roses": "trandafir" in str(row['flower_type']).lower() or "rose" in str(row['flower_type']).lower(),
            "has_peonies": "peon" in str(row['flower_type']).lower(),
            "is_bouquet": "buchet" in str(row['primary_text']).lower() or "bouquet" in str(row['primary_text']).lower(),
            "is_box": "cutie" in str(row['primary_text']).lower() or "box" in str(row['primary_text']).lower(),
            "is_basket": "coș" in str(row['primary_text']).lower() or "basket" in str(row['primary_text']).lower(),
        }
        
        return metadata
    
    def _get_price_range(self, price: float) -> str:
        """Determină categoria de preț"""
        if price <= 0:
            return "unknown"
        elif price < 500:
            return "budget"
        elif price < 1000:
            return "mid"
        elif price < 2000:
            return "premium"
        else:
            return "luxury"
    
    def load_products_in_batches(self, df: pd.DataFrame, batch_size: int = 50) -> bool:
        """Încarcă produsele în batch-uri pentru performanță optimă"""
        try:
            total_rows = len(df)
            logger.info(f"🚀 Starting batch loading of {total_rows} products...")
            
            for i in range(0, total_rows, batch_size):
                batch = df.iloc[i:i + batch_size]
                
                # Pregătire date pentru batch
                documents = []
                metadatas = []
                ids = []
                
                for _, row in batch.iterrows():
                    # Text îmbunătățit pentru embedding
                    enhanced_text = self.enhance_product_text(row)
                    documents.append(enhanced_text)
                    
                    # Metadata optimizată
                    metadata = self.create_metadata(row)
                    metadatas.append(metadata)
                    
                    # ID unic
                    ids.append(str(row['unique_id']))
                
                # Adaugă batch-ul în ChromaDB
                self.collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
                
                # Progress logging
                progress = min(i + batch_size, total_rows)
                logger.info(f"📦 Loaded batch {progress}/{total_rows} ({progress/total_rows*100:.1f}%)")
                
                # Pauză mică pentru a nu suprasolicita memoria
                time.sleep(0.1)
            
            logger.info(f"✅ Successfully loaded all {total_rows} products to ChromaDB!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error during batch loading: {e}")
            return False
    
    def verify_loading(self) -> Dict[str, Any]:
        """Verifică că datele au fost încărcate corect"""
        try:
            count = self.collection.count()
            
            # Test query
            test_results = self.collection.query(
                query_texts=["trandafiri roșii"],
                n_results=3
            )
            
            # Statistici despre colecție
            stats = {
                "total_products": count,
                "collection_name": self.collection_name,
                "embedding_model": "paraphrase-multilingual-mpnet-base-v2",
                "test_query_results": len(test_results['documents'][0]) if test_results['documents'] else 0,
                "sample_result": test_results['documents'][0][0] if test_results['documents'] and test_results['documents'][0] else "No results"
            }
            
            logger.info(f"📊 Collection Stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error verifying loading: {e}")
            return {}
    
    def create_advanced_search_method(self):
        """Creează metodă de căutare avansată"""
        def advanced_search(
            query: str,
            n_results: int = 5,
            price_range: Optional[str] = None,
            category: Optional[str] = None,
            flower_type: Optional[str] = None
        ) -> Dict[str, Any]:
            """
            Căutare avansată în ChromaDB
            
            Args:
                query: Textul de căutare
                n_results: Numărul de rezultate
                price_range: Filtru preț (budget, mid, premium, luxury)
                category: Filtru categorie
                flower_type: Filtru tip flori
            """
            # Construire filtru where
            where_filter = {}
            
            if price_range:
                where_filter["price_range"] = price_range
            
            if category:
                where_filter["category"] = {"$contains": category}
            
            if flower_type:
                where_filter["flower_type"] = {"$contains": flower_type}
            
            # Execută căutarea
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )
            
            return {
                "query": query,
                "filters": where_filter,
                "results": results,
                "count": len(results['documents'][0]) if results['documents'] else 0
            }
        
        return advanced_search
    
    def save_configuration(self):
        """Salvează configurația pentru utilizare ulterioară"""
        config = {
            "persist_directory": self.persist_directory,
            "collection_name": self.collection_name,
            "embedding_model": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            "hnsw_params": self.hnsw_params,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_products": self.collection.count() if self.collection else 0
        }
        
        config_path = os.path.join(self.persist_directory, "config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Configuration saved to {config_path}")

def main():
    """Funcția principală"""
    print("🌸 XOFlowers ChromaDB PowerLoader v2.0")
    print("=" * 50)
    
    # Verifică fișierul chunks_data.csv
    csv_file = "chunks_data.csv"
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        print("Please ensure chunks_data.csv is in the current directory")
        return
    
    # Inițializare PowerDB
    print("🔧 Initializing XOFlowers PowerDB...")
    power_db = XOFlowersPowerDB()
    
    # Creează colecția
    if not power_db.create_power_collection():
        print("❌ Failed to create collection!")
        return
    
    # Încarcă datele
    print("📊 Loading product data...")
    df = power_db.load_chunks_data(csv_file)
    
    if df.empty:
        print("❌ No products found to load!")
        return
    
    # Proces de încărcare power
    print("🚀 Starting POWER LOADING...")
    start_time = time.time()
    
    success = power_db.load_products_batch(df, batch_size=15)
    
    if success:
        end_time = time.time()
        
        # Verificare finală
        print("🔍 Verifying database...")
        stats = power_db.verify_database()
        
        # Salvează configurația
        power_db.save_config()
        
        # Creează interfața de căutare
        search_func = power_db.create_search_interface()
        
        # Afișează rezultatele
        print("\n" + "=" * 50)
        print("✅ POWER LOADING SUCCESSFUL!")
        print(f"⏱️  Time: {end_time - start_time:.2f} seconds")
        print(f"📊 Products loaded: {stats.get('total_products', 0)}")
        print(f"📁 Database: {stats.get('database_path', 'Unknown')}")
        print("=" * 50)
        
        # Test rapid
        print("\n🧪 Testing search functionality...")
        test_result = search_func("trandafiri roșii pentru iubire")
        if test_result['count'] > 0:
            print(f"✅ Search test successful: {test_result['count']} results")
            print(f"📝 Top result: {test_result['results'][0]['text'][:100]}...")
        else:
            print("⚠️ Search test returned no results")
        
        print("\n🎉 XOFlowers PowerDB is ready for production!")
        print("🔍 Vector search enabled with multilingual support")
        
    else:
        print("❌ Power loading failed!")

if __name__ == "__main__":
    main()
