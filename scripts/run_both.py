#!/usr/bin/env python3
"""
XOFlowers Dual Bot Runner
Runs both Telegram and Instagram bots simultaneously using threading
"""

import os
import sys
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load environment variables
load_dotenv()

def run_telegram_bot():
    """Run the Telegram bot in a separate thread"""
    try:
        print("🔵 [TELEGRAM] Starting Telegram bot...")
        
        from src.api.telegram_app import XOFlowersTelegramBot
        from telegram import Update
        
        bot = XOFlowersTelegramBot(debug=False)
        
        print("🔵 [TELEGRAM] Bot initialized, starting polling...")
        
        # Run the bot using application.run_polling() directly
        bot.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        print(f"🔴 [TELEGRAM] Error: {e}")
        import traceback
        traceback.print_exc()

def run_instagram_bot():
    """Run the Instagram bot in a separate thread"""
    try:
        print("🟣 [INSTAGRAM] Starting Instagram bot...")
        
        from src.api.instagram_app import XOFlowersInstagramBot
        
        app = XOFlowersInstagramBot(debug=False)
        
        print("🟣 [INSTAGRAM] Bot initialized, starting Flask server...")
        
        # Run the Flask app
        app.run(port=5001, debug=False, host='0.0.0.0', use_reloader=False)
        
    except Exception as e:
        print(f"🔴 [INSTAGRAM] Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to run both bots"""
    print("🌸 XOFlowers Dual Bot System Starting...")
    print("📱 Telegram: Polling mode")
    print("📸 Instagram: Webhook mode (port 5001)")
    print("🤖 AI Models: OpenAI + Gemini")
    print("=" * 60)
    
    try:
        # Create threads for both bots
        telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
        instagram_thread = threading.Thread(target=run_instagram_bot, daemon=True)
        
        # Start both threads
        telegram_thread.start()
        time.sleep(2)  # Give Telegram a moment to start
        instagram_thread.start()
        
        print("✅ Both bots started successfully!")
        print("🔵 Telegram bot: Running in polling mode")
        print("🟣 Instagram bot: Running on http://localhost:5001")
        print("💡 Remember to start ngrok for Instagram webhook!")
        print("⚠️  Press Ctrl+C to stop both bots")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping both bots...")
            
    except KeyboardInterrupt:
        print("\n👋 Bots stopped by user")
    except Exception as e:
        print(f"❌ Error running dual bot system: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
