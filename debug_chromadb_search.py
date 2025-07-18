#!/usr/bin/env python3
"""
Debug ChromaDB Search to understand why no products are found
"""

import asyncio
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('.')

async def debug_chromadb_search():
    """Debug ChromaDB search to see what's happening"""
    
    try:
        from src.data.chromadb_client import search_products_with_filters, search_products
        
        test_queries = [
            "buchet pentru nuntă elegant",
            "trandafiri roșii",
            "flowers",
            "red roses",
            "wedding bouquet"
        ]
        
        print("🔍 DEBUGGING CHROMADB PRODUCT SEARCH")
        print("=" * 50)
        
        for query in test_queries:
            print(f"\n🔎 Testing query: '{query}'")
            
            try:
                # Test basic search first
                basic_results = await search_products(query, max_results=3)
                print(f"  📦 Basic search results: {len(basic_results)}")
                
                if basic_results:
                    for i, product in enumerate(basic_results[:2], 1):
                        name = product.get('name', 'N/A')
                        price = product.get('price', 'N/A')
                        print(f"    {i}. {name} - {price} MDL")
                
                # Test filtered search
                filtered_results = await search_products_with_filters(
                    query=query,
                    filters={},
                    max_results=3
                )
                print(f"  🔍 Filtered search results: {len(filtered_results)}")
                
                # Test with price filter
                price_filtered = await search_products_with_filters(
                    query=query,
                    filters={"max_price": 1000},
                    max_results=3
                )
                print(f"  💰 Price filtered (≤1000): {len(price_filtered)}")
                
            except Exception as e:
                print(f"  ❌ Search failed: {e}")
        
        # Test collection stats
        try:
            from src.data.chromadb_client import get_product_search_stats
            stats = get_product_search_stats()
            print(f"\n📊 ChromaDB Stats:")
            print(f"  Collection size: {stats.get('total_products', 'N/A')}")
            print(f"  Available: {stats.get('available', 'N/A')}")
        except Exception as e:
            print(f"\n⚠️ Stats failed: {e}")
            
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_chromadb_search())
