# XOFlowers AI Agent 🌸

**Plan: Agent AI Conversațional pentru XOFlowers**

Un agent AI conversațional, funcțional și de înaltă calitate, care să îndeplinească toate cerințele din fișa de sarcini, cu o arhitectură pregătită pentru optimizări în viitor.

## 🏗️ Arhitectura Sistemului

Sistem modular, unde fiecare componentă are o singură responsabilitate. Esențial pentru a permite dezvoltarea paralelă, debug eficient și mentenanța pe termen lung.

### Diagrama Arhitecturii:

```
+----------------------+        +-------------------------+        +----------------------+
|     Platforma        |        |   Serverul API          |        |  Logica Centrală     |
| (Telegram/Insta)     | <--->  | (telegram_app.py)       | <--->  | (core_logic.py)      |
|       Utilizator     |        | (Flask pentru Insta)    |        |                      |
+----------------------+        +-------------------------+        +----------+-----------+
                                                                              |
                                                                              |
                                                           +------------------+------------------+
                                                           |                                     |
                                                    +------+--------+                  +-------+--------+
                                                    |   Modelul AI  |                  |   Baza de Date |
                                                    | (Gemini/Ollama)|                  |   (ChromaDB)   |
                                                    +----------------+                  +----------------+
```

## 📁 Structura Repository-ului

```
xoflowers-agent/
├── config/
│   ├── settings.py              # ✅ Configurări sistem
│   └── faq_data.json            # ✅ Întrebări frecvente
│
├── data/
│   └── products.json            # ✅ Date produse (50/50)
│
├── src/
│   ├── api/
│   │   ├── __init__.py          # ✅ Modul API
│   │   ├── telegram_app.py      # ✅ Aplicația Telegram (100%)
│   │   └── instagram_app.py     # ✅ Aplicația Instagram (80%)
│   │
│   ├── intelligence/
│   │   ├── __init__.py          # ✅ Modul inteligență
│   │   ├── prompts.py           # ✅ Prompt-uri AI
│   │   ├── intent_classifier.py # 🔧 Clasificator intent
│   │   ├── product_search.py    # 🔧 Căutare produse
│   │   └── action_handler.py    # 🔧 Handler acțiuni
│   │
│   ├── pipeline/
│   │   ├── __init__.py          # ✅ Modul pipeline
│   │   ├── scraper.py           # ✅ Scraper web
│   │   └── populate_db.py       # ✅ Populare bază date (90%)
│   │
│   └── security/
│       ├── __init__.py          # ✅ Modul securitate
│       └── filters.py           # ✅ Filtre securitate
│
├── .env                         # ✅ Variabile mediu
├── .gitignore                   # ✅ Fișiere ignorate
├── README.md                    # ✅ Documentație
└── requirements.txt             # 🔧 Dependențe (80% clean)
```

## 🎯 Componente Implementate

### ✅ **Complet Implementate**
- **config/settings.py** - Toate configurările sistemului
- **config/faq_data.json** - Întrebări frecvente în română
- **src/api/telegram_app.py** - Aplicația Telegram funcțională
- **src/api/instagram_app.py** - Aplicația Instagram (verificare necesară)
- **src/intelligence/prompts.py** - Toate prompt-urile AI
- **src/pipeline/scraper.py** - Scraper pentru xoflowers.md
- **src/security/filters.py** - Protecție și censură

### 🔧 **În Dezvoltare**
- **src/intelligence/intent_classifier.py** - Clasificare intent AI
- **src/intelligence/product_search.py** - Căutare vector ChromaDB
- **src/intelligence/action_handler.py** - Handler pentru acțiuni
- **src/pipeline/populate_db.py** - Adaptare la noul dataset

## 🚀 Funcționalități Planificate

### 1. **Intent Classification**
- Detectează: find_product, ask_question, subscribe, pay_for_product
- Protecție anti-jailbreak
- Confidence scoring

### 2. **Product Search**
- Căutare vector în ChromaDB
- Filtrare pe categorii
- Rezultate relevante cu similaritate

### 3. **Action Handling**
- Răspunsuri contextualizate
- Integrare cu FAQ
- Simulare plată

### 4. **Security**
- Filtrare conținut ofensator
- Rate limiting
- Protecție jailbreak

## 📋 Următorii Pași

1. **Finalizare Intelligence Module** 🔧
2. **Integrare ChromaDB** 🔧
3. **Testare End-to-End** 🔧
4. **Optimizare Performanță** 🔧
5. **Deployment Production** 🚀

## 🎯 Obiective

- ✅ Arhitectură modulară și scalabilă
- ✅ Structură clară și organizată
- 🔧 Integrare AI avansată
- 🔧 Performanță optimizată
- 🚀 Gata pentru producție

---

**Status**: Structura creată ✅ | Următorul pas: Implementare module intelligence 🔧
