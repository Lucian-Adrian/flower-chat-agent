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

### 5. Prepare Data

Ensure your data structure:

```
flower-chat-agent/
├── data/
│   └── chunks_data.csv     # Your product data
├── .env                    # Configuration
├── config.py              # Settings
└── test.py                # Main test file
```

### 6. Run Initial Test

```bash
python test.py
```

