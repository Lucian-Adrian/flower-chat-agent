#!/usr/bin/env python3
"""
Простой запуск Telegram бота без лишних импортов
"""

import os
import sys
from pathlib import Path

# Добавляем корневую папку в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Тестируем импорты по частям"""
    print("🔧 Тестирование импортов...")
    
    try:
        print("1. Загружаем dotenv...")
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv загружен")
        
        print("2. Проверяем токен...")
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ TELEGRAM_BOT_TOKEN не найден!")
            return False
        print(f"✅ Токен найден: {token[:15]}...")
        
        print("3. Загружаем telegram...")
        from telegram import Bot
        print("✅ telegram загружен")
        
        print("4. Загружаем telegram.ext...")
        from telegram.ext import Application
        print("✅ telegram.ext загружен")
        
        print("5. Создаем Application...")
        app = Application.builder().token(token).build()
        print("✅ Application создан")
        
        print("6. Тестируем bot.get_me()...")
        import asyncio
        
        async def test_bot():
            async with app:
                me = await app.bot.get_me()
                print(f"✅ Бот подключен: {me.first_name} (@{me.username})")
                return True
        
        result = asyncio.run(test_bot())
        return result
        
    except Exception as e:
        print(f"❌ Ошибка при импорте: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()
