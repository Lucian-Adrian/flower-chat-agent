#!/usr/bin/env python3
"""
Fix Unicode Logging Issues
===========================

This script fixes the Unicode encoding issues in logging by:
1. Removing emoji characters from log messages
2. Setting up proper UTF-8 encoding for console output
3. Creating a clean launcher without Unicode issues
"""

import os
import sys
import re
from pathlib import Path

def remove_emojis_from_file(file_path):
    """Remove emoji characters from a Python file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove common emoji patterns
    emoji_patterns = [
        r'✅',  # Check mark
        r'🚀',  # Rocket
        r'🌟',  # Star
        r'📱',  # Mobile phone
        r'🛍️',  # Shopping bag
        r'💡',  # Light bulb
        r'⚡',  # Lightning
        r'🔍',  # Magnifying glass
        r'💬',  # Speech bubble
        r'🎯',  # Target
        r'📊',  # Bar chart
        r'🔧',  # Wrench
        r'⚙️',   # Gear
        r'🎨',  # Artist palette
        r'📝',  # Memo
        r'🎉',  # Party popper
        r'🎊',  # Confetti ball
    ]
    
    # Replace emojis with simple text equivalents
    replacements = {
        r'✅': '[OK]',
        r'🚀': '[LAUNCH]',
        r'🌟': '[STAR]',
        r'📱': '[MOBILE]',
        r'🛍️': '[SHOP]',
        r'💡': '[IDEA]',
        r'⚡': '[FAST]',
        r'🔍': '[SEARCH]',
        r'💬': '[CHAT]',
        r'🎯': '[TARGET]',
        r'📊': '[CHART]',
        r'🔧': '[TOOL]',
        r'⚙️': '[GEAR]',
        r'🎨': '[ART]',
        r'📝': '[NOTE]',
        r'🎉': '[PARTY]',
        r'🎊': '[CONFETTI]',
    }
    
    modified_content = content
    for emoji, replacement in replacements.items():
        modified_content = modified_content.replace(emoji, replacement)
    
    return modified_content

def main():
    """Fix Unicode issues in the launcher"""
    base_dir = Path(__file__).parent
    
    # Files to fix
    files_to_fix = [
        base_dir / "launch_enhanced_telegram_bot.py",
        base_dir / "src" / "api" / "telegram_app.py"
    ]
    
    print("Fixing Unicode encoding issues...")
    
    for file_path in files_to_fix:
        if file_path.exists():
            print(f"Processing: {file_path}")
            
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            if not backup_path.exists():
                content = file_path.read_text(encoding='utf-8')
                backup_path.write_text(content, encoding='utf-8')
                print(f"  Created backup: {backup_path}")
            
            # Fix the file
            fixed_content = remove_emojis_from_file(file_path)
            file_path.write_text(fixed_content, encoding='utf-8')
            print(f"  Fixed Unicode issues in: {file_path}")
    
    print("\nCreating Unicode-safe launcher...")
    
    # Create a new launcher without Unicode issues
    safe_launcher_content = '''#!/usr/bin/env python3
"""
Enhanced Telegram Bot Launcher (Unicode-Safe)
=============================================

Safe launcher for the enhanced XOFlowers Telegram bot without Unicode issues.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

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

async def run_enhanced_telegram_bot():
    """Run the enhanced Telegram bot"""
    try:
        from api.telegram_app import TelegramApp
        
        # Initialize and start the bot
        app = TelegramApp()
        await app.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

def main():
    """Main entry point"""
    global logger
    logger = setup_safe_logging()
    
    logger.info("[LAUNCH] Starting enhanced bot with features:")
    logger.info("  [OK] Gemini AI Engine with ChromaDB integration")
    logger.info("  [OK] Intelligent product search")
    logger.info("  [OK] Price filtering and recommendations")
    logger.info("  [OK] Security validation system")
    logger.info("  [OK] Natural Romanian conversation")
    logger.info("  [OK] Context-aware responses")
    logger.info("")
    logger.info("[STAR] Enhanced Telegram Bot is now running!")
    logger.info("[MOBILE] Users can now:")
    logger.info("  • Search for products with natural language")
    logger.info("  • Get price-filtered recommendations")
    logger.info("  • Ask business questions")
    logger.info("  • Have natural conversations in Romanian")
    logger.info("")
    
    # Run the bot
    asyncio.run(run_enhanced_telegram_bot())

if __name__ == "__main__":
    main()
'''
    
    safe_launcher_path = base_dir / "launch_safe_telegram_bot.py"
    safe_launcher_path.write_text(safe_launcher_content, encoding='utf-8')
    print(f"Created: {safe_launcher_path}")
    
    print("\nUnicode fix complete!")
    print("\nTo run the bot without Unicode issues, use:")
    print("  python launch_safe_telegram_bot.py")
    print("\nThe original files have been backed up with .backup extension.")

if __name__ == "__main__":
    main()
