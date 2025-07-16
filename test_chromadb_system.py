"""
Простой тест ChromaDB системы
Проверяет основную функциональность без сложных зависимостей
"""

import os
import csv
import sys
from pathlib import Path

def test_csv_reading():
    """Тестирует чтение CSV файла и извлечение категорий"""
    print("📁 Тест чтения CSV файла...")
    
    csv_file = Path("data/final_products_case_standardized.csv")
    
    if not csv_file.exists():
        print(f"❌ CSV файл не найден: {csv_file}")
        return False
    
    try:
        categories = set()
        total_products = 0
        valid_products = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                total_products += 1
                
                # Проверяем обязательные поля
                if row.get('chunk_id') and row.get('primary_text') and row.get('category') and row.get('price'):
                    valid_products += 1
                    categories.add(row['category'])
        
        print(f"✅ CSV файл прочитан:")
        print(f"   📊 Всего продуктов: {total_products}")
        print(f"   ✅ Валидных продуктов: {valid_products}")
        print(f"   📂 Уникальных категорий: {len(categories)}")
        
        print(f"\n📂 Категории:")
        for i, category in enumerate(sorted(categories), 1):
            print(f"   {i:2d}. {category}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка чтения CSV: {e}")
        return False

def test_config_files():
    """Тестирует существование конфигурационных файлов"""
    print("\n⚙️ Тест конфигурационных файлов...")
    
    config_files = [
        "config/chromadb_settings.py",
        "src/database/chromadb_manager.py",
        "src/database/chromadb_integration.py",
        "initialize_chromadb.py"
    ]
    
    all_exist = True
    
    for file_path in config_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - не найден")
            all_exist = False
    
    return all_exist

def create_minimal_test():
    """Создает минимальный тест без внешних зависимостей"""
    print("\n🧪 Создание минимального теста...")
    
    # Проверяем импорты настроек
    try:
        sys.path.append(str(Path.cwd()))
        from config.chromadb_settings import (
            PRODUCT_CATEGORIES, FLORAL_CATEGORIES, 
            EMBEDDING_MODEL, get_csv_file
        )
        
        print(f"✅ Настройки загружены:")
        print(f"   🔧 Модель эмбеддингов: {EMBEDDING_MODEL}")
        print(f"   📂 Всего категорий: {len(PRODUCT_CATEGORIES)}")
        print(f"   🌸 Флоральных категорий: {len(FLORAL_CATEGORIES)}")
        
        # Проверяем файл CSV
        csv_path = get_csv_file()
        print(f"   📁 CSV файл: {csv_path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта настроек: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка в минимальном тесте: {e}")
        return False

def check_dependencies():
    """Проверяет доступность зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    dependencies = {
        'chromadb': 'ChromaDB для векторной базы данных',
        'sentence_transformers': 'Sentence Transformers для эмбеддингов',
        'torch': 'PyTorch для нейронных сетей',
        'numpy': 'NumPy для численных вычислений'
    }
    
    available = {}
    
    for dep, description in dependencies.items():
        try:
            __import__(dep)
            print(f"✅ {dep} - {description}")
            available[dep] = True
        except ImportError:
            print(f"❌ {dep} - {description} (не установлен)")
            available[dep] = False
    
    return available

def generate_installation_instructions():
    """Генерирует инструкции по установке"""
    print("\n📋 Инструкции по установке:")
    print("=" * 50)
    
    print("1. Активируйте виртуальное окружение:")
    print("   .\\venv\\Scripts\\Activate.ps1")
    
    print("\n2. Установите зависимости:")
    print("   pip install -r requirements.txt")
    
    print("\n3. Альтернативная установка (если есть проблемы):")
    print("   pip install chromadb sentence-transformers torch numpy")
    
    print("\n4. Запустите инициализацию:")
    print("   python initialize_chromadb.py")
    
    print("\n5. Для интеграции с существующей системой:")
    print("   Используйте src/database/chromadb_integration.py")

def main():
    """Основная функция тестирования"""
    print("🧪 ChromaDB System Test")
    print("=" * 30)
    
    # Переходим в директорию проекта
    os.chdir(Path(__file__).parent)
    
    tests_passed = 0
    total_tests = 0
    
    # Тест 1: Чтение CSV
    total_tests += 1
    if test_csv_reading():
        tests_passed += 1
    
    # Тест 2: Конфигурационные файлы
    total_tests += 1
    if test_config_files():
        tests_passed += 1
    
    # Тест 3: Минимальный тест
    total_tests += 1
    if create_minimal_test():
        tests_passed += 1
    
    # Проверка зависимостей
    available_deps = check_dependencies()
    dependencies_ready = all(available_deps.values())
    
    # Результаты
    print(f"\n📊 Результаты тестирования:")
    print(f"   ✅ Пройдено тестов: {tests_passed}/{total_tests}")
    print(f"   📦 Зависимости готовы: {'Да' if dependencies_ready else 'Нет'}")
    
    if tests_passed == total_tests and dependencies_ready:
        print("\n🎉 Система готова к работе!")
        print("   Запустите: python initialize_chromadb.py")
    elif tests_passed == total_tests:
        print("\n⚠️ Файлы готовы, но нужно установить зависимости")
        generate_installation_instructions()
    else:
        print("\n❌ Есть проблемы с файлами системы")
        print("   Проверьте пути и содержимое файлов")

if __name__ == "__main__":
    main()
