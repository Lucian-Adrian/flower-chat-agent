"""
ChromaDB settings with sentence-transformers embeddings
Configuration for creating and working with product database
"""

import os
from pathlib import Path

# === EMBEDDING MODEL ===
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# === PATHS AND DIRECTORIES ===
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_DIR = BASE_DIR / "chroma_db_products"

# CSV files
CSV_FILE = DATA_DIR / "final_products_case_standardized.csv"
FALLBACK_CSV = DATA_DIR / "chunks_data.csv"

# === PRODUCT CATEGORIES ===
PRODUCT_CATEGORIES = {
    "Additional Accessories / Vases",
    "Author'S Bouquets", 
    "Basket / Boxes With Flowers",
    "Bride'S Bouquet",
    "Chando",
    "Classic Bouquets",
    "French Roses",
    "Greeting Card",
    "Mono/Duo Bouquets",
    "Mourning Flower Arrangement",
    "Peonies",
    "Premium",
    "Soft Toys",
    "St. Valentine'S Day",
    "Sweets"
}

# Floral categories (for specialized search)
FLORAL_CATEGORIES = {
    "Author'S Bouquets",
    "Basket / Boxes With Flowers", 
    "Bride'S Bouquet",
    "Classic Bouquets",
    "French Roses",
    "Mono/Duo Bouquets",
    "Mourning Flower Arrangement",
    "Peonies",
    "Premium",
    "St. Valentine'S Day"
}

# Accessories and gifts
ACCESSORY_CATEGORIES = {
    "Additional Accessories / Vases",
    "Chando",
    "Greeting Card", 
    "Soft Toys",
    "Sweets"
}

# === CHROMADB SETTINGS ===
CHROMA_SETTINGS = {
    "collection_name_flowers": "xoflowers_products",
    "collection_name_all": "xoflowers_all_products",
    "distance_metric": "cosine",
    "embedding_function": "sentence_transformers"
}

# === SEARCH SETTINGS ===
SEARCH_SETTINGS = {
    "default_limit": 5,
    "max_limit": 50,
    "similarity_threshold": 0.3,
    "price_range_tolerance": 0.2
}

# === TEXT PROCESSING ===
TEXT_PROCESSING = {
    "max_description_length": 500,
    "combine_fields": ["primary_text", "category", "flower_type"],
    "price_extraction_patterns": [
        r"(\d+(?:\.\d+)?)\s*(?:lei|mdl|руб)",
        r"(\d+(?:\.\d+)?)"
    ],
    "supported_languages": ["english", "russian", "romanian"]  # Supported languages
}

# === VALIDATION ===
VALIDATION = {
    "required_columns": ["chunk_id", "primary_text", "category", "price"],
    "optional_columns": ["flower_type", "url", "is_verified"],
    "min_price": 0,
    "max_price": 50000
}

def get_csv_file():
    """Returns path to existing CSV file"""
    if CSV_FILE.exists():
        return CSV_FILE
    elif FALLBACK_CSV.exists():
        return FALLBACK_CSV
    else:
        raise FileNotFoundError(f"CSV files not found: {CSV_FILE}, {FALLBACK_CSV}")

def create_directories():
    """Creates necessary directories"""
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def is_floral_category(category):
    """Checks if category is floral"""
    return category in FLORAL_CATEGORIES

def is_accessory_category(category):
    """Checks if category is accessory/gift"""
    return category in ACCESSORY_CATEGORIES

def get_category_type(category):
    """Returns category type: 'floral', 'accessory' or 'other'"""
    if is_floral_category(category):
        return 'floral'
    elif is_accessory_category(category):
        return 'accessory'
    else:
        return 'other'

# === LOGGING ===
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "chromadb_operations.log"
}
