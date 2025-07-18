"""
XOFlowers ChromaDB Search Engine
Система поиска XOFlowers на основе ChromaDB

High-performance vector search engine with multilingual support
Высокопроизводительная система векторного поиска с многоязычной поддержкой
"""

import os
import csv
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

# === CONFIGURATION / КОНФИГУРАЦИЯ ===
class Config:
    # Embedding model / Модель эмбеддингов
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    
    # Paths / Пути
    BASE_DIR = Path(__file__).parent.parent.parent  # src/database -> src -> project_root
    DATA_CSV = BASE_DIR / "data" / "final_products_case_standardized.csv"
    CHROMA_DB = BASE_DIR / "chroma_db_flowers"
    
    # Categories / Категории
    FLOWER_CATEGORIES = {
        "Author'S Bouquets", "Classic Bouquets", "French Roses",
        "Mono/Duo Bouquets", "Basket / Boxes With Flowers",
        "Bride'S Bouquet", "Premium", "Peonies",
        "Mourning Flower Arrangement", "St. Valentine'S Day"
    }
    
    OTHER_CATEGORIES = {
        "Chando", "Soft Toys", "Greeting Card", 
        "Additional Accessories / Vases", "Sweets"
    }
    
    # Languages / Языки
    SUPPORTED_LANGUAGES = ["romanian", "russian", "english"]
    
    # Keywords for language detection / Ключевые слова для определения языка
    LANGUAGE_KEYWORDS = {
        'flowers': {
            'ro': ['flori', 'buchet', 'trandafiri', 'bujori'],
            'ru': ['цветы', 'букет', 'розы', 'пионы'],
            'en': ['flowers', 'bouquet', 'roses', 'peonies']
        }
    }

# === MAIN CLASS / ОСНОВНОЙ КЛАСС ===
class XOFlowersSearchEngine:
    def __init__(self):
        """Initialize the search engine / Инициализация поисковой системы"""
        self.config = Config()
        self.client = chromadb.PersistentClient(path=str(self.config.CHROMA_DB))
        self.model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        
        # Single collection for all products / Одна коллекция для всех товаров
        try:
            self.collection = self.client.create_collection("all_products")
        except Exception:
            self.collection = self.client.get_collection("all_products")
        
        print("✅ XOFlowers ChromaDB Search Engine initialized")
    
    def load_data(self):
        """Load all products from CSV / Загрузка всех продуктов из CSV"""
        if not self.config.DATA_CSV.exists():
            print(f"❌ CSV file not found: {self.config.DATA_CSV}")
            return False
        
        products = []
        categories_found = set()
        
        with open(self.config.DATA_CSV, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader, 1):
                if not self._is_valid_product(row):
                    continue
                
                category = row.get('category', '')
                categories_found.add(category)
                
                # Create product object / Создаем объект продукта
                product = {
                    'id': f'product_{i}',
                    'name': row.get('primary_text', '')[:200],
                    'category': category,
                    'price': self._parse_price(row.get('price', '0')),
                    'url': self._get_url(row),
                    'is_flower': category in self.config.FLOWER_CATEGORIES,
                    'search_text': self._create_search_text(row)
                }
                products.append(product)
        
        if products:
            self._save_to_db(products)
            print(f"✅ Loaded {len(products)} products")
            print(f"🌸 Flowers: {sum(1 for p in products if p['is_flower'])}")
            print(f"🎁 Others: {sum(1 for p in products if not p['is_flower'])}")
            print(f"📋 Categories: {sorted(categories_found)}")
            return True
        else:
            print("❌ No valid products found")
            return False
    
    def search(self, query, limit=10, flowers_only=False, max_price=None, language=None):
        """Universal search / Универсальный поиск"""
        try:
            # Auto-detect language / Автоопределение языка
            if not language:
                language = self._detect_language(query)
            
            # Enhance query with multilingual keywords / Улучшаем запрос многоязычными ключевыми словами
            enhanced_query = self._enhance_query(query, language)
            
            # Build filters / Строим фильтры
            where_filter = {}
            if flowers_only:
                where_filter["is_flower"] = True
            if max_price:
                where_filter["price"] = {"$lte": max_price}
            
            # Search / Поиск
            search_params = {
                'query_texts': [enhanced_query],
                'n_results': min(limit, 50)
            }
            if where_filter:
                search_params['where'] = where_filter
            
            results = self.collection.query(**search_params)
            return self._format_results(results)
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def search_flowers(self, query, limit=10, max_price=None):
        """Search only flowers / Поиск только цветов"""
        return self.search(query, limit, flowers_only=True, max_price=max_price)
    
    def search_with_budget(self, query, budget, limit=10):
        """Search within budget / Поиск в рамках бюджета"""
        return self.search(query, limit, max_price=budget)
    
    def get_stats(self):
        """Get database statistics / Получить статистику базы"""
        try:
            all_data = self.collection.get()
            total = len(all_data['ids']) if all_data['ids'] else 0
            
            flowers = 0
            categories = set()
            if all_data['metadatas']:
                for meta in all_data['metadatas']:
                    if meta.get('is_flower'):
                        flowers += 1
                    categories.add(meta.get('category', ''))
            
            return {
                'total_products': total,
                'flowers': flowers,
                'others': total - flowers,
                'categories': sorted(list(categories)),
                'categories_count': len(categories)
            }
        except Exception as e:
            return {'error': str(e)}
    
    # === PRIVATE METHODS / ПРИВАТНЫЕ МЕТОДЫ ===
    
    def _is_valid_product(self, row):
        """Validate product / Проверка продукта"""
        return (row.get('chunk_type') == 'product' and
                row.get('product_exists') == 'True' and
                row.get('primary_text', '').strip() and
                self._parse_price(row.get('price', '0')) > 0)
    
    def _parse_price(self, price_str):
        """Parse price / Парсинг цены"""
        if not price_str:
            return 0
        import re
        clean = re.sub(r'[^\d.]', '', str(price_str))
        try:
            return float(clean)
        except ValueError:
            return 0
    
    def _get_url(self, row):
        """Get best URL / Получить лучший URL"""
        for field in ['url', 'original_url', 'url_fixed']:
            url = row.get(field, '').strip()
            if url and url != 'True' and url != 'False':
                # Возвращаем URL как есть, без фильтрации
                return url
        return ""
    
    def _create_search_text(self, row):
        """Create searchable text / Создание текста для поиска"""
        parts = []
        
        # Main text / Основной текст
        if row.get('primary_text'):
            parts.append(row['primary_text'])
        
        # Category with multilingual keywords / Категория с многоязычными ключевыми словами
        category = row.get('category', '')
        if category:
            parts.append(category)
            # Add language variants / Добавляем языковые варианты
            if category in self.config.FLOWER_CATEGORIES:
                parts.extend(['flori', 'цветы', 'flowers', 'buchet', 'букет', 'bouquet'])
        
        # Flower type / Тип цветов
        if row.get('flower_type'):
            parts.append(row['flower_type'])
        
        # Price / Цена
        price = self._parse_price(row.get('price', '0'))
        if price > 0:
            parts.append(f"{price} MDL lei лей")
        
        return " | ".join(parts)
    
    def _detect_language(self, query):
        """Detect query language / Определение языка запроса"""
        query_lower = query.lower()
        
        # Simple language detection / Простое определение языка
        if any(word in query_lower for word in ['flori', 'buchet', 'lei']):
            return 'ro'
        elif any(word in query_lower for word in ['цветы', 'букет', 'лей']):
            return 'ru'
        else:
            return 'en'
    
    def _enhance_query(self, query, language):
        """Enhance query with keywords / Улучшение запроса ключевыми словами"""
        enhanced = query
        
        # Add cross-language flower keywords if flower-related / Добавляем кросс-языковые ключевые слова цветов
        flower_terms = ['flori', 'цветы', 'flowers', 'buchet', 'букет', 'bouquet']
        if any(term in query.lower() for term in flower_terms):
            enhanced += " " + " ".join(flower_terms)
        
        return enhanced
    
    def _format_results(self, results):
        """Format search results / Форматирование результатов"""
        products = []
        
        if results['documents'][0]:
            for i in range(len(results['documents'][0])):
                meta = results['metadatas'][0][i]
                
                product = {
                    'id': results['ids'][0][i],
                    'name': meta['name'],
                    'category': meta['category'],
                    'price': meta['price'],
                    'url': meta['url'],
                    'is_flower': meta['is_flower'],
                    'score': round(1 - results['distances'][0][i], 3)
                }
                products.append(product)
        
        return sorted(products, key=lambda x: x['score'], reverse=True)
    
    def _save_to_db(self, products):
        """Save products to ChromaDB / Сохранение продуктов в ChromaDB"""
        try:
            # Clear and recreate collection / Очистка и пересоздание коллекции
            self.client.delete_collection("all_products")
            self.collection = self.client.create_collection("all_products")
        except Exception:
            pass
        
        # Prepare data / Подготовка данных
        ids = [p['id'] for p in products]
        documents = [p['search_text'] for p in products]
        metadatas = [{
            'name': p['name'],
            'category': p['category'],
            'price': p['price'],
            'url': p['url'],
            'is_flower': p['is_flower']
        } for p in products]
        
        # Add to ChromaDB / Добавление в ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )


# === SEARCH ENGINE API / API ПОИСКОВОЙ СИСТЕМЫ ===
db = XOFlowersSearchEngine()

def load_products():
    """Load products / Загрузить продукты"""
    return db.load_data()

def search_products(query, limit=10):
    """Search all products / Поиск всех продуктов"""
    # Auto-load if empty / Автозагрузка если пусто
    stats = db.get_stats()
    if stats.get('total_products', 0) == 0:
        print("🔄 Auto-loading products...")
        db.load_data()
    
    return db.search(query, limit)

def search_flowers(query, limit=10):
    """Search flowers only / Поиск только цветов"""
    return db.search_flowers(query, limit)

def search_budget(query, budget, limit=10):
    """Search within budget / Поиск в рамках бюджета"""
    return db.search_with_budget(query, budget, limit)

def get_stats():
    """Get statistics / Получить статистику"""
    return db.get_stats()

# Auto-load on import / Автозагрузка при импорте
if __name__ == "__main__":
    load_products()
else:
    # Auto-load when imported / Автозагрузка при импорте
    try:
        stats = db.get_stats()
        if stats.get('total_products', 0) == 0:
            print("🔄 Auto-loading products on import...")
            db.load_data()
    except Exception as e:
        print(f"⚠️ Auto-load failed: {e}")
