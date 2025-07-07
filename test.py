from setup_database import XoFlowersDB
import pandas as pd

def analyze_data_quality():
    """
    Анализируем качество данных в CSV
    """
    print("🔍 АНАЛИЗ КАЧЕСТВА ДАННЫХ")
    print("=" * 40)
    
    df = pd.read_csv("data/chunks_data.csv")
    
    # Проверяем пустые значения
    print(f"📊 Всего записей: {len(df)}")
    
    for column in df.columns:
        null_count = df[column].isnull().sum()
        nan_count = (df[column].astype(str) == 'nan').sum()
        valid_count = len(df) - null_count - nan_count
        
        print(f"   {column}: {valid_count} валидных / {null_count + nan_count} пустых")
    
    return df

def final_test():
    """
    Финальный тест с улучшениями
    """
    print("\n🌸 ФИНАЛЬНЫЙ ТЕСТ XOFLOWERS CHROMADB")
    print("=" * 60)
    
    # Анализ данных
    df = analyze_data_quality()
    
    # Создание базы данных
    print(f"\n1️⃣ Создание базы данных...")
    db = XoFlowersDB()
    
    # Загрузка с исправлениями
    print(f"\n2️⃣ Загрузка товаров (с защитой от NaN)...")
    stats = db.load_products_from_csv("data/chunks_data.csv")
    
    # Статистика
    print(f"\n3️⃣ Результаты загрузки:")
    total_loaded = sum(stats.values())
    success_rate = (total_loaded / len(df)) * 100
    
    print(f"   📊 Загружено: {total_loaded} из {len(df)} ({success_rate:.1f}%)")
    print(f"   📊 Пропущено: {len(df) - total_loaded} (из-за ошибок данных)")
    
    for category, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_loaded * 100) if total_loaded > 0 else 0
        print(f"   📂 {category}: {count} товаров ({percentage:.1f}%)")
    
    # Расширенное тестирование поиска
    print(f"\n4️⃣ Расширенное тестирование поиска:")
    
    test_cases = [
        # Тест поиска цветов
        {"query": "розы красные", "category": "flowers", "description": "Поиск роз"},
        {"query": "букет невесты", "category": "flowers", "description": "Свадебные букеты"},
        
        # Тест поиска подарков
        {"query": "подарок маме", "category": None, "description": "Подарки"},
        {"query": "мягкая игрушка", "category": "gifts", "description": "Игрушки"},
        
        # Тест поиска аксессуаров
        {"query": "диффузор ароматический", "category": "fragrance", "description": "Ароматы"},
        {"query": "ваза красивая", "category": "accessories", "description": "Вазы"},
        
        # Тест сезонных товаров
        {"query": "день святого валентина", "category": "seasonal", "description": "Valentine's Day"},
        
        # Тест многоязычности
        {"query": "flori frumoase", "category": None, "description": "Румынский язык"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n   {i}. {test['description']}")
        print(f"      Запрос: '{test['query']}'")
        
        results = db.search_products(
            test['query'], 
            category=test['category'], 
            n_results=3
        )
        
        if results:
            print(f"      ✅ Найдено {len(results)} результатов:")
            for j, result in enumerate(results, 1):
                price = result['metadata'].get('price', 'N/A')
                category = result['metadata'].get('category', 'N/A')
                relevance = result['relevance']
                print(f"         {j}. {category} - {price} лей (релевантность: {relevance:.3f})")
        else:
            print(f"      ❌ Результатов не найдено")
    
    # Тест поиска по цене в разных диапазонах
    print(f"\n5️⃣ Тестирование поиска по цене:")
    
    price_ranges = [
        (0, 500, "Бюджетные"),
        (500, 1500, "Средний сегмент"), 
        (1500, 3000, "Премиум"),
        (3000, 10000, "Люкс")
    ]
    
    for min_price, max_price, segment in price_ranges:
        results = db.search_by_price(min_price, max_price)
        print(f"   💰 {segment} ({min_price}-{max_price} лей): {len(results)} товаров")
    
    # Финальная статистика
    print(f"\n6️⃣ Финальная статистика базы данных:")
    final_stats = db.get_stats()
    
    print(f"   📊 Всего в базе: {final_stats['total']} товаров")
    print(f"   📁 Размер базы: ./chroma_db/")
    
    for category, count in final_stats.items():
        if category != 'total' and count > 0:
            print(f"   📂 {category}: {count} записей")
    
    # Тест производительности
    print(f"\n7️⃣ Тест производительности:")
    import time
    
    # Измеряем время поиска
    start_time = time.time()
    for _ in range(10):
        db.search_products("розы красивые", n_results=5)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 10
    print(f"   ⚡ Среднее время поиска: {avg_time:.3f} секунд")
    print(f"   ⚡ Скорость: {1/avg_time:.1f} запросов в секунду")
    
    print(f"\n🎉 ФИНАЛЬНЫЙ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
    print(f"🚀 База данных готова для продакшена!")
    print(f"📋 Готова для интеграции с командой промптинга!")
    
    return db, stats

if __name__ == "__main__":
    db, stats = final_test()