import os

CHROMA_DB_PATH = "./chroma_db"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# CATEGORIES
CATEGORIES = {
    "flowers": ["peonies", "french roses", "bouquets", "premium"],
    "accessories": ["vases", "greeting card"],
    "gifts": ["sweets", "soft toys"],
    "fragrance": ["chando"],
    "seasonal": ["valentine", "mourning"]
}
    
# Search settings
DEFAULT_SEARCH_RESULTS = 5
MAX_SEARCH_RESULTS = 20