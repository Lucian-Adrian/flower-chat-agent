# XOFlowers Bot Scripts

This folder contains various scripts to launch and manage the XOFlowers Telegram Bot.

## 🚀 Bot Launchers

### Quick Start (Recommended)
```bash
# PowerShell (Windows)
.\scripts\start_telegram_bot.ps1

# Command Prompt (Windows)
scripts\run_telegram_bot.bat

# Cross-platform Python
python scripts\simple_bot_launcher.py
```

### Advanced Options
```bash
# Direct module execution
python -m src.api.telegram_app

# With custom launcher
python scripts\telegram_bot_launcher.py
```

## 📋 Requirements

Make sure you have:
- ✅ Python 3.8+ installed
- ✅ All dependencies: `pip install -r requirements.txt`
- ✅ `.env` file with your API keys:
  - `TELEGRAM_BOT_TOKEN`
  - `OPENAI_API_KEY`

## 🎯 Testing Your Bot

1. **Start the bot** using one of the methods above
2. **Find your bot** on Telegram using the bot username
3. **Send messages** to test:
   - `/start` - Welcome message
   - `/help` - Bot commands
   - "Salut!" - Natural conversation
   - "Vreau flori pentru ziua mamei" - Product search
   - "Care sunt prețurile?" - Price inquiry

## 🔧 Troubleshooting

If you get event loop errors:
- ✅ Bot is likely working despite the error
- ✅ Check Telegram - bot should respond to messages
- ✅ The error only affects the launcher, not bot functionality

## 📁 Available Scripts

- `simple_bot_launcher.py` - Clean, minimal launcher
- `telegram_bot_launcher.py` - Advanced launcher with error handling
- `start_telegram_bot.ps1` - PowerShell launcher
- `run_telegram_bot.bat` - Windows batch file
- `run_tests.py` - Test runner for the bot system