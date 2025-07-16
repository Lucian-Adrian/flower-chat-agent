"""
Test semantic search functionality
"""

import sys
import os
sys.path.append('src/intelligence')

try:
    from product_search import SemanticSearchEngine, get_search_engine
    print("✅ Semantic search engine imported successfully")
    
    # Get search engine
    search_engine = get_search_engine()
    print("✅ Search engine initialized")
    
    # Test queries
    test_queries = [
        "buchete roșii pentru Valentine's Day",
        "trandafiri albi sub 1000 lei",
        "flori pentru mama",
        "cadou elegant pentru aniversare",
        "bujori roz"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        
        # Extract search intent
        search_intent = search_engine.extract_search_intent(query)
        print(f"   Intent: {search_intent}")
        
        # Perform search
        results = search_engine.search_products(search_intent, n_results=3)
        print(f"   Found {len(results)} results:")
        
        for i, result in enumerate(results, 1):
            product = result.product
            print(f"   {i}. {product['name']} - {product['price']} MDL")
            print(f"      Score: {result.similarity_score:.3f}")
            print(f"      {result.relevance_explanation}")
    
    print("\n🎉 Semantic search test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()