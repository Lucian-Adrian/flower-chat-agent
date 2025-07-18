#!/usr/bin/env python3
"""
Enhanced XOFlowers Telegram Bot
Advanced conversational AI with context awareness and personalization
"""

import os
import logging
import sys
import asyncio
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

# Load environment variables FIRST (before importing our modules)
load_dotenv()

# Add path to our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.intelligence.ai_engine import process_message_ai, get_ai_engine
    from src.utils.system_definitions import get_service_config
    from src.utils.utils import setup_logger
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


class XOFlowersTelegramBot:
    """Enhanced Telegram Bot with AI-powered conversations"""

    def __init__(self):
        """Initialize the enhanced Telegram bot"""
        print("Initializing XOFlowers Telegram Bot...")
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        print("Creating Telegram application...")
        self.application = Application.builder().token(token).build()
        print("Modular components ready...")
        # No need for centralized manager - using modular approach

        print("Setting up handlers...")
        self.setup_handlers()
        logger.info("Enhanced XOFlowers Telegram Bot initialized successfully")
        print("Bot initialization complete!")

    def setup_handlers(self):
        """Setup all message and command handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("contact", self.contact_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.application.add_error_handler(self.error_handler)

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /start command with enhanced AI capabilities."""
        user = update.effective_user
        welcome_message = f"""🌸 **Bună, {user.first_name}!** 

Bine ați venit la XOFlowers - florăria cu AI inteligent! 

🤖 **Sunt asistentul dumneavoastră virtual cu căutare inteligentă și vă pot ajuta să găsiți florile perfecte.**

**Exemple de cum mă puteți folosi:**
🔍 "Caut un buchet de trandafiri roșii până în 800 lei"
🎉 "Ce flori recomandați pentru o nuntă?"
💐 "Vreau flori pentru mama, ceva elegant"
📞 "Care e programul vostru?"

**Capacități avansate:**
✅ Căutare inteligentă în catalogul nostru
✅ Filtrare după preț și categorie  
✅ Recomandări personalizate
✅ Conversație naturală în română

Spuneți-mi cu ce vă pot ajuta astăzi! 🌺
"""
        try:
            await update.message.reply_text(welcome_message, parse_mode='Markdown')
            logger.info(f"Enhanced start command: {user.first_name} (ID: {user.id})")
        except Exception as e:
            # Fallback without markdown if parsing fails
            simple_message = f"Bună, {user.first_name}! Bine ați venit la XOFlowers! Cum vă pot ajuta astăzi?"
            await update.message.reply_text(simple_message)
            logger.warning(f"Start command markdown failed, used simple text: {e}")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles all text messages using enhanced AI engine with full product integration."""
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text

        try:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
            
            # Step 1: Basic message validation
            if len(message_text) > 1000:
                await update.message.reply_text("Mesajul este prea lung. Vă rog să-l reduceți.")
                return
            
            # Step 2: Process message through ENHANCED AI engine
            try:
                logger.info(f"Processing message from {user.first_name} (ID: {user_id}): '{message_text[:50]}...'")
                
                # Process message using the enhanced Gemini+ChromaDB AI engine
                ai_result = await process_message_ai(
                    user_message=message_text,
                    user_id=user_id
                )
                
                if ai_result and ai_result.get('success') and ai_result.get('response'):
                    response = ai_result['response']
                    
                    # Log enhanced metrics
                    intent = ai_result.get('intent', 'unknown')
                    confidence = ai_result.get('confidence', 0)
                    products_found = ai_result.get('products_found', 0)
                    service_used = ai_result.get('service_used', 'unknown')
                    processing_time = ai_result.get('processing_time', 0)
                    
                    logger.info(f"[OK] Enhanced AI Response: intent={intent}, confidence={confidence:.2f}, "
                              f"products={products_found}, service={service_used}, time={processing_time:.2f}s")
                    
                    # Add product information context if available
                    if products_found > 0:
                        logger.info(f"[SHOP] Response includes context from {products_found} products")
                    
                    # Check if security blocked the message
                    if ai_result.get('security_blocked'):
                        risk_level = ai_result.get('risk_level', 'unknown')
                        logger.warning(f"[SHIELD] Security system blocked message - risk level: {risk_level}")
                
                else:
                    # Enhanced fallback with more context
                    intent = ai_result.get('intent', 'unknown') if ai_result else 'error'
                    response = "🌸 Bună ziua! Cum vă pot ajuta cu florile astăzi? Puteți să-mi spuneți ce căutați."
                    logger.warning(f"[WARNING] AI processing failed for intent: {intent}, using enhanced fallback")
                        
            except Exception as e:
                logger.error(f"[ERROR] Error in enhanced AI processing: {e}")
                response = "🌸 Îmi pare rău pentru întârziere. Sistem XOFlowers procesează cererea... Cu ce vă pot ajuta?"
            
            # Clean response for Telegram (remove problematic formatting)
            response = self._clean_response_for_telegram(response)
            
            # Create product buttons if products are available
            reply_markup = None
            if ai_result and ai_result.get('products'):
                products = ai_result.get('products', [])
                logger.info(f"[SHOP] Found {len(products)} products for buttons")
                
                # Debug: Log first product structure
                if products:
                    logger.debug(f"[SHOP] First product structure: {products[0]}")
                
                reply_markup = self._create_product_buttons(products, max_buttons=5)
                
                if reply_markup:
                    logger.info(f"[SHOP] Created product buttons successfully")
                else:
                    logger.warning(f"[SHOP] Failed to create product buttons despite having products")
            else:
                logger.info(f"[SHOP] No products available for buttons - ai_result has products: {ai_result.get('products') if ai_result else 'no ai_result'}")
            
            # Send response with retry logic
            try:
                await update.message.reply_text(
                    response, 
                    reply_markup=reply_markup
                )
                logger.info(f"[MOBILE] Response sent to {user.first_name} - length: {len(response)} chars")
                
                # Log if we included product buttons
                if reply_markup:
                    products_count = len(ai_result.get('products', []))
                    buttons_count = min(5, products_count)
                    logger.info(f"[SHOP] Sent {buttons_count} product buttons from {products_count} available products")
                    
            except Exception as send_error:
                logger.error(f"[ERROR] Failed to send response: {send_error}")
                # Fallback short response
                await update.message.reply_text("🌸 XOFlowers vă salută! Cu ce vă putem ajuta?")
            
        except Exception as e:
            logger.error(f"[ERROR] Critical error handling message: {e}")
            try:
                await update.message.reply_text("Ne pare rău pentru eroare. XOFlowers este mereu aici pentru dumneavoastră!")
            except:
                pass  # If even this fails, log it but don't crash

    def _clean_response_for_telegram(self, response: str) -> str:
        """Clean response text for Telegram compatibility"""
        # Remove problematic markdown and formatting
        cleaned = response.replace('**', '').replace('*', '').replace('_', '').replace('`', '')
        cleaned = cleaned.replace('```', '').replace('~~', '')
        
        # Ensure reasonable length for Telegram
        if len(cleaned) > 4000:
            cleaned = cleaned[:3900] + "...\n\n🌸 Pentru mai multe detalii, vă rugăm să ne contactați direct!"
        
        return cleaned.strip()

    def _create_product_buttons(self, products: list, max_buttons: int = 5) -> InlineKeyboardMarkup:
        """Create inline keyboard with product buttons"""
        if not products:
            return None
        
        keyboard = []
        
        # Add up to max_buttons products as buttons
        for i, product in enumerate(products[:max_buttons]):
            product_name = product.get('name', 'Produs')
            product_url = product.get('url', '')
            
            if product_url:
                # Create a shortened name for the button (max 30 chars)
                button_text = product_name[:27] + "..." if len(product_name) > 30 else product_name
                keyboard.append([InlineKeyboardButton(
                    text=f"🌸 {button_text}",
                    url=product_url
                )])
        
        # Add "View More Products" button if there are more products
        if len(products) > max_buttons:
            keyboard.append([InlineKeyboardButton(
                text=f"🛒 Vezi toate produsele ({len(products)} disponibile)",
                url="https://xoflowers.md"
            )])
        
        return InlineKeyboardMarkup(keyboard) if keyboard else None

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