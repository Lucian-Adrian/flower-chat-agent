"""
Test ChromaDB Connection and Basic Search
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from intelligence.chromadb_manager import get_chromadb_manager

def test_database_connection():
    """
    Tests the database connection and a simple search.
    """
    print("Testing ChromaDB Connection and Search")
    
    try:
        db_manager = get_chromadb_manager()
        
        if not db_manager.initialized:
            print("ChromaDB connection failed.")
            return

        print("ChromaDB connection successful.")
        
        # Test a simple search
        query = "trandafiri"
        print(f"Performing a test search for: '{query}'")
        results = db_manager.search_products(query, n_results=1)
        
        if results:
            print("Test search returned results:")
            for product in results:
                print(f"  - Found: {product['name']} (Score: {product['similarity_score']:.2f})")
        else:
            print("Test search returned no results. The database might be empty.")
            print("   Run 'python scripts/populate_db.py' to populate it.")

    except Exception as e:
        print(f"An error occurred during the database test: {e}")

if __name__ == "__main__":
    test_database_connection()
