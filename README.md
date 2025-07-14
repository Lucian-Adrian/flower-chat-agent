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
│   ├── settings.py                  # Setări globale și constante
│   └── faq_data.json                # Întrebări frecvente în română
│
├── docs/                            # 📚 Documentație tehnică
│   ├── architecture.md              # Arhitectura sistemului
│   ├── api_setup_guide.md           # Ghid configurare API-uri
│   ├── deployment.md                # Ghid deployment
│   └── system_flow.md               # Fluxul sistemului
│
├── data/                            # 📊 Date și cataloage
│   └── products.json                # Catalogul de produse XOFlowers
│
├── src/                             # 💻 Codul sursă
│   ├── api/                         # 🔌 Interfețe platforme
│   │   ├── __init__.py
│   │   ├── telegram_app.py          # Bot Telegram (100% funcțional)
│   │   └── instagram_app.py         # Bot Instagram (80% - verificare necesară)
│   │
│   ├── intelligence/                # 🧠 Creierul AI
│   │   ├── __init__.py
│   │   ├── prompts.py               # Template-uri și prompt-uri AI
│   │   ├── intent_classifier.py     # Clasificare intenții cu AI (17 tipuri)
│   │   ├── product_search.py        # Motor căutare ChromaDB
│   │   └── action_handler.py        # Logica de business și acțiuni
│   │
│   ├── pipeline/                    # 🔄 Procesare date
│   │   ├── __init__.py
│   │   ├── scraper.py               # Web scraping xoflowers.md
│   │   └── populate_db.py           # Populare bază de date (90%)
│   │
│   └── security/                    # 🔒 Securitate și filtrare
│       ├── __init__.py
│       └── filters.py               # Censură, anti-jailbreak, rate limiting
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

## 🎮 **UTILIZARE**

### **Pornire Bot Instagram**
```bash
python main.py --platform instagram --port 5001
```

### **Pornire Bot Telegram**
```bash
python main.py --platform telegram
```

### **Mod Debug**
```bash
python main.py --platform instagram --debug
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

## 📊 **PERFORMANȚĂ**

### **Specificații Tehnice**
- **Timp de răspuns**: < 3 secunde mediu
- **Acuratețe intenții**: 90%+ clasificare corectă
- **Capacitate**: 100+ utilizatori concurenți
- **Disponibilitate**: 99%+ uptime țintă

### **Metrici Monitorizate**
- Timpul de răspuns (mediu, p95, p99)
- Rata de erori pe categorii
- Acuratețea clasificării intențiilor
- Relevanța rezultatelor căutării
- Satisfacția utilizatorilor

## 🔮 **ROADMAP DEZVOLTARE**

### **În Dezvoltare** 🔧
- [ ] Implementare completă intelligence module
- [ ] Integrare și testare ChromaDB
- [ ] Optimizare algoritmi căutare
- [ ] Îmbunătățire acuratețe intenții

### **Planificat** 📋
- [ ] Suport multilingv complet (RO/EN)
- [ ] Integrare procesare plăți reale
- [ ] Dashboard analytics și monitoring
- [ ] Recunoaștere imagini produse
- [ ] Procesare mesaje vocale

### **Viitor** 🚀
- [ ] Arhitectură microservicii
- [ ] Scalare automată
- [ ] Machine learning personalizat
- [ ] Integrare platforme multiple

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
- [Exempluri de utilizare](examples/)

### **Probleme Comune**
- **Webhook nu funcționează**: Verifică URL-ul și token-ul de verificare
- **Bot nu răspunde**: Verifică cheile API și conexiunea la internet
- **Erori bază de date**: Asigură-te că ChromaDB este populat corect

### **Contact**
- 📧 Email: support@xoflowers.md
- 📞 Telefon: +373 XX XXX XXX
- 🌐 Website: https://xoflowers.md

## 📄 **LICENȚĂ**

Acest proiect este licențiat sub MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## 🙏 **MULȚUMIRI**

- OpenAI pentru API-ul GPT
- Google pentru Gemini API
- ChromaDB pentru baza de date vector
- Comunitatea open-source

---

**🌸 Construit cu dragoste pentru XOFlowers - Cele mai frumoase flori din Chișinău!**
