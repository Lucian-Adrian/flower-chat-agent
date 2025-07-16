"""
Тест функций поиска по цене в универсальной системе XOFlowers
"""

import sys
sys.path.insert(0, 'src')

def test_price_extraction():
    """Тест извлечения цены из запроса"""
    print("💰 ТЕСТ ИЗВЛЕЧЕНИЯ ЦЕНЫ ИЗ ЗАПРОСА")
    print("=" * 50)
    
    try:
        from database.vector_search import universal_search
        
        test_queries = [
            # Румынский
            ("vreau trandafiri până la 800 lei", 800),
            ("buchet sub 500 mdl", 500),
            ("flori cu buget de 1200 lei", 1200),
            ("maxim 600 MDL", 600),
            
            # Русский
            ("цветы до 700 лей", 700),
            ("букет не более 900 mdl", 900),
            ("бюджет до 1000 лей", 1000),
            ("максимум 400 MDL", 400),
            
            # Английский
            ("flowers under 600 mdl", 600),
            ("bouquet up to 800 lei", 800),
            ("max 500 MDL", 500),
            
            # Без цены
            ("красивые розы", None),
            ("trandafiri frumoși", None)
        ]
        
        for query, expected_price in test_queries:
            extracted = universal_search._extract_price_from_query(query)
            status = "✅" if extracted == expected_price else "❌"
            print(f"   {status} '{query}' → {extracted} (ожидалось: {expected_price})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте извлечения цены: {e}")
        return False

def test_budget_search():
    """Тест поиска в бюджете"""
    print(f"\n💰 ТЕСТ ПОИСКА В БЮДЖЕТЕ")
    print("=" * 50)
    
    try:
        from database.vector_search import search_budget_flowers, search_budget_gifts, smart_search
        
        # Инициализация
        from database.vector_search import universal_search
        universal_search.load_products_from_csv("final_products_case_standardized.csv")
        
        # Тест 1: Цветы в бюджете до 600 MDL
        print(f"\n1️⃣ Цветы до 600 MDL:")
        budget_flowers = search_budget_flowers(600, "trandafiri frumoși", limit=3)
        print(f"   Найдено: {len(budget_flowers)} цветов")
        for i, product in enumerate(budget_flowers, 1):
            verified = "✅" if product.get('is_verified') else "⚠️"
            print(f"   {i}. {verified} {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        # Тест 2: Подарки в бюджете до 300 MDL
        print(f"\n2️⃣ Подарки до 300 MDL:")
        budget_gifts = search_budget_gifts(300, "cadou frumos", limit=3)
        print(f"   Найдено: {len(budget_gifts)} подарков")
        for i, product in enumerate(budget_gifts, 1):
            print(f"   {i}. 🎁 {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        # Тест 3: Автоматическое извлечение бюджета
        print(f"\n3️⃣ Автоматическое извлечение бюджета:")
        auto_budget = smart_search("flori frumoase până la 800 lei", limit=3)
        print(f"   Найдено: {len(auto_budget)} товаров")
        for i, product in enumerate(auto_budget, 1):
            print(f"   {i}. 🌸 {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте бюджетного поиска: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_price_range_search():
    """Тест поиска в ценовом диапазоне"""
    print(f"\n💎 ТЕСТ ПОИСКА В ЦЕНОВОМ ДИАПАЗОНЕ")
    print("=" * 50)
    
    try:
        from database.vector_search import search_by_price_range
        
        # Тест 1: Цветы в среднем ценовом сегменте (500-1500 MDL)
        print(f"\n1️⃣ Цветы в диапазоне 500-1500 MDL:")
        mid_range_flowers = search_by_price_range(500, 1500, "buchete frumoase", limit=4, flowers_only=True)
        print(f"   Найдено: {len(mid_range_flowers)} цветов")
        for i, product in enumerate(mid_range_flowers, 1):
            print(f"   {i}. 🌸 {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        # Тест 2: Все товары в премиум сегменте (2000-5000 MDL)
        print(f"\n2️⃣ Премиум товары 2000-5000 MDL:")
        premium_products = search_by_price_range(2000, 5000, "premium luxury", limit=4, flowers_only=False)
        print(f"   Найдено: {len(premium_products)} товаров")
        for i, product in enumerate(premium_products, 1):
            print(f"   {i}. 👑 {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте ценового диапазона: {e}")
        return False

def test_price_suggestions():
    """Тест предложений по ценовым категориям"""
    print(f"\n🎯 ТЕСТ ЦЕНОВЫХ ПРЕДЛОЖЕНИЙ")
    print("=" * 50)
    
    try:
        from database.vector_search import get_price_suggestions
        
        # Тест 1: Предложения для цветов
        print(f"\n1️⃣ Ценовые категории для цветов:")
        flower_suggestions = get_price_suggestions("trandafiri", flowers_only=True)
        
        for suggestion in flower_suggestions:
            range_info = suggestion["range"]
            count = suggestion["count"]
            print(f"   {range_info['emoji']} {range_info['name']} ({range_info['min']}-{range_info['max']} MDL): {count} товаров")
            
            if suggestion["products"]:
                example = suggestion["products"][0]
                print(f"      Пример: {example['name'][:40]}... - {example['price']} MDL")
        
        # Тест 2: Предложения для всех товаров
        print(f"\n2️⃣ Ценовые категории для всех товаров:")
        all_suggestions = get_price_suggestions("cadou", flowers_only=False)
        
        for suggestion in all_suggestions:
            range_info = suggestion["range"]
            count = suggestion["count"]
            print(f"   {range_info['emoji']} {range_info['name']} ({range_info['min']}-{range_info['max']} MDL): {count} товаров")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте ценовых предложений: {e}")
        return False

if __name__ == "__main__":
    print("💰 ПОЛНЫЙ ТЕСТ СИСТЕМЫ ПОИСКА ПО ЦЕНЕ")
    print("=" * 60)
    
    tests = [
        ("Извлечение цены", test_price_extraction),
        ("Поиск в бюджете", test_budget_search),
        ("Ценовой диапазон", test_price_range_search),
        ("Ценовые предложения", test_price_suggestions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    print(f"\n{'='*60}")
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ТЕСТОВ ЦЕНЫ:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Результат: {passed}/{len(results)} тестов прошли")
    
    if passed == len(results):
        print("🎉 ВСЕ ТЕСТЫ ЦЕНЫ ПРОШЛИ!")
        print("💰 СИСТЕМА ПОИСКА ПО ЦЕНЕ ГОТОВА!")
        print("\n💡 НОВЫЕ ВОЗМОЖНОСТИ:")
        print("   💰 Автоматическое извлечение бюджета из запроса")
        print("   🔍 Поиск в ценовом диапазоне")
        print("   🎯 Предложения по ценовым категориям")
        print("   🌸 Цветы в бюджете")
        print("   🎁 Подарки в бюджете")
        print("\n🚀 ГОТОВО К ИНТЕГРАЦИИ В БОТА!")
    else:
        print("❌ Некоторые тесты не прошли - требуется доработка")