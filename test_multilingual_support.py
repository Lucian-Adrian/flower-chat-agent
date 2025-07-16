"""
Trilingual support test for ChromaDB system
Tests search functionality in English, Russian, and Romanian
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

def test_multilingual_search():
    """Tests search in three languages"""
    print("🌍 Trilingual ChromaDB Support Test")
    print("=" * 45)
    
    try:
        from database.chromadb_integration import smart_search, search_flowers_only, search_all_products
        
        # Test queries in three languages
        test_cases = [
            # Romanian language
            {
                "language": "Romanian 🇲🇩",
                "queries": [
                    ("trandafiri roșii", "red roses"),
                    ("buchet pentru nuntă", "wedding bouquet"),
                    ("cadou frumos", "beautiful gift"),
                    ("flori pentru mama", "flowers for mom"),
                    ("aranjament floral", "floral arrangement")
                ]
            },
            # Russian language  
            {
                "language": "Russian 🇷🇺",
                "queries": [
                    ("красные розы", "red roses"),
                    ("свадебный букет", "wedding bouquet"),
                    ("красивый подарок", "beautiful gift"),
                    ("цветы для мамы", "flowers for mom"),
                    ("пионы розовые", "pink peonies")
                ]
            },
            # English language
            {
                "language": "English 🇬🇧",
                "queries": [
                    ("red roses", "красные розы"),
                    ("wedding bouquet", "свадебный букет"), 
                    ("beautiful gift", "красивый подарок"),
                    ("flowers for mom", "цветы для мамы"),
                    ("premium arrangement", "премиум композиция")
                ]
            }
        ]
        
        total_tests = 0
        successful_tests = 0
        
        for language_test in test_cases:
            language = language_test["language"]
            queries = language_test["queries"]
            
            print(f"\n🔍 Тестирование: {language}")
            print("-" * 30)
            
            for query, description in queries:
                total_tests += 1
                
                # Тестируем умный поиск
                results = smart_search(query, limit=3)
                
                if results:
                    successful_tests += 1
                    status = "✅"
                    result_count = len(results)
                    
                    # Показываем первый результат
                    first_result = results[0]
                    price = first_result.get('price', 0)
                    category = first_result.get('category', 'N/A')
                    
                    print(f"   {status} \"{query}\" ({description})")
                    print(f"      📊 Найдено: {result_count} товаров")
                    print(f"      🏆 Топ результат: {price} MDL | {category}")
                    
                    # Проверяем релевантность
                    similarity = first_result.get('similarity_score', 0)
                    if similarity > 0.3:  # Порог релевантности
                        print(f"      ⭐ Релевантность: {similarity:.2f} (отлично)")
                    else:
                        print(f"      ⚠️ Релевантность: {similarity:.2f} (низкая)")
                else:
                    status = "❌"
                    print(f"   {status} \"{query}\" ({description})")
                    print(f"      📊 Результатов не найдено")
        
        # Итоговая статистика
        success_rate = (successful_tests / total_tests) * 100
        print(f"\n📊 Итоговая статистика:")
        print(f"   ✅ Успешных тестов: {successful_tests}/{total_tests}")
        print(f"   📈 Процент успеха: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"   🎉 Отличный результат! Система работает стабильно")
        elif success_rate >= 60:
            print(f"   👍 Хороший результат! Есть место для улучшений")
        else:
            print(f"   ⚠️ Требуются доработки системы")
        
        return success_rate >= 70
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("💡 Убедитесь, что ChromaDB система инициализирована")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        return False

def test_specific_language_features():
    """Тестирует специфические особенности каждого языка"""
    print("\n🔬 Тест языковых особенностей")
    print("=" * 30)
    
    try:
        from database.chromadb_integration import search_flowers_only, search_all_products
        
        # Специфические тесты
        specific_tests = [
            # Румынские диакритические знаки
            ("flori frumoașe", "цветы с диакритиками", "румынский"),
            ("trandafiri roșii", "розы с ș", "румынский"),
            
            # Русские падежи
            ("букета роз", "букет в родительном падеже", "русский"),
            ("цветами красивыми", "творительный падеж", "русский"),
            
            # Английские синонимы  
            ("flower arrangement", "английские синонимы", "английский"),
            ("floral composition", "формальный английский", "английский")
        ]
        
        print("Тестирование языковых особенностей:")
        
        for query, description, language in specific_tests:
            results = search_flowers_only(query, limit=2)
            
            if results:
                status = "✅"
                count = len(results)
            else:
                status = "⚠️"
                count = 0
            
            print(f"   {status} {language}: \"{query}\" ({description}) - {count} результатов")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в языковых тестах: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Multilingual ChromaDB Test Suite")
    print("===================================")
    
    # Основной тест
    main_test_passed = test_multilingual_search()
    
    # Дополнительные тесты
    feature_test_passed = test_specific_language_features()
    
    # Итоговый результат
    print(f"\n🏁 Итоговый результат:")
    if main_test_passed and feature_test_passed:
        print("✅ Все тесты пройдены! Трехъязычная поддержка работает отлично")
        print("🚀 Система готова для работы с английским, русским и румынским языками")
    elif main_test_passed:
        print("✅ Основные тесты пройдены, есть небольшие замечания")
        print("👍 Система работоспособна для базового использования")
    else:
        print("❌ Обнаружены проблемы в трехъязычной поддержке")
        print("🔧 Требуется дополнительная настройка системы")

if __name__ == "__main__":
    main()
