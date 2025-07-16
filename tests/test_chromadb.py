"""
Simple test script to verify ChromaDB setup
"""

import sys
import os
sys.path.append('src/intelligence')

try:
    from chromadb_manager import ChromaDBManager, Product
    print("✅ ChromaDB manager imported successfully")
    
    # Test ChromaDB initialization
    manager = ChromaDBManager()
    print(f"✅ ChromaDB initialized: {manager.initialized}")
    
    if manager.initialized:
        # Test adding a simple product
        test_product = Product(
            id="test_001",
            name="Test Bouquet",
            description="Beautiful test bouquet with red roses",
            price=500.0,
            category="Test",
            colors=["roșu"],
            occasions=["test"]
        )
        
        success = manager.add_products([test_product], 'products_main')
        print(f"✅ Test product added: {success}")
        
        # Test search
        results = manager.search_products("red roses", n_results=1)
        print(f"✅ Search test: found {len(results)} results")
        
        # Get stats
        stats = manager.get_collection_stats()
        print(f"✅ Database stats: {stats}")
        
    else:
        print("❌ ChromaDB not initialized properly")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()