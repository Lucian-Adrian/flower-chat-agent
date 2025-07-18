# XOFlowers AI Agent - Launch Guide (2025)

## 🚀 **CURRENT IMPLEMENTATION - HOW TO RUN**

This guide covers the **current working implementation** of the XOFlowers AI Agent (January 2025). All commands are tested and verified.

## 📋 **Prerequisites**

1. **Python 3.9+** installed
2. **Docker & Docker Compose** (for production)
3. **API Keys** (at least one):
   - OpenAI API Key (primary)
   - Google Gemini API Key (fallback)
   - Telegram Bot Token
   - Instagram API credentials (optional)

## ⚡ **Quick Start (Recommended)**

### **Method 1: FastAPI Application (Main)**

This is the **current main application** that includes all bots and services:

```bash
# 1. Clone and navigate to project
cd xoflowers-agent

# 2. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the main FastAPI application
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 5. Check system health
curl http://localhost:8000/health
```

**What this runs:**
- ✅ FastAPI main application on port 8000
- ✅ Integrated Telegram bot webhooks
- ✅ Integrated Instagram bot webhooks
- ✅ ChromaDB product search (692 products)
- ✅ Redis fallback (in-memory if Redis unavailable)
- ✅ AI engine with OpenAI + Gemini fallback
- ✅ Health monitoring endpoints

## 🧪 **Testing the Current System**

### **1. Complete Integration Test**
Tests all components together:
```bash
python test_complete_integration.py
```

**Expected output:**
- ✅ ChromaDB: 692 products loaded
- ✅ Price filtering: MDL currency
- ✅ Redis fallback: Working
- ✅ AI engine: Available

### **2. System Status Test**
Quick health check:
```bash
python test_system_working.py
```

### **3. ChromaDB & Price Filtering Test**
Tests product search and price ranges:
```bash
python test_price_filtering.py
```

**Expected output:**
- ✅ Products under 100 MDL
- ✅ Products 500-1000 MDL range
- ✅ Products over 1000 MDL
- ✅ Romanian language search working

## 🐳 **Production Deployment**

### **Docker Compose (Recommended for Production)**

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with production values

# 2. Deploy complete stack
docker-compose up -d

# 3. Check all services
docker-compose ps
docker-compose logs -f xoflowers-ai

# 4. Health check
curl http://localhost:8000/health
```

**Services included:**
- `xoflowers-ai`: Main application
- `redis`: Conversation context storage
- `prometheus`: Metrics collection
- `grafana`: Monitoring dashboard

### **Quick Deployment Script**
```bash
# Linux/Mac
./deploy.sh -e production --backup

# Windows
.\deploy.ps1 -Environment production -Backup
```

## 🔧 **Alternative Running Methods**

### **Standalone Telegram Bot**
```bash
python src/api/telegram_app.py
```

### **Standalone Instagram Bot**
```bash
python src/api/instagram_app.py
```

### **Development Mode with Auto-reload**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 **System Endpoints**

When running the main application, these endpoints are available:

- **Main API**: `http://localhost:8000`
- **Health Check**: `http://localhost:8000/health`
- **API Documentation**: `http://localhost:8000/docs`
- **ChromaDB Stats**: `http://localhost:8000/chromadb/stats`
- **Redis Stats**: `http://localhost:8000/redis/stats`
- **Telegram Webhook**: `http://localhost:8000/telegram/webhook`
- **Instagram Webhook**: `http://localhost:8000/instagram/webhook`

## ⚠️ **Common Issues & Solutions**

### **1. ChromaDB Slow on First Run**
```bash
# First run downloads embedding model (~20 seconds)
# Subsequent runs are faster (~12 seconds)
# This is normal - wait for completion
```

### **2. Missing API Keys**
```bash
# Check .env file has required keys:
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
TELEGRAM_BOT_TOKEN=123...
```

### **3. Import Errors**
```bash
# Make sure you're in the correct directory
cd xoflowers-agent

# Install dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### **4. Price Filtering Not Working**
```bash
# Test ChromaDB directly
python test_price_filtering.py

# Check logs for errors
tail -f logs/app.log
```

### **5. Redis Connection Issues**
```bash
# System automatically falls back to in-memory storage
# Check logs for "Redis fallback mode" messages

# For Docker:
docker-compose logs redis
```

## 📊 **Monitoring & Logs**

### **Application Logs**
```bash
# Real-time logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f xoflowers-ai
```

### **Performance Monitoring**
- **Grafana**: `http://localhost:3000` (admin/admin)
- **Prometheus**: `http://localhost:9090`

### **Health Checks**
```bash
# Full system health
curl http://localhost:8000/health | jq

# Individual components
curl http://localhost:8000/chromadb/stats | jq
curl http://localhost:8000/redis/stats | jq
```

## 🗂️ **Current vs Legacy Files**

### **✅ USE THESE (Current 2025)**
- `src/api/main.py` - Main FastAPI application
- `test_complete_integration.py` - Main integration test
- `test_system_working.py` - System status test
- `test_price_filtering.py` - ChromaDB test
- `docker-compose.yml` - Production deployment

### **❌ DON'T USE (Legacy)**
- `test_enhanced_system.py` - Old system test
- `test_final_system.py` - Old final test
- `test_gemini_api.py` - API-only test
- `test_new_gemini.py` - Old Gemini test
- `chatbot-vladimir-products-agent/` - Old implementation
- `chatbot-andrei-chromadb/` - Old ChromaDB version

## 🚦 **System Status Indicators**

### **✅ Working System Indicators**
- ChromaDB: 692 products loaded
- Redis: Available or fallback mode
- AI Engine: OpenAI + Gemini available
- Price filtering: MDL currency working
- Health endpoint: Returns 200 OK

### **❌ Problem Indicators**
- ChromaDB: 0 products or errors
- Missing environment variables
- Import errors on startup
- Health endpoint: Returns errors

## 🎯 **Next Steps After Launch**

1. **Monitor logs** for any errors
2. **Test with real messages** via Telegram
3. **Check price filtering** works correctly
4. **Verify Romanian language** responses
5. **Monitor performance** via Grafana dashboard

---

**📞 Need Help?**
Check the logs, run the test files, and ensure all environment variables are set correctly. The system is designed with graceful fallbacks for maximum reliability.
