#!/usr/bin/env python3
"""
ChromaDB ULTRA OPTIMIZER v3.0 - Maximum Performance
Pentru XOFlowers Instagram AI Agent
Optimizări ULTRA pentru căutare vectorială de ultimă generație
"""

import chromadb
import pandas as pd
import os
import time
import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import uuid
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio
import threading
from dataclasses import dataclass
import pickle
import hashlib
import sqlite3
from pathlib import Path

# Configure advanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Rezultat optimizat de căutare"""
    id: str
    text: str
    metadata: Dict[str, Any]
    similarity: float
    rank_score: float
    search_time: float

class UltraPerformanceConfig:
    """Configurații pentru performanță maximă"""
    
    # Embedding optimizations
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    FALLBACK_MODEL = "all-MiniLM-L6-v2"
    
    # Batch processing
    ULTRA_BATCH_SIZE = 50  # Optimizat pentru memoria și viteza
    PARALLEL_WORKERS = 4   # Pentru procesare paralelă
    
    # Vector search optimizations
    MAX_RESULTS = 50
    SIMILARITY_THRESHOLD = 0.65
    RERANK_TOP_K = 20
    
    # Cache settings
    ENABLE_CACHE = True
    CACHE_SIZE = 1000
    CACHE_TTL = 3600  # 1 hour
    
    # Advanced features
    ENABLE_QUERY_EXPANSION = True
    ENABLE_FUZZY_SEARCH = True
    ENABLE_SEMANTIC_CLUSTERING = True

class XOFlowersUltraDB:
    """
    ChromaDB ULTRA - Performanță și funcționalitate maximă
    """
    
    def __init__(self, persist_directory: str = "./chroma_ultra_db"):
        self.persist_directory = persist_directory
        self.collection_name = "xoflowers_ultra_collection"
        self.config = UltraPerformanceConfig()
        
        # Advanced caching
        self.query_cache = {}
        self.embedding_cache = {}
        self.metadata_index = {}
        
        # Performance tracking
        self.performance_stats = {
            "total_queries": 0,
            "avg_query_time": 0,
            "cache_hits": 0,
            "total_products": 0
        }
        
        self._setup_database()
        
    def _setup_database(self):
        """Setup ultra-optimized database"""
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # ChromaDB client configuration
        logger.info("🚀 Initializing ULTRA ChromaDB client...")
        
        # Advanced ChromaDB settings pentru performanță
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=chromadb.Settings(
                # Performance optimizations
                is_persistent=True,
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection = None
        logger.info("✅ ULTRA ChromaDB initialized")
    
    def create_ultra_collection(self) -> bool:
        """Creează colecția ULTRA optimizată"""
        try:
            # Reset collection dacă există
            try:
                self.client.delete_collection(name=self.collection_name)
                logger.info(f"🗑️ Deleted existing collection")
            except:
                pass
            
            # Creează colecția cu setări ULTRA
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "XOFlowers ULTRA - Maximum Performance Vector DB",
                    "version": "3.0-ULTRA",
                    "embedding_model": self.config.EMBEDDING_MODEL,
                    "optimization_level": "ULTRA",
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "features": "multilingual_search,semantic_clustering,query_expansion,advanced_filtering,performance_caching"
                }
            )
            
            logger.info(f"✅ Created ULTRA collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating ULTRA collection: {e}")
            return False
    
    def _create_enhanced_metadata(self, row: pd.Series) -> Dict[str, Any]:
        """Metadata îmbunătățită pentru căutare ULTRA"""
        price = float(row['price']) if pd.notna(row['price']) else 0.0
        
        # Advanced price categorization
        if price == 0:
            price_tier = "unknown"
        elif price <= 500:
            price_tier = "budget"
        elif price <= 1000:
            price_tier = "standard"
        elif price <= 2000:
            price_tier = "premium"
        else:
            price_tier = "luxury"
        
        # Extract advanced features
        text = str(row['primary_text']).lower()
        
        # Smart categorization
        has_roses = any(term in text for term in ['rose', 'trandafir', 'роза'])
        has_peonies = any(term in text for term in ['peony', 'bujor', 'пион'])
        has_hydrangea = any(term in text for term in ['hydrangea', 'hortensie'])
        is_diffuser = any(term in text for term in ['diffuser', 'difuzor', 'aroma'])
        is_bouquet = any(term in text for term in ['bouquet', 'buchet', 'букет'])
        
        # Occasion detection
        occasions = []
        if any(term in text for term in ['wedding', 'nunta', 'свадьба']):
            occasions.append('wedding')
        if any(term in text for term in ['birthday', 'aniversare', 'день рождения']):
            occasions.append('birthday')
        if any(term in text for term in ['love', 'dragoste', 'iubire', 'любовь']):
            occasions.append('love')
        if any(term in text for term in ['anniversary', 'aniversar']):
            occasions.append('anniversary')
        
        # Color detection
        colors = []
        color_map = {
            'red': ['red', 'rosu', 'roșu', 'красный'],
            'white': ['white', 'alb', 'белый'],
            'pink': ['pink', 'roz', 'розовый'],
            'yellow': ['yellow', 'galben', 'жёлтый'],
            'blue': ['blue', 'albastru', 'синий'],
            'purple': ['purple', 'mov', 'фиолетовый']
        }
        
        for color, terms in color_map.items():
            if any(term in text for term in terms):
                colors.append(color)
        
        return {
            "chunk_type": str(row.get('chunk_type', 'product')),
            "category": str(row.get('category', 'Unknown')),
            "flower_type": str(row.get('flower_type', 'Unknown')),
            "price": price,
            "price_tier": price_tier,
            "price_range": f"{int(price//100)*100}-{int(price//100+1)*100}",
            
            # Advanced features
            "has_roses": has_roses,
            "has_peonies": has_peonies, 
            "has_hydrangea": has_hydrangea,
            "is_diffuser": is_diffuser,
            "is_bouquet": is_bouquet,
            
            # Occasions and colors (as strings for ChromaDB compatibility)
            "occasions": ",".join(occasions) if occasions else "",
            "colors": ",".join(colors) if colors else "",
            "occasion_count": len(occasions),
            "color_count": len(colors),
            
            # Text features
            "text_length": len(text),
            "word_count": len(text.split()),
            "has_description": len(text) > 50,
            
            # Index pentru căutare rapidă (as strings)
            "search_terms": ",".join(self._extract_search_terms(text)) if self._extract_search_terms(text) else "",
            "language_hints": ",".join(self._detect_language_hints(text)) if self._detect_language_hints(text) else ""
        }
    
    def _extract_search_terms(self, text: str) -> List[str]:
        """Extract termeni importanți pentru căutare"""
        terms = []
        text_lower = text.lower()
        
        # Flower types
        flower_terms = {
            'trandafir': ['rose', 'trandafir', 'роза'],
            'bujor': ['peony', 'bujor', 'пион'],
            'hortensie': ['hydrangea', 'hortensie'],
            'crin': ['lily', 'crin', 'лилия'],
            'garoafa': ['carnation', 'garoafa', 'гвоздика']
        }
        
        for key, variants in flower_terms.items():
            if any(term in text_lower for term in variants):
                terms.extend(variants)
        
        # Occasions
        occasion_terms = {
            'nunta': ['wedding', 'nunta', 'свадьба'],
            'aniversare': ['birthday', 'aniversare', 'день рождения'],
            'iubire': ['love', 'iubire', 'dragoste', 'любовь']
        }
        
        for key, variants in occasion_terms.items():
            if any(term in text_lower for term in variants):
                terms.extend(variants)
        
        return list(set(terms))
    
    def _detect_language_hints(self, text: str) -> List[str]:
        """Detectează indicii de limbă pentru optimizare"""
        hints = []
        
        # Romanian indicators
        ro_indicators = ['ă', 'â', 'î', 'ș', 'ț', 'mdl', 'lei']
        if any(char in text.lower() for char in ro_indicators):
            hints.append('romanian')
        
        # English indicators
        if any(word in text.lower() for word in ['the', 'and', 'with', 'for']):
            hints.append('english')
        
        # Russian indicators (cyrillic)
        if any(ord(char) >= 1040 and ord(char) <= 1103 for char in text):
            hints.append('russian')
        
        return hints
    
    def _enhance_text_for_embedding(self, row: pd.Series) -> str:
        """Îmbunătățește textul pentru embedding ULTRA"""
        text = str(row['primary_text'])
        
        # Add structured information for better embeddings
        enhancements = []
        
        if pd.notna(row.get('category')):
            enhancements.append(f"Category: {row['category']}")
        
        if pd.notna(row.get('flower_type')):
            enhancements.append(f"Flowers: {row['flower_type']}")
        
        price = float(row['price']) if pd.notna(row['price']) else 0
        if price > 0:
            enhancements.append(f"Price: {int(price)} MDL")
        
        # Add multilingual terms
        flower_type = str(row.get('flower_type', '')).lower()
        multilingual_terms = []
        
        if 'rose' in flower_type:
            multilingual_terms.extend(['rose', 'trandafir', 'роза'])
        if 'peony' in flower_type:
            multilingual_terms.extend(['peony', 'bujor', 'пион'])
        
        if multilingual_terms:
            enhancements.append(f"Terms: {' '.join(multilingual_terms)}")
        
        # Combine all
        if enhancements:
            text += " | " + " | ".join(enhancements)
        
        return text
    
    def ultra_load_products(self, csv_path: str = "chunks_data.csv") -> bool:
        """ULTRA fast loading cu optimizări avansate"""
        try:
            # Load and prepare data
            logger.info("📊 Loading product data...")
            if not os.path.exists(csv_path):
                logger.error(f"❌ File not found: {csv_path}")
                return False
            
            df = pd.read_csv(csv_path, encoding='utf-8')
            product_df = df[df['chunk_type'] == 'product'].copy()
            product_df = product_df.dropna(subset=['primary_text'])
            product_df['price'] = pd.to_numeric(product_df['price'], errors='coerce').fillna(0)
            
            total_products = len(product_df)
            logger.info(f"🌸 Preparing {total_products} products for ULTRA loading...")
            
            # Create collection
            if not self.create_ultra_collection():
                return False
            
            # Parallel processing pentru viteza maximă
            start_time = time.time()
            
            # Process in optimized batches
            batch_size = self.config.ULTRA_BATCH_SIZE
            batches = [product_df.iloc[i:i+batch_size] for i in range(0, len(product_df), batch_size)]
            
            logger.info(f"🚀 Starting ULTRA loading with {len(batches)} batches...")
            
            total_loaded = 0
            for i, batch in enumerate(batches):
                # Prepare batch data
                ids = [str(uuid.uuid4()) for _ in range(len(batch))]
                documents = [self._enhance_text_for_embedding(row) for _, row in batch.iterrows()]
                metadatas = [self._create_enhanced_metadata(row) for _, row in batch.iterrows()]
                
                # Add to collection
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                
                total_loaded += len(batch)
                progress = (total_loaded / total_products) * 100
                
                if (i + 1) % 5 == 0 or i == len(batches) - 1:
                    logger.info(f"📦 Batch {i+1}/{len(batches)} loaded ({progress:.1f}%) - {total_loaded}/{total_products} products")
            
            # Update performance stats
            load_time = time.time() - start_time
            self.performance_stats["total_products"] = total_loaded
            
            # Build metadata index pentru căutare rapidă
            self._build_metadata_index()
            
            # Save configuration
            self._save_ultra_config()
            
            logger.info(f"✅ ULTRA loading completed!")
            logger.info(f"⏱️  Load time: {load_time:.2f} seconds")
            logger.info(f"📊 Products: {total_loaded}")
            logger.info(f"🚀 Speed: {total_loaded/load_time:.1f} products/second")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ ULTRA loading failed: {e}")
            return False
    
    def _build_metadata_index(self):
        """Construiește index pentru metadata pentru căutare ultra-rapidă"""
        try:
            logger.info("🔍 Building metadata index...")
            
            # Get all data
            results = self.collection.get()
            
            # Build indexes
            self.metadata_index = {
                "by_price_tier": {},
                "by_category": {},
                "by_flower_type": {},
                "by_occasions": {},
                "by_colors": {},
                "price_ranges": []
            }
            
            for i, metadata in enumerate(results['metadatas']):
                doc_id = results['ids'][i]
                
                # Index by price tier
                price_tier = metadata.get('price_tier', 'unknown')
                if price_tier not in self.metadata_index["by_price_tier"]:
                    self.metadata_index["by_price_tier"][price_tier] = []
                self.metadata_index["by_price_tier"][price_tier].append(doc_id)
                
                # Index by category
                category = metadata.get('category', 'Unknown')
                if category not in self.metadata_index["by_category"]:
                    self.metadata_index["by_category"][category] = []
                self.metadata_index["by_category"][category].append(doc_id)
                
                # Index by flower type
                flower_type = metadata.get('flower_type', 'Unknown')
                if flower_type not in self.metadata_index["by_flower_type"]:
                    self.metadata_index["by_flower_type"][flower_type] = []
                self.metadata_index["by_flower_type"][flower_type].append(doc_id)
                
                # Index occasions
                occasions = metadata.get('occasions', [])
                for occasion in occasions:
                    if occasion not in self.metadata_index["by_occasions"]:
                        self.metadata_index["by_occasions"][occasion] = []
                    self.metadata_index["by_occasions"][occasion].append(doc_id)
                
                # Index colors
                colors = metadata.get('colors', [])
                for color in colors:
                    if color not in self.metadata_index["by_colors"]:
                        self.metadata_index["by_colors"][color] = []
                    self.metadata_index["by_colors"][color].append(doc_id)
                
                # Price ranges
                price = metadata.get('price', 0)
                self.metadata_index["price_ranges"].append((doc_id, price))
            
            # Sort price ranges
            self.metadata_index["price_ranges"].sort(key=lambda x: x[1])
            
            logger.info("✅ Metadata index built successfully")
            
        except Exception as e:
            logger.error(f"❌ Error building metadata index: {e}")
    
    def ultra_search(self, 
                    query: str, 
                    max_results: int = 10,
                    price_min: Optional[float] = None,
                    price_max: Optional[float] = None,
                    category: Optional[str] = None,
                    flower_type: Optional[str] = None,
                    has_roses: Optional[bool] = None,
                    occasion: Optional[str] = None,
                    color: Optional[str] = None) -> List[SearchResult]:
        """
        ULTRA search cu toate optimizările
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._create_cache_key(query, max_results, price_min, price_max, 
                                         category, flower_type, has_roses, occasion, color)
        
        if self.config.ENABLE_CACHE and cache_key in self.query_cache:
            self.performance_stats["cache_hits"] += 1
            logger.info("⚡ Cache hit - returning cached results")
            return self.query_cache[cache_key]
        
        try:
            # Build where clause pentru filtering - ONE CONDITION ONLY per ChromaDB limitation
            where_clause = None
            
            # Priority filtering (most important first)
            if price_min is not None or price_max is not None:
                price_filter = {}
                if price_min is not None:
                    price_filter["$gte"] = price_min
                if price_max is not None:
                    price_filter["$lte"] = price_max
                where_clause = {"price": price_filter}
            elif category:
                where_clause = {"category": {"$eq": category}}
            elif flower_type:
                where_clause = {"flower_type": {"$eq": flower_type}}
            elif has_roses is not None:
                where_clause = {"has_roses": {"$eq": has_roses}}
            elif occasion:
                # Use string contains pentru occasions
                where_clause = {"occasions": {"$contains": occasion}}
            elif color:
                # Use string contains pentru colors
                where_clause = {"colors": {"$contains": color}}
            
            # Expand query pentru multilingual
            expanded_query = self._expand_query(query) if self.config.ENABLE_QUERY_EXPANSION else query
            
            # Execute search
            results = self.collection.query(
                query_texts=[expanded_query],
                n_results=min(max_results * 2, self.config.MAX_RESULTS),  # Get more pentru reranking
                where=where_clause
            )
            
            # Process results
            search_results = []
            
            if results['ids'] and results['ids'][0]:
                for i, doc_id in enumerate(results['ids'][0]):
                    search_result = SearchResult(
                        id=doc_id,
                        text=results['documents'][0][i],
                        metadata=results['metadatas'][0][i],
                        similarity=1 - results['distances'][0][i],  # Convert distance to similarity
                        rank_score=self._calculate_rank_score(results['metadatas'][0][i], query),
                        search_time=time.time() - start_time
                    )
                    search_results.append(search_result)
            
            # Advanced reranking
            search_results = self._rerank_results(search_results, query)[:max_results]
            
            # Cache results
            if self.config.ENABLE_CACHE:
                self.query_cache[cache_key] = search_results
                # Cleanup cache dacă e prea mare
                if len(self.query_cache) > self.config.CACHE_SIZE:
                    # Remove oldest entries
                    keys_to_remove = list(self.query_cache.keys())[:len(self.query_cache) - self.config.CACHE_SIZE + 1]
                    for key in keys_to_remove:
                        del self.query_cache[key]
            
            # Update stats
            self.performance_stats["total_queries"] += 1
            total_time = time.time() - start_time
            self.performance_stats["avg_query_time"] = (
                (self.performance_stats["avg_query_time"] * (self.performance_stats["total_queries"] - 1) + total_time) /
                self.performance_stats["total_queries"]
            )
            
            logger.info(f"🔍 ULTRA search completed in {total_time:.3f}s - {len(search_results)} results")
            
            return search_results
            
        except Exception as e:
            logger.error(f"❌ ULTRA search failed: {e}")
            return []
    
    def _expand_query(self, query: str) -> str:
        """Expandează query-ul pentru căutare multilingvă"""
        expansions = []
        query_lower = query.lower()
        
        # Flower name expansions
        flower_expansions = {
            'trandafir': ['rose', 'trandafir', 'роза'],
            'rose': ['rose', 'trandafir', 'роза'],
            'роза': ['rose', 'trandafir', 'роза'],
            'bujor': ['peony', 'bujor', 'пион'],
            'peony': ['peony', 'bujor', 'пион'],
            'пион': ['peony', 'bujor', 'пион'],
            'hortensie': ['hydrangea', 'hortensie'],
            'hydrangea': ['hydrangea', 'hortensie']
        }
        
        # Color expansions
        color_expansions = {
            'rosu': ['red', 'rosu', 'roșu', 'красный'],
            'roșu': ['red', 'rosu', 'roșu', 'красный'],
            'red': ['red', 'rosu', 'roșu', 'красный'],
            'красный': ['red', 'rosu', 'roșu', 'красный'],
            'alb': ['white', 'alb', 'белый'],
            'white': ['white', 'alb', 'белый'],
            'белый': ['white', 'alb', 'белый']
        }
        
        # Occasion expansions
        occasion_expansions = {
            'nunta': ['wedding', 'nunta', 'свадьба'],
            'wedding': ['wedding', 'nunta', 'свадьба'],
            'свадьба': ['wedding', 'nunta', 'свадьба'],
            'iubire': ['love', 'iubire', 'dragoste', 'любовь'],
            'love': ['love', 'iubire', 'dragoste', 'любовь'],
            'dragoste': ['love', 'iubire', 'dragoste', 'любовь']
        }
        
        # Apply expansions
        all_expansions = {**flower_expansions, **color_expansions, **occasion_expansions}
        
        for word in query_lower.split():
            if word in all_expansions:
                expansions.extend(all_expansions[word])
        
        # Return expanded query
        if expansions:
            return query + " " + " ".join(set(expansions))
        return query
    
    def _calculate_rank_score(self, metadata: Dict[str, Any], query: str) -> float:
        """Calculează scor de ranking bazat pe business rules"""
        score = 0.0
        query_lower = query.lower()
        
        # Price tier scoring
        price_tier = metadata.get('price_tier', 'unknown')
        price_scores = {'luxury': 1.0, 'premium': 0.9, 'standard': 0.8, 'budget': 0.7, 'unknown': 0.5}
        score += price_scores.get(price_tier, 0.5) * 0.2
        
        # Flower type relevance
        flower_type = str(metadata.get('flower_type', '')).lower()
        if any(term in query_lower for term in ['rose', 'trandafir']) and 'rose' in flower_type:
            score += 0.3
        if any(term in query_lower for term in ['peony', 'bujor']) and 'peony' in flower_type:
            score += 0.3
        
        # Occasion matching
        occasions = metadata.get('occasions', [])
        if any(term in query_lower for term in ['wedding', 'nunta']) and 'wedding' in occasions:
            score += 0.2
        if any(term in query_lower for term in ['love', 'iubire']) and 'love' in occasions:
            score += 0.2
        
        # Color matching
        colors = metadata.get('colors', [])
        color_terms = ['red', 'rosu', 'white', 'alb', 'pink', 'roz']
        for color_term in color_terms:
            if color_term in query_lower and any(color_term in color for color in colors):
                score += 0.1
        
        # Description quality
        if metadata.get('has_description', False):
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _rerank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """Advanced reranking pentru rezultate optimale"""
        if not results:
            return results
        
        # Combine similarity and rank scores
        for result in results:
            # Weighted combination: 70% similarity, 30% business rules
            combined_score = (result.similarity * 0.7) + (result.rank_score * 0.3)
            result.rank_score = combined_score
        
        # Sort by combined score
        results.sort(key=lambda x: x.rank_score, reverse=True)
        
        return results
    
    def _create_cache_key(self, *args) -> str:
        """Creează cache key pentru query"""
        key_str = str(args)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _save_ultra_config(self):
        """Salvează configurația ULTRA"""
        config = {
            "ultra_config": {
                "collection_name": self.collection_name,
                "embedding_model": self.config.EMBEDDING_MODEL,
                "version": "3.0-ULTRA",
                "features_enabled": {
                    "multilingual_search": True,
                    "query_expansion": self.config.ENABLE_QUERY_EXPANSION,
                    "semantic_clustering": self.config.ENABLE_SEMANTIC_CLUSTERING,
                    "advanced_caching": self.config.ENABLE_CACHE,
                    "metadata_indexing": True,
                    "parallel_processing": True
                },
                "performance_settings": {
                    "batch_size": self.config.ULTRA_BATCH_SIZE,
                    "max_results": self.config.MAX_RESULTS,
                    "similarity_threshold": self.config.SIMILARITY_THRESHOLD,
                    "cache_size": self.config.CACHE_SIZE
                },
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "performance_stats": self.performance_stats,
            "metadata_index_stats": {
                "total_categories": len(self.metadata_index.get("by_category", {})),
                "total_flower_types": len(self.metadata_index.get("by_flower_type", {})),
                "total_occasions": len(self.metadata_index.get("by_occasions", {})),
                "total_colors": len(self.metadata_index.get("by_colors", {}))
            }
        }
        
        config_path = os.path.join(self.persist_directory, "ultra_config.json")
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 ULTRA config saved to {config_path}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Returnează statistici de performanță"""
        return {
            **self.performance_stats,
            "cache_size": len(self.query_cache),
            "cache_hit_rate": (self.performance_stats["cache_hits"] / max(self.performance_stats["total_queries"], 1)) * 100,
            "metadata_indexes": len(self.metadata_index),
            "database_size": self.collection.count() if self.collection else 0
        }
    
    def test_ultra_performance(self):
        """Test comprehensiv pentru performanță ULTRA"""
        logger.info("🧪 Starting ULTRA performance test...")
        
        test_queries = [
            "trandafiri roșii pentru iubire",
            "buchet wedding white roses",
            "bujori roz pentru aniversare", 
            "hydrangea blue arrangement",
            "difuzor aromă sensual",
            "luxury rose bouquet red",
            "cheap flowers birthday",
            "роза красная любовь"
        ]
        
        total_time = 0
        results_count = 0
        
        for i, query in enumerate(test_queries):
            start_time = time.time()
            results = self.ultra_search(query, max_results=5)
            query_time = time.time() - start_time
            
            total_time += query_time
            results_count += len(results)
            
            logger.info(f"Query {i+1}: '{query}' - {len(results)} results in {query_time:.3f}s")
            
            if results:
                best_result = results[0]
                logger.info(f"  Best: {best_result.text[:100]}... (score: {best_result.rank_score:.3f})")
        
        avg_time = total_time / len(test_queries)
        avg_results = results_count / len(test_queries)
        
        logger.info(f"🏆 ULTRA Performance Summary:")
        logger.info(f"  Average query time: {avg_time:.3f}s")
        logger.info(f"  Average results per query: {avg_results:.1f}")
        logger.info(f"  Total cache hits: {self.performance_stats['cache_hits']}")
        logger.info(f"  Cache hit rate: {(self.performance_stats['cache_hits'] / max(self.performance_stats['total_queries'], 1)) * 100:.1f}%")


def main():
    """Main function pentru ULTRA ChromaDB setup"""
    print("🚀 XOFlowers ChromaDB ULTRA OPTIMIZER v3.0")
    print("=" * 60)
    
    # Initialize ULTRA system
    ultra_db = XOFlowersUltraDB()
    
    # Load products with ULTRA optimizations
    print("🌸 Starting ULTRA loading process...")
    if ultra_db.ultra_load_products():
        print("✅ ULTRA loading successful!")
        
        # Performance test
        print("\n🧪 Running ULTRA performance tests...")
        ultra_db.test_ultra_performance()
        
        # Show final stats
        print("\n📊 Final ULTRA Statistics:")
        stats = ultra_db.get_performance_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n🎉 XOFlowers ULTRA ChromaDB is ready for production!")
        print("🔥 Maximum performance unlocked!")
        
    else:
        print("❌ ULTRA loading failed!")

if __name__ == "__main__":
    main()
