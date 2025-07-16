"""
ChromaDB integration with existing search system
Ensures compatibility with current Intent and search functions
"""

import sys
import traceback
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add src to path if needed
sys.path.append(str(Path(__file__).parent / "src"))

class ChromaDBIntegration:
    """ChromaDB integration class with existing system"""
    
    def __init__(self):
        self.chroma_manager = None
        self.is_initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialize ChromaDB manager"""
        try:
            from database.chromadb_manager import chroma_manager
            self.chroma_manager = chroma_manager
            self.is_initialized = True
            print("✅ ChromaDB integration initialized")
        except ImportError as e:
            print(f"⚠️ ChromaDB unavailable: {e}")
            self.is_initialized = False
        except Exception as e:
            print(f"❌ ChromaDB initialization error: {e}")
            self.is_initialized = False
    
    def smart_search(self, query: str, limit: int = 5, budget: Optional[float] = None,
                    price_min: Optional[float] = None, price_max: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Smart search - automatically determines search type
        Compatible with existing smart_search function
        """
        if not self.is_initialized:
            return []
        
        try:
            # Determine search type by keywords (English, Russian, Romanian)
            flower_keywords = [
                'букет', 'bouquet', 'buchet', 'цветы', 'flori', 'flowers',
                'роза', 'rose', 'trandafir', 'пион', 'peony', 'bujor',
                'свадебный', 'wedding', 'nunta', 'невеста', 'bride', 'mireasa',
                'композиция', 'composition', 'aranjament', 'композиции', 'arrangements'
            ]
            
            query_lower = query.lower()
            is_flower_query = any(keyword in query_lower for keyword in flower_keywords)
            
            # Use budget as price_max if not specified
            effective_price_max = price_max or budget
            
            if is_flower_query:
                return self.search_flowers_only(query, limit, price_min, effective_price_max)
            else:
                return self.search_all_products(query, limit, price_min, effective_price_max)
                
        except Exception as e:
            print(f"❌ Error in smart_search: {e}")
            return []
    
    def search_flowers_only(self, query: str, limit: int = 5, 
                           price_min: Optional[float] = None, price_max: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Поиск только цветов
        Совместим с существующей функцией search_flowers_only
        """
        if not self.is_initialized:
            return []
        
        try:
            from database.chromadb_manager import search_flowers
            results = search_flowers(query, limit, price_min, price_max)
            return self._format_results_for_compatibility(results)
        except Exception as e:
            print(f"❌ Ошибка в search_flowers_only: {e}")
            return []
    
    def search_all_products(self, query: str, limit: int = 5,
                           price_min: Optional[float] = None, price_max: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Поиск по всем товарам
        Совместим с существующей функцией search_all_products
        """
        if not self.is_initialized:
            return []
        
        try:
            from database.chromadb_manager import search_all_products
            results = search_all_products(query, limit, price_min, price_max)
            return self._format_results_for_compatibility(results)
        except Exception as e:
            print(f"❌ Ошибка в search_all_products: {e}")
            return []
    
    def search_budget_flowers(self, budget: float, query: str = "flori frumoase", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Поиск цветов в бюджете
        Совместим с существующей функцией search_budget_flowers
        """
        return self.search_flowers_only(query, limit, price_max=budget)
    
    def search_budget_gifts(self, budget: float, query: str = "cadou frumos", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Поиск подарков в бюджете
        Совместим с существующей функцией search_budget_gifts
        """
        return self.search_all_products(query, limit, price_max=budget)
    
    def search_gifts_and_accessories(self, query: str, limit: int = 5, budget: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Поиск подарков и аксессуаров
        Совместим с существующей функцией search_gifts_and_accessories
        """
        return self.search_all_products(query, limit, price_max=budget)
    
    def _format_results_for_compatibility(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Форматирует результаты для совместимости с существующей системой
        """
        formatted_results = []
        
        for result in results:
            # Приводим к формату, ожидаемому существующей системой
            formatted_result = {
                'id': result.get('id', ''),
                'name': result.get('name', ''),
                'category': result.get('category', ''),
                'price': result.get('price', 0),
                'flower_type': result.get('flower_type', ''),
                'url': result.get('url', ''),
                'is_verified': result.get('is_verified', False),
                'source': 'chromadb',  # Указываем источник
                'similarity_score': 1.0 - result.get('distance', 0),  # Преобразуем distance в similarity
                'category_type': result.get('category_type', 'other')
            }
            formatted_results.append(formatted_result)
        
        return formatted_results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получает статистику системы
        Совместим с существующей функцией get_stats
        """
        if not self.is_initialized:
            return {'error': 'ChromaDB не инициализирован'}
        
        try:
            from database.chromadb_manager import get_database_stats
            stats = get_database_stats()
            
            if 'error' in stats:
                return stats
            
            # Форматируем для совместимости
            flowers_stats = stats.get('flowers_collection', {})
            all_stats = stats.get('all_products_collection', {})
            
            return {
                'total_products': all_stats.get('total_products', 0),
                'flower_products': flowers_stats.get('total_products', 0),
                'verified_products': all_stats.get('total_products', 0),  # В ChromaDB все проверенные
                'functional_urls': all_stats.get('total_products', 0),
                'categories_count': all_stats.get('categories_count', 0),
                'categories': all_stats.get('categories', []),
                'price_range': all_stats.get('price_range', {}),
                'source': 'chromadb'
            }
            
        except Exception as e:
            return {'error': f'Ошибка получения статистики: {e}'}

# Create global integration instance
chromadb_integration = ChromaDBIntegration()

# Export functions for compatibility with existing system
def smart_search(query: str, limit: int = 5, budget: Optional[float] = None,
                price_min: Optional[float] = None, price_max: Optional[float] = None) -> List[Dict[str, Any]]:
    """Smart search - automatically determines type with price support"""
    return chromadb_integration.smart_search(query, limit, budget, price_min, price_max)

def search_flowers_only(query: str, limit: int = 5, budget: Optional[float] = None,
                       price_min: Optional[float] = None, price_max: Optional[float] = None) -> List[Dict[str, Any]]:
    """Search flowers only with price filter"""
    effective_price_max = price_max or budget
    return chromadb_integration.search_flowers_only(query, limit, price_min, effective_price_max)

def search_all_products(query: str, limit: int = 5, budget: Optional[float] = None,
                       price_min: Optional[float] = None, price_max: Optional[float] = None) -> List[Dict[str, Any]]:
    """Search all products with price filter"""
    effective_price_max = price_max or budget
    return chromadb_integration.search_all_products(query, limit, price_min, effective_price_max)

def search_gifts_and_accessories(query: str, limit: int = 5, budget: Optional[float] = None) -> List[Dict[str, Any]]:
    """Search gifts and accessories with budget"""
    return chromadb_integration.search_gifts_and_accessories(query, limit, budget)

def search_budget_flowers(budget: float, query: str = "flori frumoase", limit: int = 10) -> List[Dict[str, Any]]:
    """Search flowers within budget"""
    return chromadb_integration.search_budget_flowers(budget, query, limit)

def search_budget_gifts(budget: float, query: str = "cadou frumos", limit: int = 10) -> List[Dict[str, Any]]:
    """Search gifts within budget"""
    return chromadb_integration.search_budget_gifts(budget, query, limit)

def get_stats() -> Dict[str, Any]:
    """Get system statistics"""
    return chromadb_integration.get_stats()

# Alias for compatibility
universal_search = chromadb_integration
