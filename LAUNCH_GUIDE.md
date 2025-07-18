# 🌸 XOFlowers Bot - Quick Launch Guide

## How to Launch the Bot

### Option 1: Simple Launch (Recommended)
```bash
# Navigate to the xoflowers-agent directory
cd "d:\OneDrive - Technical University of Moldova\work\smartagents\xoflowers_chatbot\xoflowers-agent"

# Run the simple launcher
python launch_bot.py
```

### Option 2: Direct Launch
```bash
# Navigate to src directory
cd "d:\OneDrive - Technical University of Moldova\work\smartagents\xoflowers_chatbot\xoflowers-agent\src"

# Run the Telegram app directly
python -m api.telegram_app
```

### Option 3: Safe Launch (Unicode-safe for Windows)
```bash
# Navigate to the xoflowers-agent directory
cd "d:\OneDrive - Technical University of Moldova\work\smartagents\xoflowers_chatbot\xoflowers-agent"

# Run the safe launcher
python launch_safe_telegram_bot.py
```

## Prerequisites

### 1. Environment Variables
Create a `.env` file with:
```env
# Required for full functionality
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Database (auto-configured)
CHROMADB_PATH=./chroma_db_flowers
```

**⚠️ IMPORTANT**: Without the API keys, the bot will only give generic responses and won't show product buttons or use the enhanced product search. Make sure your `.env` file has valid API keys!

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize ChromaDB (Automatic)
The system automatically loads 724 products from `src/database/products.csv` into ChromaDB on first run.

## System Status Check

Run a quick test to verify everything is working:
```bash
python test_enhanced_products.py
```

## What the Bot Does

✅ **AI-Powered Responses**: Uses Gemini 2.5 Flash + OpenAI fallback  
✅ **Product Search**: 724 products searchable via ChromaDB  
✅ **Smart Recommendations**: Multiple products with direct purchase links  
✅ **Security Validation**: AI-powered message filtering  
✅ **Telegram Buttons**: Product URLs as clickable buttons  
✅ **Romanian Language**: Natural Romanian conversations  

## Stopping the Bot

Press `Ctrl+C` in the terminal to stop the bot gracefully.

## Logs

Bot logs are saved to:
- `logs/bot.log` (simple launcher)
- `logs/enhanced_bot.log` (safe launcher)

## Troubleshooting

### Common Issues:

1. **Missing API Keys**: Check your `.env` file - this is the most common issue!
   - Without GEMINI_API_KEY: Bot gives generic responses, no product search
   - Without TELEGRAM_BOT_TOKEN: Bot won't start at all
   - Test your keys: Run `python test_products_bypass.py` to verify
2. **ChromaDB Issues**: Delete `chroma_db_flowers/` folder and restart
3. **Unicode Errors on Windows**: Use `launch_safe_telegram_bot.py`
4. **Import Errors**: Make sure you're in the correct directory
5. **No Product Buttons**: Usually caused by missing Gemini API key

### Test Commands:
```bash
# Test AI engine (requires API keys)
python test_enhanced_ai_engine.py

# Test product search (works without API keys)
python test_products_bypass.py

# Test full system (requires API keys)
python test_bot_launch_readiness.py

# Test specific product search functionality
python test_enhanced_products.py
```

## Core System Files

The working system uses these essential files:
- `src/api/telegram_app.py` - Main Telegram bot
- `src/intelligence/ai_engine.py` - AI processing engine
- `src/data/chromadb_client.py` - Product search database
- `src/database/products.csv` - 724 products database
- `src/utils/system_definitions.py` - Configuration
- `src/intelligence/security_ai.py` - Security validation

All other files have been identified and can be safely removed if desired.
