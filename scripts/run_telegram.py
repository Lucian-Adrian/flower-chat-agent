#!/usr/bin/env python3
"""
XOFlowers Telegram Bot Runner
Runs the Telegram bot in a separate process
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables from the correct path
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def run_telegram_bot():
    """Run the Telegram bot"""
    try:
        print("🌸 XOFlowers Telegram Bot Starting...")
        print("📱 Platform: Telegram")
        print("🤖 AI Models: OpenAI + Gemini")
        print("💬 Polling: Active")
        print("-" * 50)
        
        from src.api.telegram_app import XOFlowersTelegramBot
        from telegram import Update
        
        bot = XOFlowersTelegramBot(debug=True)
        
        print("✅ Telegram bot initialized successfully")
        print("🔄 Starting polling...")
        
        # Run the bot using application.run_polling() directly
        bot.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Telegram bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting Telegram bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_telegram_bot()
