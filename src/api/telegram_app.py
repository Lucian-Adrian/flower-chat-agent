#!/usr/bin/env python3
"""
Enhanced XOFlowers Telegram Bot
Advanced conversational AI with context awareness and personalization
"""

import os
import logging
import sys
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

# Add path to our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from intelligence.conversation_manager import get_conversation_manager
    from security.filters import SecurityFilter
    print("All modules imported successfully")
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all modules exist in the new structure")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class XOFlowersTelegramBot:
    """Enhanced Telegram Bot with AI-powered conversations"""

    def __init__(self):
        """Initialize the enhanced Telegram bot"""
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        self.application = Application.builder().token(token).build()
        self.conversation_manager = get_conversation_manager()
        self.security_filter = SecurityFilter()

        self.setup_handlers()
        logger.info("Enhanced XOFlowers Telegram Bot initialized successfully")

    def setup_handlers(self):
        """Setup all message and command handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("contact", self.contact_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /start command."""
        user = update.effective_user
        welcome_message = f"""**Bună, {user.first_name}!** 

Bine ați venit la XOFlowers! Sunt asistentul dumneavoastră virtual și vă pot ajuta să găsiți florile perfecte.

**Cum vă pot ajuta?**
- "Caut un buchet de trandafiri roșii."
- "Ce flori recomandați pentru o zi de naștere?"
- "Aveți buchete sub 500 de lei?"

Spuneți-mi cu ce vă pot ajuta astăzi!
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"Start command: {user.first_name} (ID: {user.id})")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles all text messages from the user."""
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text

        if not self.security_filter.is_safe_message(message_text):
            await update.message.reply_text("Vă rog să păstrăm o conversație politicoasă.")
            return

        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            response = await self.conversation_manager.handle_message(user_id, message_text)
            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Message from {user.first_name}: '{message_text}' -> Response generated")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await update.message.reply_text("Ne pare rău, am întâmpinat o eroare. Vă rugăm să încercați din nou.")

    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Contact information command"""
        contact_text = """
**Contact XOFlowers**

**Informații contact:**
• **Telefon:** +373 22 123 456
• **Email:** hello@xoflowers.md
• **Website:** www.xoflowers.md

**Locația magazinului:**
• Strada Florilor 25, Chișinău, Moldova
• Luni-Vineri: 9:00-20:00
• Sâmbătă: 10:00-18:00
• Duminică: 11:00-17:00
        """
        await update.message.reply_text(contact_text, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
**Ghid de utilizare XOFlowers Bot**

Puteți să-mi scrieți în limbaj natural despre ce flori căutați. De exemplu:
- "Vreau trandafiri roșii pentru Valentine's Day"
- "Caut buchete sub 500 MDL"
- "Arată-mi florile albe disponibile"

De asemenea, puteți folosi comenzile:
- /start - Pornire bot
- /contact - Informații de contact
- /help - Acest ghid
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log Errors caused by Updates."""
        logger.error(f"Update {update} caused error {context.error}")

    async def run(self):
        """Run the Telegram bot."""
        commands = [
            BotCommand("start", "Pornire bot și salut"),
            BotCommand("help", "Ghid de utilizare"),
            BotCommand("contact", "Informații contact"),
        ]
        await self.application.bot.set_my_commands(commands)
        
        logger.info("Starting bot...")
        
        # The following lines are adjusted to prevent event loop conflicts.
        # We initialize the application and then let the main script handle the event loop.
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()


async def main_async():
    """Main async function to run the bot"""
    try:
        bot = XOFlowersTelegramBot()
        await bot.run()
        # Keep the event loop running
        while True:
            await asyncio.sleep(3600) # Sleep for an hour, or use another way to keep the loop alive
    except (ValueError, KeyboardInterrupt) as e:
        logger.info(f"Bot stopped: {e}")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main_async())