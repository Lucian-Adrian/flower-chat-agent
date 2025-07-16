"""
ChromaDB initialization script for XOFlowers products
Creates and populates embedding database
"""

import sys
import os
import traceback
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    """Main initialization function"""
    print("🚀 Initializing ChromaDB for XOFlowers")
    print("=" * 50)
    
    try:
        # Импортируем после добавления пути
        from database.chromadb_manager import (
            initialize_database, 
            get_database_stats,
            search_flowers,
            search_all_products
        )
        
        print("📦 Модули успешно импортированы")
        
        # 1. Инициализация базы данных
        print("\n1️⃣ Создание и заполнение базы данных...")
        result = initialize_database(recreate=True)
        
        if not result.get('success'):
            print(f"❌ Ошибка инициализации: {result.get('error')}")
            return False
        
        print("✅ База данных создана и заполнена")
        print(f"   📊 Всего продуктов: {result['total_products']}")
        print(f"   ✅ Валидных: {result['valid_products']}")
        print(f"   🌸 Флоральных: {result['floral_products']}")
        
        # 2. Получение статистики
        print("\n2️⃣ Получение статистики...")
        stats = get_database_stats()
        
        if 'error' not in stats:
            print("✅ Статистика коллекций:")
            
            # Статистика цветов
            flowers_stats = stats.get('flowers_collection', {})
            print(f"   🌸 Коллекция цветов:")
            print(f"      - Продуктов: {flowers_stats.get('total_products', 0)}")
            print(f"      - Категорий: {flowers_stats.get('categories_count', 0)}")
            
            # Статистика всех продуктов
            all_stats = stats.get('all_products_collection', {})
            print(f"   🛍️ Все продукты:")
            print(f"      - Продуктов: {all_stats.get('total_products', 0)}")
            print(f"      - Категорий: {all_stats.get('categories_count', 0)}")
            
            # Ценовые диапазоны
            price_range = all_stats.get('price_range', {})
            if price_range:
                print(f"   💰 Ценовой диапазон: {price_range.get('min', 0):.0f} - {price_range.get('max', 0):.0f} MDL")
            
            # Категории
            categories = all_stats.get('categories', [])
            if categories:
                print(f"\n📂 Доступные категории ({len(categories)}):")
                for i, category in enumerate(categories, 1):
                    print(f"   {i:2d}. {category}")
        
        # 3. Тестирование поиска
        print("\n3️⃣ Тестирование поиска...")
        
        test_queries = [
            ("тандафири роșii", "Поиск красных роз"),
            ("cadou frumos", "Поиск красивых подарков"), 
            ("buchet pentru nuntă", "Свадебный букет"),
            ("difuzor aromă", "Ароматический диффузор"),
            ("peonii roz", "Розовые пионы")
        ]
        
        for query, description in test_queries:
            print(f"\n   🔍 {description} ({query}):")
            
            # Поиск в цветах
            flower_results = search_flowers(query, limit=2)
            print(f"      🌸 Цветы: {len(flower_results)} результатов")
            for result in flower_results:
                price = result.get('price', 0)
                category = result.get('category', 'N/A')
                verified = "✅" if result.get('is_verified') else "⚠️"
                name = result.get('name', '')[:60] + "..." if len(result.get('name', '')) > 60 else result.get('name', '')
                print(f"         {verified} {name}")
                print(f"             💰 {price} MDL | 📂 {category}")
            
            # Поиск во всех продуктах
            all_results = search_all_products(query, limit=2)
            print(f"      🛍️ Все товары: {len(all_results)} результатов")
            for result in all_results:
                price = result.get('price', 0)
                category = result.get('category', 'N/A')
                verified = "✅" if result.get('is_verified') else "⚠️"
                name = result.get('name', '')[:60] + "..." if len(result.get('name', '')) > 60 else result.get('name', '')
                print(f"         {verified} {name}")
                print(f"             💰 {price} MDL | 📂 {category}")
        
        # 4. Тестирование поиска с фильтрами цены
        print("\n4️⃣ Тестирование поиска с фильтрами цены...")
        
        budget_tests = [
            (500, "Бюджет до 500 MDL"),
            (1000, "Бюджет до 1000 MDL"),
            (2000, "Бюджет до 2000 MDL")
        ]
        
        for budget, description in budget_tests:
            print(f"\n   💰 {description}:")
            results = search_all_products("cadou frumos", limit=3, price_max=budget)
            print(f"      Найдено: {len(results)} товаров")
            for result in results:
                price = result.get('price', 0)
                category = result.get('category', 'N/A')
                name = result.get('name', '')[:50] + "..." if len(result.get('name', '')) > 50 else result.get('name', '')
                print(f"         💰 {price} MDL | 📂 {category} | {name}")
        
        print("\n🎉 Инициализация ChromaDB завершена успешно!")
        print("🚀 Система готова к работе")
        print("\n📋 Доступные функции:")
        print("   - search_flowers(query, limit, price_min, price_max)")
        print("   - search_all_products(query, limit, price_min, price_max)")
        print("   - get_database_stats()")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь, что установлены зависимости:")
        print("   pip install chromadb sentence-transformers")
        return False
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        traceback.print_exc()
        return False

def test_search_functions():
    """Дополнительные тесты поисковых функций"""
    print("\n🧪 Дополнительное тестирование...")
    
    try:
        from database.chromadb_manager import search_flowers, search_all_products
        
        # Тест многоязычности (английский, русский, румынский)
        multilingual_tests = [
            ("roses", "Английский"),
            ("trandafiri", "Румынский"),
            ("розы", "Русский")
        ]
        
        print("\n   🌍 Тест многоязычности:")
        for query, language in multilingual_tests:
            results = search_flowers(query, limit=1)
            status = "✅" if results else "❌"
            print(f"      {status} {language} ({query}): {len(results)} результатов")
        
        # Тест поиска по ценовым диапазонам
        print("\n   💰 Тест ценовых диапазонов:")
        price_ranges = [
            (0, 500, "Эконом"),
            (500, 1500, "Средний"),
            (1500, 5000, "Премиум"),
            (5000, None, "Люкс")
        ]
        
        for price_min, price_max, segment in price_ranges:
            results = search_all_products("букет", limit=1, price_min=price_min, price_max=price_max)
            status = "✅" if results else "❌"
            range_str = f"{price_min}-{price_max if price_max else '∞'}"
            print(f"      {status} {segment} ({range_str} MDL): {len(results)} результатов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в дополнительных тестах: {e}")
        return False

if __name__ == "__main__":
    print("ChromaDB Product Database Initializer")
    print("====================================")
    
    success = main()
    
    if success:
        test_search_functions()
        print("\n✅ Все тесты завершены")
    else:
        print("\n❌ Инициализация не удалась")
        sys.exit(1)
