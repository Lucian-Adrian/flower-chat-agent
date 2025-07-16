#!/usr/bin/env python3
"""
Final Bot Launcher
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


if __name__ == "__main__":
    print("XOFlowers Telegram Bot")
    print("=" * 40)
    
    # Import and run
    try:
        from api.telegram_app import main_async
        
        print("Starting bot...")
        print("Bot is ready to receive messages!")
        print("Press Ctrl+C to stop")
        
        # Run the bot
        asyncio.run(main_async())
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()