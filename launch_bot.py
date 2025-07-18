#!/usr/bin/env python3
"""
Simple XOFlowers Bot Launcher
=============================

Quick and easy way to start the enhanced XOFlowers Telegram bot.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging():
    """Setup simple logging"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def verify_environment():
    """Check required environment variables"""
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'GEMINI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("Please set them in your .env file")
        return False
    
    print("✅ Environment variables OK")
    return True

async def main():
    """Main function"""
    print("🌸 Starting XOFlowers Telegram Bot...")
    
    # Setup logging
    logger = setup_logging()
    
    # Verify environment
    if not verify_environment():
        sys.exit(1)
    
    # Import and run the bot
    try:
        from src.api.telegram_app import XOFlowersTelegramBot
        
        print("✅ Bot modules loaded successfully")
        print("🚀 Starting Telegram bot...")
        
        bot = XOFlowersTelegramBot()
        await bot.run()
        
        # Keep running
        print("✅ Bot is running! Press Ctrl+C to stop.")
        
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        logger.info("Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        logger.error(f"Error starting bot: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
