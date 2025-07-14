#!/usr/bin/env python3
"""
XOFlowers Telegram Bot
Task Lucian: Conectează core_logic.py cu Telegram

Autor: Lucian (Webhook)
Data: 2025
"""

import os
import logging
import sys
from typing import Dict, List
import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    CallbackContext
)
from dotenv import load_dotenv
import json

# Adaugă calea către modulele noastre
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'intelligence'))

try:
    from core_logic import XOFlowersAI
except ImportError as e:
    print(f"❌ Eroare la importul core_logic: {e}")
    print("Asigură-te că core_logic.py există în src/intelligence/")
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
    """
    Botul Telegram pentru XOFlowers
    Conectează utilizatorii cu creierul AI prin Telegram
    """
    
    def __init__(self):
        # Token-ul botului
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN nu este setat în fișierul .env")
        
        # Inițializează AI-ul
        try:
            self.ai = XOFlowersAI()
            logger.info("✅ AI Core Logic inițializat cu succes")
        except Exception as e:
            logger.error(f"❌ Eroare la inițializarea AI: {e}")
            raise
        
        # Aplicația Telegram
        self.application = Application.builder().token(self.token).build()
        
        # Statistici
        self.user_stats = {}
        self.total_messages = 0
        
        # Configurează handler-ele
        self._setup_handlers()
        
        logger.info("🤖 XOFlowers Telegram Bot inițializat")
    
    def _setup_handlers(self):
        """
        Configurează toate handler-ele pentru comenzi și mesaje
        """
        # Comenzi
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("catalog", self.catalog_command))
        self.application.add_handler(CommandHandler("contact", self.contact_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        
        # Mesaje text (aici se întâmplă magia cu AI-ul)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
        
        # Handler pentru mesaje nesuportate
        self.application.add_handler(
            MessageHandler(filters.ALL, self.handle_unsupported)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler pentru comanda /start
        """
        user = update.effective_user
        user_id = str(user.id)
        
        # Înregistrează utilizatorul
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'name': user.first_name,
                'messages_count': 0,
                'started_at': update.message.date.isoformat()
            }
        
        welcome_message = f"""🌸 **Bună, {user.first_name}!** 🌸

Bun venit la XOFlowers - cel mai frumos magazin de flori din Moldova! 

Eu sunt asistentul tău virtual și sunt aici să te ajut să găsești florile perfecte pentru orice ocazie specială.

**Ce pot face pentru tine:**
🔍 Căutare flori după preferințe
💰 Recomandări în orice buget  
🎨 Filtrare după culori
🎉 Sugestii pentru ocazii speciale
📦 Detalii complete despre produse

**Începe pur și simplu să îmi spui ce cauți!**

*Exemple:*
• "Vreau trandafiri roșii pentru Valentine"
• "Caut buchete albe sub 1000 lei"
• "Am nevoie de flori pentru aniversare"

Să începem! Cu ce te pot ajuta? 😊"""
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown'
        )
        
        logger.info(f"👤 Utilizator nou: {user.first_name} (ID: {user_id})")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler pentru comanda /help
        """
        help_text = """🌸 **XOFlowers - Ghid de Utilizare** 🌸

**Comenzi disponibile:**
/start - Începe conversația
/help - Acest ghid
/catalog - Vezi categoriile noastre
/contact - Informații de contact
/stats - Statisticile tale

**Cum să cauți flori:**
Pur și simplu spune-mi ce vrei în limba română! Eu înțeleg:

🎨 **Culori:** "trandafiri roșii", "buchete albe"
💰 **Prețuri:** "sub 1000 lei", "între 500 și 1500 lei"
🌸 **Tipuri:** "bujori", "trandafiri", "crizanteme"
🎉 **Ocazii:** "pentru Valentine", "pentru aniversare"

**Exemple:**
• "Vreau ceva frumos pentru mama mea"
• "Buchete roșii și albe pentru nuntă"
• "Trandafiri ieftini pentru colega"
• "Cel mai scump buchet pe care îl aveți"

Sunt aici să te ajut să creezi momente magice! 🌹"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def catalog_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler pentru comanda /catalog
        """
        catalog_text = """🌸 **Catalogul XOFlowers** 🌸

**Categoriile noastre principale:**

🌹 **Trandafiri**
• Trandafiri roșii clasici
• Trandafiri albi eleganți
• Trandafiri roz romantici
• Buchete mixte de trandafiri

🌺 **Bujori**
• Bujori de sezon
• Aranjamente premium cu bujori
• Culori: roz, alb, coral

🌼 **Buchete Mixte**
• Combinații creative
• Pentru toate ocaziile
• Variate game de prețuri

🎁 **Premium & Luxury**
• Aranjamente exclusive
• Flori importate
• Pentru momente speciale

💍 **Pentru Ocazii**
• Valentine's Day
• Zilele de naștere
• Nunți și aniversări
• 8 Martie

Spune-mi ce te interesează și îți voi arăta opțiunile perfecte! 🌟"""
        
        await update.message.reply_text(catalog_text, parse_mode='Markdown')
    
    async def contact_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler pentru comanda /contact
        """
        contact_text = """📞 **Contactează XOFlowers** 📞

**🏪 Magazin Principal:**
📍 Chișinău, Moldova
⏰ Program: 08:00 - 20:00 (Lun-Dom)

**📱 Comandă Online:**
🌐 Website: xoflowers.md
📧 Email: comenzi@xoflowers.md
📲 WhatsApp: [Numărul de telefon]

**🚚 Livrare:**
🏃‍♂️ Livrare rapidă în Chișinău
🚗 Livrare în toată Moldova
⚡ Comenzi urgente acceptate

**💳 Modalități de Plată:**
💰 Numerar la livrare
💳 Card bancar
📱 Plați online

Pentru comenzi prin Telegram, spune-mi ce vrei și te voi ghida pas cu pas! 🌹

*Momentan sunt în versiunea de test - pentru comenzi finale te rog să folosești website-ul sau telefoanele oficiale.*"""
        
        await update.message.reply_text(contact_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler pentru comanda /stats
        """
        user_id = str(update.effective_user.id)
        
        if user_id in self.user_stats:
            stats = self.user_stats[user_id]
            stats_text = f"""📊 **Statisticile tale:**

👤 Nume: {stats['name']}
💬 Mesaje trimise: {stats['messages_count']}
📅 Membru din: {stats['started_at'][:10]}

📈 **Statistici generale:**
👥 Total utilizatori: {len(self.user_stats)}
💬 Total mesaje procesate: {self.total_messages}

Mulțumesc că folosești XOFlowers Bot! 🌸"""
        else:
            stats_text = "Nu am găsit statistici pentru tine. Scrie /start pentru a începe!"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler principal pentru mesajele text
        AICI SE CONECTEAZĂ CU CORE_LOGIC.PY!
        """
        user = update.effective_user
        user_id = str(user.id)
        user_message = update.message.text
        
        # Actualizează statisticile
        self.total_messages += 1
        if user_id in self.user_stats:
            self.user_stats[user_id]['messages_count'] += 1
        
        logger.info(f"👤 {user.first_name} (ID: {user_id}): {user_message}")
        
        try:
            # Indică că botul scrie (typing indicator)
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, 
                action='typing'
            )
            
            # AICI SE ÎNTÂMPLĂ MAGIA - Apelăm creierul AI!
            ai_response = self.ai.get_response(
                user_message=user_message,
                user_id=user_id
            )
            
            # Trimite răspunsul
            await update.message.reply_text(
                ai_response, 
                parse_mode='Markdown'
            )
            
            logger.info(f"🤖 Răspuns trimis către {user.first_name}")
            
        except Exception as e:
            logger.error(f"❌ Eroare la procesarea mesajului: {e}")
            
            error_message = """😔 Îmi pare rău, am întâmpinat o mică problemă tehnică.

Te rog să încerci din nou sau folosește comenzile:
/help - pentru ghidul de utilizare
/catalog - pentru a vedea categoriile
/contact - pentru informații de contact

Îmi pare rău pentru inconvenient! 🌸"""
            
            await update.message.reply_text(error_message)
    
    async def handle_unsupported(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler pentru mesaje nesuportate (poze, stickere, etc.)
        """
        unsupported_message = """🤖 Îmi pare rău, momentan pot răspunde doar la mesaje text.

Scrie-mi în cuvinte ce flori cauți și îți voi găsi exact ce ai nevoie! 🌸

Exemple:
• "Vreau trandafiri roșii"
• "Buchete pentru aniversare"
• "Ceva frumos sub 1000 lei"

Sau folosește /help pentru mai multe informații."""
        
        await update.message.reply_text(unsupported_message)
    
    async def set_bot_commands(self):
        """
        Configurează meniul de comenzi al botului
        """
        commands = [
            BotCommand("start", "Începe conversația"),
            BotCommand("help", "Ghid de utilizare"),
            BotCommand("catalog", "Vezi catalogul nostru"),
            BotCommand("contact", "Informații de contact"),
            BotCommand("stats", "Statisticile tale"),
        ]
        
        await self.application.bot.set_my_commands(commands)
        logger.info("✅ Comenzile botului au fost configurate")
    
    async def startup(self):
        """
        Funcții de rulat la pornirea botului
        """
        await self.set_bot_commands()
        logger.info("🚀 XOFlowers Telegram Bot este gata!")
    
    def run(self):
        """
        Pornește botul
        """
        logger.info("🚀 Pornesc XOFlowers Telegram Bot...")
        
        # Adaugă funcția de startup
        self.application.job_queue.run_once(
            lambda context: asyncio.create_task(self.startup()), 
            when=1
        )
        
        # Pornește botul
        self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )

def main():
    """
    Funcția principală - Sarcina lui Lucian
    """
    print("🤖 XOFlowers Telegram Bot - Sarcina lui Lucian")
    print("=" * 60)
    
    try:
        # Verifică token-ul
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ TELEGRAM_BOT_TOKEN nu este setat în fișierul .env!")
            print("   1. Creează un bot nou cu @BotFather pe Telegram")
            print("   2. Copiază token-ul în fișierul .env")
            print("   3. Rulează din nou acest script")
            return
        
        # Creează și pornește botul
        bot = XOFlowersTelegramBot()
        
        print("\\n🎉 Bot configurat cu succes!")
        print(f"   Token: {token[:10]}...")
        print("   Conectându-mă la Telegram...")
        
        # Pornește botul (blocking call)
        bot.run()
        
    except KeyboardInterrupt:
        print("\\n⏹️  Bot oprit de utilizator")
    except Exception as e:
        logger.error(f"❌ Eroare critică: {e}")
        print(f"\\n❌ Eroare: {e}")
        print("\\nVerifică:")
        print("   1. Token-ul Telegram în .env")
        print("   2. Conectivitatea la internet")
        print("   3. Că core_logic.py funcționează")

if __name__ == "__main__":
    main()
