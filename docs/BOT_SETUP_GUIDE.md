# 🌸 XOFlowers AI Agent - Setup Guide

## 🚀 Agent Conversațional Natural

XOFlowers AI Agent este un agent conversațional natural care conduce conversații personalizate cu clienții, având acces la funcții de căutare în baza de date pentru recomandări relevante.

## 🔧 Rularea Agentului

### **Option 1: PowerShell Scripts (Recommended)**
```powershell
# Start Instagram bot in separate terminal
.\scripts\start_instagram.ps1

# Start Telegram bot in separate terminal  
.\scripts\start_telegram.ps1

# Start both bots + ngrok automatically
.\scripts\start_all.ps1
```

### **Option 2: Launcher Python**
```bash
# From project root directory
python scripts/launcher.py
# Choose:
# 1 - Telegram bot only
# 2 - Instagram bot only
# 3 - Both bots
# 4 - Run tests
```

### **Option 3: Manual Python Commands**
```bash
# From project root directory
python scripts/run_instagram.py    # Instagram bot
python scripts/run_telegram.py     # Telegram bot
python scripts/run_both.py         # Both bots
```

## 🔧 Setup Requirements

### **1. Directory Structure**
```
xoflowers-agent/
├── .venv/                    # Virtual environment
├── scripts/                  # 🚀 Launchers și runners
│   ├── launcher.py           # Main launcher
│   ├── run_instagram.py      # Instagram agent
│   ├── run_telegram.py       # Telegram agent
│   ├── run_both.py          # Dual agent
│   ├── start_*.ps1          # PowerShell launchers
│   └── launcher.bat         # Batch launcher
├── src/                      # 💻 Natural AI Agent Code
│   ├── api/                  # Platform integrations
│   ├── intelligence/         # AI brain (no templates)
│   ├── security/             # Guard rails
│   └── database/             # Vector database
└── data/                     # Product catalog & contexts
```

### **2. Environment Setup**
- Python 3.13.1 with virtual environment activated
- All dependencies installed via `requirements.txt`
- `.env` file with API keys configured

### **3. For Instagram Webhook**
```bash
# Start ngrok tunnel
ngrok http 5001

# Configure in Meta Developer Console:
# Webhook URL: https://your-ngrok-url.ngrok-free.app/webhook
# Verify Token: xoflowers_webhook_secret_2024
```

## 🎯 Natural AI Agent Features

### **📱 Telegram Agent**
- **Mode**: Polling (no webhook needed)
- **AI**: Natural conversation with OpenAI GPT-4 → Gemini fallback
- **Language**: Romanian (perfect native speaker)
- **Features**: Natural product search, contextual recommendations, business info

### **📸 Instagram Agent**
- **Mode**: Webhook (Flask server on port 5001)
- **AI**: Same natural conversation capabilities
- **Features**: Same as Telegram agent
- **Requirements**: ngrok tunnel for webhook

### **🤖 Natural AI System**
- **No Templates**: Every response is generated naturally by AI
- **Database Access**: MCP-style access to product database
- **Context Awareness**: Multi-turn conversation memory
- **Personalization**: Learns user preferences and adapts
- **Guard Rails**: Strong business focus without restricting naturalness

## 🔍 Testing

### **Test Instagram Bot**
```bash
# Health check
curl http://localhost:5001/health

# Webhook verification
curl "http://localhost:5001/webhook?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=xoflowers_webhook_secret_2024"
```

### **Test Telegram Bot**
- Send message to bot on Telegram
- Check terminal for processing logs
- Verify AI responses

## 📊 System Status

- ✅ **OpenAI Integration**: Tested and working
- ✅ **Gemini Fallback**: Configured and ready
- ✅ **Product Database**: 709 products loaded
- ✅ **Romanian Language**: Native support
- ✅ **Webhook System**: Verified and tested
- ✅ **Professional Responses**: No persona, business-focused

## 🚨 Troubleshooting

### **Common Issues:**
1. **Virtual Environment**: Make sure you're in `xoflowers_chatbot/` directory
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **API Keys**: Check `.env` file has all required keys
4. **ngrok**: Make sure ngrok is running for Instagram webhook
5. **Ports**: Ensure port 5001 is available for Instagram bot

### **Log Files:**
- Check terminal output for bot status
- Instagram bot logs show webhook activity
- Telegram bot logs show polling activity

---
**Last Updated**: July 15, 2025  
**Status**: Production Ready 🌸
