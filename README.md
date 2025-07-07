# XOFlowers Instagram AI Agent Chatbot

Acest proiect implementează un chatbot AI inteligent pentru XOFlowers care poate fi integrat cu Instagram și folosit pentru a răspunde automat la întrebările clienților despre flori și servicii.

## Caracteristici

- 🤖 **AI-powered** - Folosește OpenAI pentru răspunsuri inteligente
- 🔍 **Recunoașterea intent-urilor** - Detectează automat ce vrea clientul
- 🏷️ **Extragerea entităților** - Identifică produse, culori, prețuri, etc.
- 📊 **Baza de date** - Stochează conversații și produse
- 🌐 **API REST** - Endpoints pentru chat, produse și analiză
- 📱 **Instagram ready** - Webhook pentru integrarea cu Instagram
- 🌸 **Multilingv** - Suport pentru română, engleză și rusă

## Structura proiectului

```
XOFlowers Instagram AI agent chatbot/
├── app.py                      # Aplicația Flask principală
├── setup_database.py           # Script pentru inițializarea bazei de date
├── requirements.txt            # Dependențele Python
├── .env.example               # Exemplu de configurare environment
├── README.md                  # Documentația proiectului
├── chunks_data.csv            # Date procesate despre produse (709 produse)
├── products.csv               # Produse curate și deduplicate
├── multilingual_mapping.json  # Mapări multilingve și sinonime
├── multilingual_faq.json      # FAQ în RO/EN/RU
├── chromadb_config.json       # Configurare pentru ChromaDB
└── collection_descriptions.json # Descrieri colecții produse
```

## Instalare și configurare

### 1. Instalarea dependențelor

```bash
pip install -r requirements.txt
```

### 2. Configurarea environment-ului

Copiați `.env.example` la `.env` și completați cu cheile voastre:

```bash
cp .env.example .env
```

Editați `.env` cu cheile voastre reale:
```
OPENAI_KEY=sk-your-actual-openai-key
INSTAGRAM_VERIFY_TOKEN=your-verify-token
INSTAGRAM_ACCESS_TOKEN=your-access-token
```

### 3. Inițializarea bazei de date

```bash
python setup_database.py
```

Acest script va:
- Crea baza de date SQLite
- Încărca toate produsele din `chunks_data.csv` (709 produse)
- Crea conversații de test

### 4. Rularea aplicației

```bash
python app.py
```

Aplicația va rula pe `http://localhost:5000`

## Utilizare

### API Endpoints

#### 1. Chat cu AI-ul
```bash
POST /api/chat
{
    "message": "Vreau trandafiri roșii pentru ziua de naștere",
    "user_id": "user123"
}
```

#### 2. Căutare produse
```bash
GET /api/products?category=roses&color=red&price_range=mid-range
```

#### 3. Analiză conversații
```bash
GET /api/analytics
```

#### 4. Webhook Instagram
```bash
GET /webhook?hub.mode=subscribe&hub.verify_token=your_token&hub.challenge=challenge
POST /webhook  # Pentru mesajele primite
```

### Testare

Puteți testa chatbot-ul cu următoarele mesaje:

```bash
# Căutare produse
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Vreau trandafiri roșii", "user_id": "test_user"}'

# Întrebări generale
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Care este programul magazinului?", "user_id": "test_user"}'

# Abonament
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Vreau un abonament lunar", "user_id": "test_user"}'
```

## Arhitectura chatbot-ului

### 1. **IntentRecognizer** 
Detectează ce vrea utilizatorul:
- `find_product` - Caută produse
- `ask_question` - Întrebări generale
- `subscribe` - Abonament
- `pay_for_product` - Finalizare comandă
- `greeting` - Salutări
- `complaint` - Plângeri

### 2. **EntityExtractor**
Extrage entități relevante:
- `product_type` - tipul produsului (buchet, cutie, etc.)
- `color` - culoarea dorită
- `occasion` - ocazia (ziua de naștere, nuntă, etc.)
- `price_range` - gama de preț
- `payment_method` - metoda de plată

### 3. **DatabaseManager**
Gestionează baza de date cu:
- Conversații (pentru analiză și învățare)
- Produse (709 produse din cataloagul XOFlowers)
- Filtrare inteligentă după criterii

### 4. **XOFlowersAgent**
Coordonează toate componentele pentru:
- Procesarea mesajelor
- Generarea răspunsurilor
- Integrarea cu OpenAI
- Logarea conversațiilor

## Date disponibile

Proiectul include date complete procesate:

- **709 produse** în `chunks_data.csv`
- **7 categorii principale**: Chando, Peonies, French roses, Basket/Boxes with flowers, Author's bouquets, etc.
- **Descrieri multilingve** în română și engleză
- **Prețuri** de la 565 la 11500 MDL
- **Mapări multilingve** pentru sinonime și traduceri

## Integrarea cu Instagram

Pentru a conecta chatbot-ul la Instagram:

1. **Creați o aplicație Facebook/Instagram** pe developers.facebook.com
2. **Configurați webhook-ul** să pointeze la `/webhook`
3. **Setați token-urile** în `.env`
4. **Activați permisiunile** pentru mesaje

## Analiză și monitorizare

Chatbot-ul oferă analiză detaliată:
- Numărul total de conversații
- Distribuția intent-urilor
- Activitatea recentă
- Entitățile cel mai des căutate

## Dezvoltare viitoare

Funcționalități planificate:
- Integrare ChromaDB pentru căutare semantică
- Suport pentru imagini produse
- Sistem de recomandări personalizate
- Integrare cu sisteme de plată
- Dashboard admin pentru monitorizare

## Suport tehnic

Pentru întrebări sau probleme:
1. Verificați că toate dependențele sunt instalate
2. Asigurați-vă că `.env` este configurat corect
3. Rulați `setup_database.py` pentru a inițializa datele
4. Verificați log-urile pentru erori

## Licență

Acest proiect este dezvoltat pentru XOFlowers și conține date proprietare ale companiei.
