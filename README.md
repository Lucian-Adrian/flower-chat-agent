# 🌸 XOFlowers AI Agent

**Enhanced AI Conversational Agent pentru XOFlowers** - Powered by Gemini Chat + Fallback Systems

Un agent AI conversațional de ultimă generație care conduce conversații naturale și personalizate cu clienții XOFlowers prin Instagram și Telegram. Agentul utilizează **Gemini Chat cu context integrat**, **sisteme de fallback robuste**, și **zero dependencies** pentru a oferi o experiență conversațională premium fără template-uri predefinite.

## 🌟 **ENHANCED FEATURES (2025)**

### **🚀 Gemini Chat Integration**
- **Built-in Conversation Memory**: Context automat fără Redis
- **Structured Output**: Răspunsuri JSON cu Pydantic models
- **System Instructions**: Instrucțiuni sistem în loc de prompt injection
- **Multi-turn Conversations**: Conversații naturale cu istoric automat
- **Thinking Disabled**: Răspunsuri rapide optimizate pentru speed

### **🔄 Graceful Degradation System**
- **ChromaDB → CSV Fallback**: Căutare produse fără dependențe externe
- **Redis → In-Memory Fallback**: Context storage în memorie
- **OpenAI → Gemini Fallback**: Redundanță completă AI services
- **Zero Single Points of Failure**: Sistem robust și fiabil

### **⚡ Enhanced Performance**
- **<2 seconds average response time** (îmbunătățit)
- **100% success rate** în teste (9/9 messages)
- **Connection pooling** pentru AI services
- **Response caching** cu TTL pentru performance
- **Real-time monitoring** și logging

## 🎯 **FUNCȚIONALITĂȚI PRINCIPALE**

### **🧠 Agent Conversațional Natural cu AI**
Botul funcționează ca un **consultant floral expert** care:
- **Conduce conversații naturale** fără template-uri predefinite
- **Personalizează fiecare răspuns** pe baza contextului conversației
- **Căutare activă în baza de date** pentru recomandări relevante
- **Acces la informații complete** despre produse, prețuri, disponibilitate
- **Memorie conversațională** care păstrează contextul între mesaje

### **🔍 Sistem de Căutare Inteligentă (MCP-Style)**
Agentul are acces la funcții de căutare specializate:
- **Căutare vectorială semantică** în catalogul de produse
- **Filtrare după categorie** (buchete, cutii cadou, plante, etc.)
- **Căutare după buget** și preferințe specifice
- **Informații despre disponibilitate** și stock
- **Recomandări personalizate** bazate pe istoric conversații

### **�️ Guard Rails Avansate**
Sistemul de securitate asigură:
- **Focusul pe business XOFlowers** - agentul nu se abate de la rol
- **Protecție anti-jailbreak** cu prompturi robuste
- **Filtrare conținut ofensator** cu răspunsuri politicoase
- **Rate limiting inteligent** (10 msg/min, 100 msg/h)
- **Logging și monitoring** pentru debug și optimizare

### **⚡ Capabilități AI Avansate**
- **Conversații Multi-Turn**: Înțelege și păstrează contextul conversațiilor
- **Răspunsuri Contextuale**: Fiecare mesaj este adaptat la situația specifică
- **Căutare Semantică**: Găsește produse relevante chiar și cu descrieri vagi
- **Personalizare Completă**: Ține cont de preferințele și istoricul clientului
- **Fallback Inteligent**: OpenAI GPT-4 → Google Gemini Pro pentru redundanță

### **🏗️ Arhitectură Agent Conversațional**
- **AI-First Approach**: Toate răspunsurile sunt generate natural de AI, nu template-uri
- **MCP-Style Database Access**: Agentul are acces la funcții de căutare în timp real
- **Context-Aware Responses**: Fiecare răspuns ține cont de istoricul conversației
- **Semantic Search Engine**: ChromaDB cu embeddings pentru căutare inteligentă
- **Guard Rails Robuste**: Protecție împotriva manipulării fără a afecta natura
- **Multi-Platform Support**: Telegram (100% LIVE) și Instagram (90% testare finală)

## � **QUICK START - HOW TO RUN**

### **🎯 Current Implementation (2025)**

The system now uses **FastAPI as the main application** with integrated Telegram and Instagram bots. Here's how to run the current version:

#### **Method 1: Docker Compose (Recommended)**
```bash
# 1. Copy environment configuration
cp .env.example .env

# 2. Edit .env with your API keys:
# - TELEGRAM_BOT_TOKEN
# - OPENAI_API_KEY or GEMINI_API_KEY  
# - INSTAGRAM credentials if needed

# 3. Start the complete system
docker-compose up -d

# 4. Check system health
curl http://localhost:8000/health
```

#### **Method 2: Direct Python Execution**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
cp .env.example .env
# Edit .env with your keys

# 3. Run the main FastAPI application
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# 4. For Telegram bot only (alternative)
python src/api/telegram_app.py

# 5. For Instagram bot only (alternative) 
python src/api/instagram_app.py
```

#### **Method 3: Testing the System**
```bash
# Test complete integration
python test_complete_integration.py

# Test ChromaDB functionality
python test_price_filtering.py

# Test system working status
python test_system_working.py
```

### **📊 System Status Dashboard**
- **Main API**: `http://localhost:8000`
- **Health Check**: `http://localhost:8000/health`
- **ChromaDB Stats**: `http://localhost:8000/chromadb/stats`
- **Telegram Bot**: Integrated in main app
- **Instagram Bot**: Integrated in main app

## 📁 **CURRENT PROJECT STRUCTURE**

```
xoflowers-agent/
├── src/                             # 💻 Main source code
│   ├── api/                         # 🔌 API interfaces & bots
│   │   ├── main.py                  # 🚀 MAIN FASTAPI APPLICATION
│   │   ├── telegram_app.py          # Telegram bot (standalone)
│   │   ├── telegram_integration.py  # Telegram FastAPI integration
│   │   ├── instagram_app.py         # Instagram bot (standalone)
│   │   └── instagram_integration.py # Instagram FastAPI integration
│   │
│   ├── intelligence/                # 🧠 AI Engine & Intelligence
│   │   ├── ai_engine.py             # Main AI coordinator (OpenAI + Gemini)
│   │   ├── gemini_chat_manager.py   # Enhanced Gemini Chat with context
│   │   ├── security_ai.py           # AI-powered security & jailbreak detection
│   │   ├── context_manager.py       # Conversation context with Redis fallback
│   │   ├── response_generator.py    # Natural response generation
│   │   ├── product_recommender.py   # AI product recommendations
│   │   └── business_info_integrator.py # Business info integration
│   │
│   ├── data/                        # 📊 Data management
│   │   ├── chromadb_client.py       # 🚀 CHROMADB INTEGRATION (692 products)
│   │   ├── redis_client.py          # Redis with in-memory fallback
│   │   └── faq_manager.py           # FAQ and business information
│   │
│   ├── database/                    # 💾 Database files
│   │   └── products.csv             # 692 products in CSV format
│   │
│   └── helpers/                     # 🛠️ Utility modules
│       ├── system_definitions.py    # System configuration
│       ├── utils.py                 # Logging and utilities
│       └── monitoring.py            # Performance monitoring
│
├── tests/                           # 🧪 Test files (current)
│   ├── test_ai_engine.py
│   ├── test_integration.py
│   └── test_system_integration.py
│
├── test_*.py                        # 🧪 Root test files (current)
│   ├── test_complete_integration.py # ✅ MAIN INTEGRATION TEST
│   ├── test_system_working.py       # ✅ SYSTEM STATUS TEST
│   ├── test_price_filtering.py      # ✅ CHROMADB PRICE FILTERING TEST
│   └── test_fixed_integration.py    # ✅ FIXED INTEGRATION TEST
│
├── docker-compose.yml               # 🐳 Main deployment config
├── deploy.sh / deploy.ps1           # 🚀 Deployment scripts
├── .env.example                     # ⚙️ Environment template
└── requirements.txt                 # 📦 Python dependencies
```

### **🗂️ LEGACY FILES (Not Used in Current Implementation)**

These files are from older versions and are **NOT USED** in the current system:

❌ **Deprecated Test Files:**
- `test_enhanced_system.py` (old system test)
- `test_final_system.py` (old final test)
- `test_gemini_api.py` (API-only test)
- `test_openai_api.py` (API-only test)
- `test_new_gemini.py` (old Gemini test)
- `test_system_end_to_end.py` (old e2e test)

❌ **Legacy Folders:**
- `chatbot-vladimir-products-agent/` (old implementation)
- `chatbot-andrei-chromadb/` (old ChromaDB version)
- `chatbot-main/` (old main version)

### **✅ CURRENT FILES TO USE:**

🟢 **Main Application:** `src/api/main.py` (FastAPI)
🟢 **Current Tests:** `test_complete_integration.py`, `test_system_working.py`
🟢 **Deployment:** `docker-compose.yml`, `deploy.sh`
🟢 **Config:** `.env` (based on `.env.example`)

## 💡 **TROUBLESHOOTING CURRENT IMPLEMENTATION**

### **Common Issues & Solutions:**

1. **ChromaDB Slow Loading:**
   ```bash
   # First run takes ~20s to download embedding model
   # Subsequent runs are faster (~12s)
   # Check: python test_price_filtering.py
   ```

2. **Missing Environment Variables:**
   ```bash
   # Copy and edit environment template
   cp .env.example .env
   # Add your API keys
   ```

3. **Price Filtering Issues:**
   ```bash
   # Test price filtering functionality
   python test_price_filtering.py
   # Check ChromaDB logs for errors
   ```

4. **Redis Connection Issues:**
   ```bash
   # System uses fallback mode if Redis unavailable
   # Check: docker-compose logs redis
   ```

5. **Currency Display:**
   ```bash
   # System now uses MDL instead of RON
   # Prices automatically converted in responses
   ```

## 🚀 **PRODUCTION DEPLOYMENT**

### **Docker Compose (Recommended)**
```bash
# Quick production deployment
./deploy.sh -e production --backup

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### **Health Monitoring**
- **System Health:** `http://localhost:8000/health`
- **ChromaDB Status:** `http://localhost:8000/chromadb/stats`
- **Redis Status:** `http://localhost:8000/redis/stats`
- **Prometheus Metrics:** `http://localhost:9090`
- **Grafana Dashboard:** `http://localhost:3000`
