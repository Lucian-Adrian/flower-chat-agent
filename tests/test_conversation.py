#!/usr/bin/env python3
"""
Тест улучшенного ConversationManager
"""

import sys
from pathlib import Path

# Добавляем корневую папку в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_conversation_manager():
    """Тестируем ConversationManager с различными запросами"""
    print("🧪 Тестирование улучшенного ConversationManager...")
    
    try:
        from src.intelligence.conversation_manager import get_conversation_manager
        
        manager = get_conversation_manager()
        print("✅ ConversationManager инициализирован")
        
        # Тестовые запросы
        test_queries = [
            "Привет я ищу букет для девушки",
            "Что вы мне можете предложить", 
            "Doresc un buchet pentru socia",
            "Flori",
            "Caut trandafiri roșii"
        ]
        
        print("\n🔍 Тестирование поисковых запросов:")
        print("=" * 50)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Запрос: '{query}'")
            try:
                response = manager.process_message_sync("test_user", query)
                print(f"Ответ: {response[:200]}...")
                print("-" * 30)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversation_manager()
