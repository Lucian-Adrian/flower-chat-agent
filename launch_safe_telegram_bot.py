#!/usr/bin/env python3
"""
Enhanced Telegram Bot Launcher (Unicode-Safe)
=============================================

Safe launcher for the enhanced XOFlowers Telegram bot without Unicode issues.
This version removes emoji characters that cause encoding errors on Windows.
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

def setup_safe_logging():
    """Setup logging that works with Windows console"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging with safe format
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "enhanced_bot.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def verify_environment():
    """Verify all required environment variables and dependencies"""
    logger = logging.getLogger(__name__)
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'GEMINI_API_KEY', 
        'OPENAI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("[OK] All environment variables found")
    return True

async def run_enhanced_telegram_bot():
    """Run the enhanced Telegram bot"""
    logger = logging.getLogger(__name__)
    
    try:
        # Import and initialize the bot
        from src.api.telegram_app import XOFlowersTelegramBot
        
        logger.info("[ROBOT] Initializing Enhanced XOFlowers Telegram Bot...")
        
        bot = XOFlowersTelegramBot()
        
        logger.info("[LAUNCH] Starting enhanced bot with features:")
        logger.info("  [OK] Gemini AI Engine with ChromaDB integration")
        logger.info("  [OK] Intelligent product search")
        logger.info("  [OK] Price filtering and recommendations")
        logger.info("  [OK] Security validation system")
        logger.info("  [OK] Natural Romanian conversation")
        logger.info("  [OK] Context-aware responses")
        
        # Run the bot
        await bot.run()
        
        # Keep running
        logger.info("[STAR] Enhanced Telegram Bot is now running!")
        logger.info("[MOBILE] Users can now:")
        logger.info("  • Search for products with natural language")
        logger.info("  • Get price-filtered recommendations")
        logger.info("  • Ask business questions")
        logger.info("  • Have natural conversations in Romanian")
        
        # Keep the bot running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("[STOP] Bot stopped by user")
    except Exception as e:
        logger.error(f"[ERROR] Failed to start bot: {e}")
        raise

def main():
    """Main entry point"""
    # Setup safe logging
    logger = setup_safe_logging()
    
    logger.info("=" * 60)
    logger.info("XOFlowers Enhanced Telegram Bot - Unicode Safe Launcher")
    logger.info("=" * 60)
    
    # Verify environment
    if not verify_environment():
        logger.error("[ERROR] Environment verification failed!")
        sys.exit(1)
    
    logger.info("[INIT] Environment verified successfully")
    logger.info("[INIT] Starting enhanced AI-powered Telegram bot...")
    
    # Run the bot
    try:
        asyncio.run(run_enhanced_telegram_bot())
    except KeyboardInterrupt:
        logger.info("[STOP] Bot shutdown complete")
    except Exception as e:
        logger.error(f"[FATAL] Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
