#!/usr/bin/env python3
"""
Launch the Enhanced XOFlowers Telegram Bot
Production-ready launcher with full monitoring
"""

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_production_logging():
    """Setup comprehensive logging for production"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/telegram_bot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for different components
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.INFO)
    logging.getLogger('src.intelligence.ai_engine').setLevel(logging.INFO)
    logging.getLogger('src.data.chromadb_client').setLevel(logging.INFO)
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Enhanced XOFlowers Telegram Bot starting...")
    return logger

async def run_enhanced_telegram_bot():
    """Run the enhanced Telegram bot with full monitoring"""
    
    logger = setup_production_logging()
    
    try:
        # Verify environment variables
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'GEMINI_API_KEY',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing environment variables: {missing_vars}")
        
        logger.info("✅ Environment variables verified")
        
        # Add current directory to Python path
        sys.path.append('.')
        
        # Import and run the enhanced bot
        from src.api.telegram_app import XOFlowersTelegramBot
        
        logger.info("🤖 Initializing Enhanced XOFlowers Telegram Bot...")
        
        bot = XOFlowersTelegramBot()
        
        logger.info("🚀 Starting enhanced bot with features:")
        logger.info("  ✅ Gemini AI Engine with ChromaDB integration")
        logger.info("  ✅ Intelligent product search")
        logger.info("  ✅ Price filtering and recommendations")
        logger.info("  ✅ Security validation system")
        logger.info("  ✅ Natural Romanian conversation")
        logger.info("  ✅ Context-aware responses")
        
        # Run the bot
        await bot.run()
        
        # Keep running
        logger.info("🌟 Enhanced Telegram Bot is now running!")
        logger.info("📱 Users can now:")
        logger.info("  • Search for products with natural language")
        logger.info("  • Get price-filtered recommendations")
        logger.info("  • Ask business questions") 
        logger.info("  • Have natural conversations in Romanian")
        
        # Keep the bot alive
        while True:
            await asyncio.sleep(3600)  # Sleep for 1 hour
            logger.info("💚 Bot heartbeat - Enhanced system running smoothly")
            
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Critical error in enhanced bot: {e}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Main entry point for enhanced bot launcher"""
    
    print("🌸 XOFlowers Enhanced Telegram Bot Launcher")
    print("=" * 50)
    print("🤖 Enhanced AI Features:")
    print("  ✅ Gemini 2.5 Flash AI Engine")
    print("  ✅ ChromaDB Product Search")
    print("  ✅ Price Filtering")
    print("  ✅ Security Validation")
    print("  ✅ Natural Romanian Responses")
    print("  ✅ Context-Aware Conversations")
    print("=" * 50)
    
    try:
        # Run the enhanced bot
        asyncio.run(run_enhanced_telegram_bot())
    except KeyboardInterrupt:
        print("\n🛑 Enhanced bot shutdown complete")
    except Exception as e:
        print(f"\n❌ Enhanced bot failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
