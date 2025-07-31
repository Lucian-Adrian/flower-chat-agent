import os
import sys
import csv
import json
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.manager import DatabaseManager

PRODUCTS_CSV = os.path.join(os.path.dirname(__file__), 'products.csv')
COLLECTION_NAME = 'products'

def load_products_from_csv(csv_path: str) -> List[Dict]:
    products = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Normalize price
            try:
                price = float(row.get('price', 0))
            except Exception:
                price = 0.0
            product = {
                'id': row.get('id', row.get('product_id', '')),
                'name': row.get('name', ''),
                'description': row.get('description', row.get('full_description', '')),
                'price': price,
                'category': row.get('category', ''),
                'url': row.get('url', ''),
                'metadata': {k: v for k, v in row.items() if k not in ['id','name','description','price','category','url']}
            }
            products.append(product)
    return products

def index_products_to_chromadb():
    print(f"🔄 Indexing products from {PRODUCTS_CSV} into ChromaDB...")
    db = DatabaseManager()
    products = load_products_from_csv(PRODUCTS_CSV)
    docs = []
    for prod in products:
        docs.append({
            'id': prod['id'],
            'text': f"{prod['name']} {prod['description']} {prod['category']}",
            'metadata': {
                'price': prod['price'],
                'category': prod['category'],
                'url': prod['url'],
                **prod['metadata']
            }
        })
    db.add_documents(COLLECTION_NAME, docs)
    print(f"✅ Indexed {len(docs)} products into ChromaDB collection '{COLLECTION_NAME}'")

def search_products_chromadb(query: str, n_results: int = 5):
    db = DatabaseManager()
    results = db.search_documents(COLLECTION_NAME, query, n_results)
    print(f"\n🔍 Search results for: '{query}'")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['text']}")
        print(f"   Category: {res['metadata'].get('category','')}, Price: {res['metadata'].get('price','')} MDL")
        print(f"   URL: {res['metadata'].get('url','')}")
        print(f"   Distance: {res.get('distance')}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Index and search products in ChromaDB")
    parser.add_argument('--index', action='store_true', help='Index all products from CSV into ChromaDB')
    parser.add_argument('--search', type=str, help='Search query for products')
    parser.add_argument('--n', type=int, default=5, help='Number of results to return')
    args = parser.parse_args()
    if args.index:
        index_products_to_chromadb()
    if args.search:
        search_products_chromadb(args.search, args.n)
