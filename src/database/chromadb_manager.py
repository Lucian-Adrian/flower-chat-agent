"""
ChromaDB Product Database Manager
System for creating and managing product database with embeddings
"""

import os
import csv
import logging
import traceback
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# ChromaDB and embeddings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Settings
from config.chromadb_settings import (
    EMBEDDING_MODEL, CHROMA_DB_DIR, CHROMA_SETTINGS,
    SEARCH_SETTINGS, TEXT_PROCESSING, VALIDATION,
    PRODUCT_CATEGORIES, FLORAL_CATEGORIES, ACCESSORY_CATEGORIES,
    get_csv_file, create_directories, get_category_type
)

class ChromaDBManager:
    """Manager for working with ChromaDB and embeddings"""
    
    def __init__(self):
        self.embedding_model = None
        self.chroma_client = None
        self.collections = {}
        self.logger = self._setup_logging()
        
        # Initialization
        create_directories()
        self._initialize_embedding_model()
        self._initialize_chroma_client()
        
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _initialize_embedding_model(self):
        """Initialize embedding model"""
        try:
            self.logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            self.logger.info("✅ Embedding model loaded")
        except Exception as e:
            self.logger.error(f"❌ Error loading embedding model: {e}")
            raise
    
    def _initialize_chroma_client(self):
        """Initialize ChromaDB client"""
        try:
            self.logger.info("Initializing ChromaDB client")
            self.chroma_client = chromadb.PersistentClient(
                path=str(CHROMA_DB_DIR),
                settings=Settings(anonymized_telemetry=False)
            )
            self.logger.info("✅ ChromaDB client initialized")
        except Exception as e:
            self.logger.error(f"❌ Error initializing ChromaDB: {e}")
            raise
    
    def create_embedding_function(self):
        """Создает функцию эмбеддингов для ChromaDB"""
        class SentenceTransformerEmbedding:
            def __init__(self, model):
                self.model = model
            
            def __call__(self, input):
                if isinstance(input, str):
                    input = [input]
                return self.model.encode(input).tolist()
            
            def name(self):
                return "sentence_transformers"
        
        return SentenceTransformerEmbedding(self.embedding_model)
    
    def get_or_create_collection(self, collection_name: str, recreate: bool = False):
        """Получает или создает коллекцию"""
        try:
            if recreate:
                try:
                    self.chroma_client.delete_collection(collection_name)
                    self.logger.info(f"🗑️ Удалена существующая коллекция: {collection_name}")
                except Exception:
                    pass
            
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.create_embedding_function(),
                metadata={"hnsw:space": CHROMA_SETTINGS["distance_metric"]}
            )
            
            self.collections[collection_name] = collection
            self.logger.info(f"✅ Коллекция готова: {collection_name}")
            return collection
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка создания коллекции {collection_name}: {e}")
            raise
    
    def prepare_product_text(self, product: Dict[str, Any]) -> str:
        """Подготавливает текст продукта для эмбеддинга"""
        text_parts = []
        
        # Основной текст
        if product.get('primary_text'):
            text_parts.append(product['primary_text'])
        
        # Категория
        if product.get('category'):
            text_parts.append(f"Категория: {product['category']}")
        
        # Тип цветка
        if product.get('flower_type'):
            text_parts.append(f"Тип: {product['flower_type']}")
        
        # Цена
        if product.get('price'):
            text_parts.append(f"Цена: {product['price']} MDL")
        
        combined_text = " | ".join(text_parts)
        
        # Ограничиваем длину
        max_length = TEXT_PROCESSING["max_description_length"]
        if len(combined_text) > max_length:
            combined_text = combined_text[:max_length] + "..."
        
        return combined_text
    
    def validate_product(self, product: Dict[str, Any]) -> bool:
        """Валидация продукта"""
        required_columns = VALIDATION["required_columns"]
        
        # Проверка обязательных полей
        for field in required_columns:
            if not product.get(field):
                return False
        
        # Проверка цены
        try:
            price = float(product.get('price', 0))
            if price < VALIDATION["min_price"] or price > VALIDATION["max_price"]:
                return False
        except (ValueError, TypeError):
            return False
        
        # Проверка категории
        if product.get('category') not in PRODUCT_CATEGORIES:
            return False
        
        return True
    
    def load_products_from_csv(self, csv_file_path: Optional[str] = None, recreate_collections: bool = False):
        """Загружает продукты из CSV в ChromaDB"""
        try:
            # Определяем файл
            if csv_file_path:
                csv_path = Path(csv_file_path)
            else:
                csv_path = get_csv_file()
            
            self.logger.info(f"📁 Загрузка из файла: {csv_path}")
            
            # Создаем коллекции
            flowers_collection = self.get_or_create_collection(
                CHROMA_SETTINGS["collection_name_flowers"], 
                recreate=recreate_collections
            )
            all_products_collection = self.get_or_create_collection(
                CHROMA_SETTINGS["collection_name_all"], 
                recreate=recreate_collections
            )
            
            # Счетчики
            total_products = 0
            valid_products = 0
            floral_products = 0
            
            # Подготовка данных для batch вставки
            batch_size = 100
            flowers_batch = {"ids": [], "documents": [], "metadatas": []}
            all_batch = {"ids": [], "documents": [], "metadatas": []}
            
            # Читаем CSV
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    total_products += 1
                    
                    # Валидация
                    if not self.validate_product(row):
                        continue
                    
                    valid_products += 1
                    
                    # Подготовка данных
                    product_id = row['chunk_id']
                    product_text = self.prepare_product_text(row)
                    
                    # Метаданные
                    metadata = {
                        'category': row['category'],
                        'price': float(row['price']),
                        'flower_type': row.get('flower_type', ''),
                        'url': row.get('url', ''),
                        'is_verified': row.get('is_verified', 'False').lower() == 'true',
                        'category_type': get_category_type(row['category'])
                    }
                    
                    # Добавляем во все продукты
                    all_batch["ids"].append(product_id)
                    all_batch["documents"].append(product_text)
                    all_batch["metadatas"].append(metadata.copy())
                    
                    # Добавляем в цветы если флоральная категория
                    if get_category_type(row['category']) == 'floral':
                        floral_products += 1
                        flowers_batch["ids"].append(product_id)
                        flowers_batch["documents"].append(product_text)
                        flowers_batch["metadatas"].append(metadata.copy())
                    
                    # Batch вставка
                    if len(all_batch["ids"]) >= batch_size:
                        self._insert_batch(all_products_collection, all_batch, "all_products")
                        all_batch = {"ids": [], "documents": [], "metadatas": []}
                    
                    if len(flowers_batch["ids"]) >= batch_size:
                        self._insert_batch(flowers_collection, flowers_batch, "flowers")
                        flowers_batch = {"ids": [], "documents": [], "metadatas": []}
            
            # Вставляем оставшиеся
            if all_batch["ids"]:
                self._insert_batch(all_products_collection, all_batch, "all_products")
            
            if flowers_batch["ids"]:
                self._insert_batch(flowers_collection, flowers_batch, "flowers")
            
            # Статистика
            self.logger.info(f"✅ Загрузка завершена:")
            self.logger.info(f"   📊 Всего продуктов: {total_products}")
            self.logger.info(f"   ✅ Валидных продуктов: {valid_products}")
            self.logger.info(f"   🌸 Флоральных продуктов: {floral_products}")
            
            return {
                'success': True,
                'total_products': total_products,
                'valid_products': valid_products,
                'floral_products': floral_products
            }
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка загрузки продуктов: {e}")
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _insert_batch(self, collection, batch_data, collection_type):
        """Вставляет batch данных в коллекцию"""
        try:
            collection.add(
                ids=batch_data["ids"],
                documents=batch_data["documents"],
                metadatas=batch_data["metadatas"]
            )
            self.logger.debug(f"✅ Вставлено {len(batch_data['ids'])} продуктов в {collection_type}")
        except Exception as e:
            self.logger.error(f"❌ Ошибка вставки batch в {collection_type}: {e}")
            raise
    
    def search_products(self, query: str, collection_name: str, limit: int = 5, 
                       price_min: Optional[float] = None, price_max: Optional[float] = None,
                       category_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Поиск продуктов в коллекции"""
        try:
            if collection_name not in self.collections:
                collection = self.get_or_create_collection(collection_name)
            else:
                collection = self.collections[collection_name]
            
            # Подготовка фильтров
            where_clause = {}
            
            # Обрабатываем фильтры цены отдельно для ChromaDB
            if price_min is not None and price_max is not None:
                where_clause["$and"] = [
                    {"price": {"$gte": price_min}},
                    {"price": {"$lte": price_max}}
                ]
            elif price_min is not None:
                where_clause["price"] = {"$gte": price_min}
            elif price_max is not None:
                where_clause["price"] = {"$lte": price_max}
            
            if category_filter:
                where_clause["category"] = {"$in": category_filter}
            
            # Поиск
            results = collection.query(
                query_texts=[query],
                n_results=min(limit, SEARCH_SETTINGS["max_limit"]),
                where=where_clause if where_clause else None
            )
            
            # Форматирование результатов
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    result = {
                        'id': results['ids'][0][i],
                        'name': doc,
                        'category': metadata.get('category', ''),
                        'price': metadata.get('price', 0),
                        'flower_type': metadata.get('flower_type', ''),
                        'url': metadata.get('url', ''),
                        'is_verified': metadata.get('is_verified', False),
                        'category_type': metadata.get('category_type', 'other'),
                        'distance': results['distances'][0][i] if results.get('distances') else 0
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка поиска в {collection_name}: {e}")
            return []
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Получает статистику коллекции"""
        try:
            if collection_name not in self.collections:
                collection = self.get_or_create_collection(collection_name)
            else:
                collection = self.collections[collection_name]
            
            count = collection.count()
            
            # Получаем примеры метаданных для анализа категорий
            sample = collection.get(limit=min(count, 1000))
            
            categories = set()
            price_range = {'min': float('inf'), 'max': 0}
            
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    if metadata.get('category'):
                        categories.add(metadata['category'])
                    
                    price = metadata.get('price', 0)
                    if price > 0:
                        price_range['min'] = min(price_range['min'], price)
                        price_range['max'] = max(price_range['max'], price)
            
            if price_range['min'] == float('inf'):
                price_range['min'] = 0
            
            return {
                'collection_name': collection_name,
                'total_products': count,
                'categories': sorted(list(categories)),
                'categories_count': len(categories),
                'price_range': price_range
            }
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения статистики {collection_name}: {e}")
            return {'error': str(e)}
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Получает полную статистику всех коллекций"""
        try:
            flowers_stats = self.get_collection_stats(CHROMA_SETTINGS["collection_name_flowers"])
            all_stats = self.get_collection_stats(CHROMA_SETTINGS["collection_name_all"])
            
            return {
                'flowers_collection': flowers_stats,
                'all_products_collection': all_stats,
                'total_categories': len(PRODUCT_CATEGORIES),
                'floral_categories': len(FLORAL_CATEGORIES),
                'accessory_categories': len(ACCESSORY_CATEGORIES)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Ошибка получения общей статистики: {e}")
            return {'error': str(e)}

# Создаем глобальный экземпляр
chroma_manager = ChromaDBManager()

# Удобные функции для использования
def initialize_database(csv_file_path: Optional[str] = None, recreate: bool = False):
    """Инициализирует базу данных"""
    return chroma_manager.load_products_from_csv(csv_file_path, recreate)

def search_flowers(query: str, limit: int = 5, price_min: Optional[float] = None, 
                  price_max: Optional[float] = None):
    """Поиск только цветов"""
    return chroma_manager.search_products(
        query, CHROMA_SETTINGS["collection_name_flowers"], 
        limit, price_min, price_max, list(FLORAL_CATEGORIES)
    )

def search_all_products(query: str, limit: int = 5, price_min: Optional[float] = None,
                       price_max: Optional[float] = None):
    """Поиск по всем продуктам"""
    return chroma_manager.search_products(
        query, CHROMA_SETTINGS["collection_name_all"], 
        limit, price_min, price_max
    )

def get_database_stats():
    """Получает статистику базы данных"""
    return chroma_manager.get_all_stats()
