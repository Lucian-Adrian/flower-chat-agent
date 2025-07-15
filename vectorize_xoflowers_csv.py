import pandas as pd
from tqdm import tqdm
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

# Config
CSV_PATH = os.path.join(os.path.dirname(__file__), '../Downloads/xoflowers_final_simplified.csv')
CHROMA_PATH = os.path.join(os.path.dirname(__file__), 'chroma_db')
COLLECTION_NAME = 'flowers_products'
EMBEDDING_MODEL = 'all-mpnet-base-v2'  # One of the strongest for semantic search

# Load CSV
df = pd.read_csv(CSV_PATH)

# Prepare texts for vectorization
texts = df['primary_text'].astype(str).tolist()
metadatas = df.drop(columns=['primary_text']).to_dict(orient='records')

# Load embedding model
model = SentenceTransformer(EMBEDDING_MODEL)

# Create ChromaDB client
client = chromadb.Client(Settings(
    persist_directory=CHROMA_PATH,
    anonymized_telemetry=False
))

# Create or get collection
collection = client.get_or_create_collection(COLLECTION_NAME)

# Vectorize and add to ChromaDB
for i in tqdm(range(0, len(texts), 64)):
    batch_texts = texts[i:i+64]
    batch_metadatas = metadatas[i:i+64]
    embeddings = model.encode(batch_texts, show_progress_bar=False, normalize_embeddings=True)
    ids = [f"product_{i+j:04d}" for j in range(len(batch_texts))]
    collection.add(
        embeddings=embeddings.tolist(),
        documents=batch_texts,
        metadatas=batch_metadatas,
        ids=ids
    )

print(f"Vectorizare completă! {len(texts)} produse adăugate în ChromaDB la {CHROMA_PATH}")
