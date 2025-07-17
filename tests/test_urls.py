#!/usr/bin/env python3
"""
Подробный тест URL в ConversationManager
"""

import sys
from pathlib import Path

# Добавляем корневую папку в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_url_display():
    """Тестируем отображение URL"""
    print("🧪 Тестирование отображения URL...")
    
    try:
        from src.intelligence.conversation_manager import get_conversation_manager
        
        manager = get_conversation_manager()
        print("✅ ConversationManager инициализирован")
        
        # Тестовый запрос
        query = "Хочу купить букет роз"
        print(f"\nЗапрос: '{query}'")
        
        response = manager.process_message_sync("test_user", query)
        print("\nПолный ответ:")
        print(response)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_display()
