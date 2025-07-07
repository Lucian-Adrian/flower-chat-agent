import csv
import sqlite3
import json
from contextlib import contextmanager

def load_products_from_csv():
    """Load products from chunks_data.csv into SQLite database"""
    
    @contextmanager
    def get_connection():
        conn = sqlite3.connect("xoflowers.db")
        try:
            yield conn
        finally:
            conn.close()
    
    # Initialize database
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                category TEXT,
                flower_type TEXT,
                url TEXT,
                chunk_id TEXT UNIQUE,
                in_stock BOOLEAN DEFAULT 1
            )
        ''')
        conn.commit()
    
    # Load data from CSV
    products_loaded = 0
    
    try:
        with open('chunks_data.csv', 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            with get_connection() as conn:
                for row in reader:
                    if row['chunk_type'] == 'product':
                        # Extract product name from primary_text
                        description = row['primary_text']
                        name = description.split(' - ')[0] if ' - ' in description else description[:100]
                        
                        try:
                            conn.execute('''
                                INSERT OR REPLACE INTO products 
                                (chunk_id, name, description, price, category, flower_type, url, in_stock)
                                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                            ''', (
                                row['chunk_id'],
                                name,
                                description,
                                float(row['price']) if row['price'] else 0.0,
                                row['category'],
                                row['flower_type'],
                                row['url']
                            ))
                            products_loaded += 1
                        except Exception as e:
                            print(f"Error inserting product {row['chunk_id']}: {e}")
                
                conn.commit()
    
    except FileNotFoundError:
        print("chunks_data.csv not found. Please ensure the file exists in the current directory.")
        return False
    
    print(f"Successfully loaded {products_loaded} products into database.")
    return True

def create_sample_conversations():
    """Create some sample conversations for testing"""
    
    @contextmanager
    def get_connection():
        conn = sqlite3.connect("xoflowers.db")
        try:
            yield conn
        finally:
            conn.close()
    
    sample_conversations = [
        {
            "user_id": "test_user_1",
            "message": "Salut! Vreau niște trandafiri roșii",
            "intent": "find_product",
            "entities": '{"product_type": "trandafiri", "color": "roșu"}',
            "response": "Bună! Avem trandafiri roșii frumoși. Vă pot recomanda câteva opțiuni..."
        },
        {
            "user_id": "test_user_2", 
            "message": "Cât costă livrarea?",
            "intent": "ask_question",
            "entities": '{}',
            "response": "Livrarea în Chișinău costă 50 MDL."
        },
        {
            "user_id": "test_user_3",
            "message": "Vreau un abonament lunar",
            "intent": "subscribe", 
            "entities": '{"subscription_type": "lunar"}',
            "response": "Excelent! Vă putem oferi un abonament lunar de flori..."
        }
    ]
    
    with get_connection() as conn:
        for conv in sample_conversations:
            conn.execute('''
                INSERT INTO conversations (user_id, message, intent, entities, response)
                VALUES (?, ?, ?, ?, ?)
            ''', (conv["user_id"], conv["message"], conv["intent"], conv["entities"], conv["response"]))
        
        conn.commit()
    
    print(f"Created {len(sample_conversations)} sample conversations.")

if __name__ == "__main__":
    print("Setting up XOFlowers database...")
    
    # Load products
    if load_products_from_csv():
        print("✅ Products loaded successfully")
    else:
        print("❌ Failed to load products")
    
    # Create sample conversations
    create_sample_conversations()
    print("✅ Sample conversations created")
    
    print("\nDatabase setup complete! You can now run the Flask app with: python app.py")
