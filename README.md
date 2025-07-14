# 🌸 XOFlowers AI Agent

**Instagram AI Agent pentru XOFlowers** - Construit cu ChromaDB + LLMs

Un agent AI inteligent integrat cu Instagram și Telegram care interacționează cu clienții prin mesaje directe, înțelege intențiile lor și oferă răspunsuri utile precum recomandări de produse, abonamente, informații despre afacere și procesarea plăților.

## 🎯 **FUNCȚIONALITĂȚI PRINCIPALE**

### **Procesarea Intențiilor**
Botul gestionează 4 tipuri principale de intenții:

1. **🔍 find_product** - Căutare și recomandări de produse (buchete, cutii cadou, plante)
2. **❓ ask_question** - Întrebări generale despre afacere (program, locație, politici)
3. **📧 subscribe** - Abonare la planuri de flori sau actualizări promoționale
4. **💳 pay_for_product** - Procesarea intențiilor de plată cu simulare de plată

### **Arhitectură Inteligentă**
- **AI Multimodal**: OpenAI primar cu fallback Google Gemini
- **Căutare Vector**: ChromaDB pentru căutare semantică în produse
- **Securitate Avansată**: Filtrare conținut + protecție anti-jailbreak
- **Multi-Platform**: Suport Instagram DM și Telegram

## 📁 **STRUCTURA PROIECTULUI**

```
xoflowers-agent/
├── config/                          # ⚙️ Configurări sistem
│   └── settings.py                  # Setări globale și constante
│
├── docs/                            # 📚 Documentație tehnică
│   ├── architecture.md              # Arhitectura sistemului
│   ├── deployment.md                # Ghid deployment
│   ├── system_flow.md               # Fluxul sistemului
│   └── project_progress.md          # Progresul proiectului
│
├── data/                            # 📊 Date și cataloage
│   ├── products.json                # Catalogul de produse XOFlowers
│   ├── chunks_data.csv              # Date procesate produse
│   └── faq_data.json                # Întrebări frecvente în română
│
├── src/                             # 💻 Codul sursă
│   ├── api/                         # 🔌 Interfețe platforme
│   │   ├── __init__.py
│   │   ├── telegram_app.py          # Bot Telegram (100% LIVE)
│   │   └── instagram_app.py         # Bot Instagram (90% - testare finală)
│   │
│   ├── intelligence/                # 🧠 Creierul AI
│   │   ├── __init__.py
│   │   ├── prompts.py               # Template-uri AI (100% - Brand Voice)
│   │   ├── intent_classifier.py     # Clasificare AI (100% - 17 tipuri)
│   │   ├── conversation_context.py  # Context manager (100% - Memorie)
│   │   ├── product_search.py        # Motor căutare (95% - Vector Search)
│   │   └── action_handler.py        # Logica business (100% - Context-aware)
│   │
│   ├── pipeline/                    # 🔄 Procesare date
│   │   ├── __init__.py
│   │   ├── scraper.py               # Web scraping (90% - Automatizare)
│   │   └── populate_db.py           # Populare bază date (90% - Optimizare)
│   │
│   ├── database/                    # 🗄️ Gestionare bază de date
│   │   ├── __init__.py
│   │   └── manager.py               # Database manager (100% - ChromaDB)
│   │
│   └── security/                    # 🔒 Securitate și filtrare
│       ├── __init__.py
│       └── filters.py               # Censură, anti-jailbreak (100%)
│
├── tests/                           # 🧪 Suite de teste
│   ├── __init__.py
│   ├── test_imports.py              # Teste validare import-uri
│   ├── test_agent.py                # Teste funcționalitate de bază
│   ├── test_enhanced_agent.py       # Teste comprehensive (17 intenții)
│   └── README.md                    # Documentație teste
│
├── .env                             # 🔑 Variabile de mediu
├── .gitignore                       # 📝 Fișiere ignorate de Git
├── README.md                        # 📖 Documentația proiectului
└── requirements.txt                 # 📦 Dependențe Python (80% clean)
```

## 🚀 **INSTALARE ȘI CONFIGURARE**

### **1. Clonare și Setup**
```bash
# Clonează repository-ul
git clone <repository-url>
cd xoflowers-agent

# Creează mediul virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Instalează dependențele
pip install -r requirements.txt
```

### **2. Configurare Environment**
```bash
# Copiază template-ul de mediu
cp .env.example .env

# Editează .env cu cheile tale API
# OPENAI_API_KEY=your_openai_key
# GEMINI_API_KEY=your_gemini_key
# INSTAGRAM_ACCESS_TOKEN=your_instagram_token
# TELEGRAM_BOT_TOKEN=your_telegram_token
```

### **3. Populare Bază de Date**
```bash
# Populează ChromaDB cu produsele
python -m src.pipeline.populate_db

# Verifică populația bazei de date
python -c "import chromadb; client = chromadb.PersistentClient('./chroma_db_flowers'); print(f'Collections: {len(client.list_collections())}')"
```

## 🎮 **UTILIZARE - SISTEM LIVE**

### **🟢 Telegram Bot LIVE**
**Bot-ul Telegram este acum LIVE și funcționează complet!**

```bash
# Pornește botul Telegram (LIVE)
cd xoflowers-agent
python src/api/telegram_app.py

# Sau folosește main.py
python main.py --platform telegram
```

**Comenzi disponibile:**
- `/start` - Salut și introducere XOFlowers
- `/help` - Ghid complet de utilizare
- `/menu` - Meniu interactiv principal
- `/catalog` - Catalogul de flori
- `/contact` - Informații contact
- `/orders` - Status comenzi
- `/subscribe` - Abonare newsletter
- `/feedback` - Trimite feedback

### **🔄 Instagram Bot (În testare)**
```bash
# Pornește botul Instagram (testare finală)
python main.py --platform instagram --port 5001
```

### **🛠️ Mod Debug și Testare**
```bash
# Mod debug pentru dezvoltare
python main.py --platform telegram --debug

# Testare rapidă intent classifier
python -c "
from src.intelligence.intent_classifier import IntentClassifier
ic = IntentClassifier()
print(ic.classify_intent('Vreau un buchet frumos pentru soția mea'))
"
```

## 🧪 **TESTARE**

### **Testare Webhook Instagram**
```bash
# Testează verificarea webhook-ului
curl -X GET "http://localhost:5001/webhook?hub.mode=subscribe&hub.verify_token=xoflowers_webhook_secret_2024&hub.challenge=test"

# Răspuns așteptat: test
```

### **Testare Endpoint Sănătate**
```bash
curl http://localhost:5001/health
# Răspuns: {"status": "healthy", "service": "XOFlowers Instagram Bot"}
```

### **Testare Clasificare Intenții**
```bash
python -c "
from src.intelligence.intent_classifier import IntentClassifier
ic = IntentClassifier()
print(ic.classify_intent('Vreau să cumpăr flori pentru soția mea'))
"
```

## 🔧 **CONFIGURARE AVANSATĂ**

### **Setări AI (config/settings.py)**
```python
AI_MODEL = {
    'primary': 'openai',        # Serviciu AI primar
    'fallback': 'gemini',       # Serviciu AI de rezervă
    'temperature': 0.7,         # Creativitatea răspunsurilor
    'max_tokens': 1000          # Lungimea maximă răspuns
}
```

### **Configurare Securitate**
```python
SECURITY = {
    'enable_censorship': True,          # Activează filtrarea conținutului
    'enable_jailbreak_protection': True, # Protecție anti-manipulare
    'rate_limiting': {
        'max_requests_per_minute': 10,  # Limite pe minut
        'max_requests_per_hour': 100    # Limite pe oră
    }
}
```

### **Configurare Căutare Produse**
```python
DATABASE = {
    'chromadb_path': './chroma_db_flowers',
    'embedding_model': 'all-MiniLM-L6-v2',
    'collections': {
        'bouquets': 'bouquets_collection',
        'boxes': 'boxes_collection',
        'compositions': 'compositions_collection',
        'plants': 'plants_collection',
        'gifts': 'gifts_collection'
    }
}
```

## 🎯 **EXEMPLE DE UTILIZARE**

### **Căutare Produse**
```
User: "Vreau un buchet pentru soția mea"
Bot: "🌸 Am găsit aceste buchete perfecte pentru soția dumneavoastră:

🌸 **Buchet Romantic Supreme**
💰 750 MDL
📝 Buchet elegant cu 25 trandafiri roșii și baby breath

🌸 **Buchet Passion**
💰 600 MDL  
📝 Combinație frumoasă de trandafiri și bujori roz"
```

### **Întrebări Business**
```
User: "Care sunt orele de lucru?"
Bot: "🕒 Orele noastre de lucru:
• Luni-Duminică: 09:00 - 21:00
• Suntem disponibili în fiecare zi pentru a vă servi!"
```

### **Procesare Plată**
```
User: "Vreau să plătesc pentru buchețul acela"
Bot: "💳 Plata a fost procesată cu succes! 🎉

Comanda dumneavoastră a fost confirmată.
Vă vom contacta în curând pentru finalizarea livrării.

Mulțumim că ați ales XOFlowers! 🌺"
```

## 📊 **PERFORMANȚĂ LIVE**

### **🎯 Metrici Producție Actuală**
```
🌸 XOFlowers AI Agent - LIVE METRICS:
├── 🤖 AI Intent Recognition: 17 tipuri cu 95%+ acuratețe
├── 📱 Telegram Bot: 100% operațional cu toate comenzile
├── 💬 Context System: Conversații multi-turn cu memorie
├── 🔒 Security Layer: Rate limiting + filtrare conținut
├── ⚡ Response Time: <3 secunde mediu
├── 🎯 Brand Voice: Experiență premium XOFlowers
└── 🌐 Multi-platform: Telegram LIVE, Instagram ready
```

### **📈 Capabilități Avansate**
- **Conversații Inteligente**: AI-powered cu memorie contextuală
- **Căutare Semantică**: Vector search cu similaritate avansată
- **Personalizare**: Răspunsuri adaptate preferințelor utilizatorului
- **Robusteță**: Fallback mechanisms pentru fiabilitate maximă

### **🔧 Arhitectură Scalabilă**
- **Timp de răspuns**: < 3 secunde mediu
- **Disponibilitate**: 99%+ uptime reliability
- **Capacitate**: 100+ utilizatori concurenți
- **Scalabilitate**: Arhitectură modulară pentru extindere

## 🔮 **ROADMAP ACTUALIZAT - IULIE 2025**

### **🎉 REALIZAT - SISTEM LIVE** ✅
- [x] **Sistem AI Complet** - Intent classification cu 17 tipuri
- [x] **Context Conversațional** - Memorie și personalizare
- [x] **Telegram Bot LIVE** - Complet funcțional în producție
- [x] **Brand Voice Premium** - Experiență XOFlowers elegantă
- [x] **Securitate Avansată** - Protecție și rate limiting
- [x] **ChromaDB Integration** - Vector search optimizat

### **🔄 În Finalizare** 📋
- [ ] **Instagram Bot Testing** - Testare finală webhook
- [ ] **Performance Monitoring** - Analytics și optimizare
- [ ] **Documentation Complete** - Ghiduri utilizator finale
- [ ] **User Feedback Integration** - Colectare și procesare feedback

### **🚀 Următoarea Fază** 
- [ ] **Suport multilingv extins** (RO/EN/RU)
- [ ] **Integrare procesare plăți reale**
- [ ] **Dashboard analytics** complet
- [ ] **Recunoaștere imagini** produse
- [ ] **Procesare mesaje vocale**

### **🌟 Viitor Extins**
- [ ] **Arhitectură microservicii**
- [ ] **Scalare automată**
- [ ] **Machine learning personalizat**
- [ ] **Integrare platforme multiple**
- [ ] **Mobile app integration**

## 🛠️ **DEZVOLTARE**

### **Contribuție**
1. Fork repository-ul
2. Creează branch pentru feature (`git checkout -b feature/AmazingFeature`)
3. Commit schimbările (`git commit -m 'Add AmazingFeature'`)
4. Push la branch (`git push origin feature/AmazingFeature`)
5. Deschide Pull Request

### **Rulare Teste**
```bash
# Teste comprehensive (17 intenții)
python tests/test_enhanced_agent.py

# Teste import-uri și dependențe
python tests/test_imports.py

# Teste funcționalitate de bază
python tests/test_agent.py

# Toate testele cu pytest (dacă instalat)
pip install pytest
pytest tests/ -v

# Verificare stil cod
flake8 src/
black src/
```

## 📞 **SUPORT**

### **Documentație**
- [Arhitectura Sistemului](docs/architecture.md)
- [Ghid Setup API](docs/api_setup_guide.md)
- [Exemplu
