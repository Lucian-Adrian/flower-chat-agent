"""
Debug ChromaDB data
"""

import chromadb
from chromadb.config import Settings

db = chromadb.PersistentClient(path='./chroma_db_flowers', settings=Settings(anonymized_telemetry=False))
collection = db.get_collection('flowers_products')
results = collection.get(limit=3)

print('Sample data:')
for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
    print(f'{i+1}. ID: {results["ids"][i]}')
    print(f'   Name: {metadata.get("name", "MISSING")}')
    print(f'   Price: {metadata.get("price", "MISSING")}')
    print(f'   Category: {metadata.get("category", "MISSING")}')
    print(f'   Document: {doc[:100]}...')
    print()
