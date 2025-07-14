# 🔬 Teste Unitare

Această secțiune conține teste unitare specifice pentru diverse componente ale sistemului.

## 📁 **Conținut Teste Unitare**

### **🧠 Testare Componente AI**
- **`test_action_handler_budget.py`** - Testare recomandări buget
- **`test_action_handler_fix.py`** - Testare corectări action handler
- **`test_conversational_tone.py`** - Testare tonul conversațional
- **`test_director_scenario.py`** - Testare scenarii complexe

### **🔍 Testare Căutare Produse**
- **`test_product_search.py`** - Testare căutare de bază
- **`test_product_search_fix.py`** - Testare corectări căutare
- **`test_diverse_searches.py`** - Testare căutări diverse
- **`test_budget_recommendations.py`** - Testare recomandări buget

### **⚡ Testare Funcționalități**
- **`test_basic.py`** - Testare funcționalități de bază
- **`test_bot_functionality.py`** - Testare funcționalități bot
- **`test_telegram_bot.py`** - Testare específic Telegram
- **`test_tasks.py`** - Testare sarcini diverse
- **`test_various_scenarios.py`** - Testare scenarii variate

## 🚀 **Cum să Rulezi**

### **Teste Individuale**
```bash
# Test specific
python tests/unit/test_basic.py

# Test căutare produse
python tests/unit/test_product_search.py

# Test bot functionality
python tests/unit/test_bot_functionality.py
```

### **Toate Testele Unitare**
```bash
# Cu pytest (recomandat)
pytest tests/unit/ -v

# Manual, toate testele
python -m pytest tests/unit/
```

## 🎯 **Cerințe**

- Python 3.8+
- Toate dependențele din `requirements.txt`
- Configurare corectă a `.env` cu API keys
- Baza de date ChromaDB populată (pentru unele teste)

## 📊 **Categorii de Teste**

### **🧠 AI și Inteligență**
- Clasificarea intențiilor
- Generarea răspunsurilor
- Contextul conversațional
- Recomandările personalizate

### **🔍 Căutare și Produse**
- Căutarea în baza de date
- Filtrarea rezultatelor
- Recomandările bugetare
- Eliminarea duplicatelor

### **🤖 Funcționalități Bot**
- Procesarea mesajelor
- Gestionarea comenzilor
- Răspunsurile automate
- Integrarea platformelor

## 📝 **Note**

- Testele unitare sunt rapide și izolate
- Pot fi rulate independent
- Ideal pentru dezvoltare și debugging
- Acoperă funcționalități specifice
