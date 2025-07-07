# flower-chat-agent

# 🌸 XoFlowers ChromaDB - Setup Guide

### 1. Clone Repository

```bash
git clone https://github.com/Lucian-Adrian/flower-chat-agent.git
cd flower-chat-agent
```

### 2. Create Virtual Environment

```bash
# Or using venv
python -m venv ai_agents_env
source ai_agents_env/bin/activate  # Linux/Mac
# ai_agents_env\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**

- `chromadb` - Vector database
- `sentence-transformers` - Local embeddings
- `pandas` - Data processing
- `python-dotenv` - Environment configuration

### 4. Setup Configuration

Create `.env` file in project root:

```env
# ChromaDB settings
CHROMA_DB_PATH=./chroma_db

# Embedding model (local, no API key needed)
USE_LOCAL_EMBEDDINGS=true
LOCAL_EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# OpenAI API (optional, for future chatbot features)
OPENAI_API_KEY=your-key-here
```

### 5. Project Structure

```
flower-chat-agent/
├── data/
│   ├── chunks_data.csv              # Product database (724 items)
│   ├── multilingual_faq.json        # FAQ responses (3 languages)
│   ├── multilingual_mapping.json    # Language mappings & synonyms
│   ├── multilingual_responses.json  # Response templates
│   └── language_detection.json      # Intent classification patterns
├── config.py                        # Categories & settings
├── setup_database.py               # Main XoFlowersDB class
├── test.py                          # Comprehensive testing
├── requirements.txt                 # Dependencies
└── .env                            # Configuration (create this)
```

### 6. Initialize Database

```bash
python setup_database.py
```

This will:

- Create ChromaDB collections
- Load 724 products from CSV
- Generate multilingual embeddings
- Display loading statistics

### 7. Run Tests

```bash
python test.py
```

This will test:

- Database loading
- Search functionality
- Multilingual queries
- Performance metrics
