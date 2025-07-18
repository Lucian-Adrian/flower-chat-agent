#!/usr/bin/env python3
"""
ChromaDB Data Analysis
Analyze what products are actually in the database
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables  
load_dotenv()

# Add current directory to Python path
sys.path.append('.')

async def analyze_chromadb_data():
    """Analyze ChromaDB data structure and pricing"""
    try:
        print("🔍 Analyzing ChromaDB Data...")
        
        from src.data.chromadb_client import chromadb_client
        
        # Get collection stats
        stats = chromadb_client.get_collection_stats()
        print(f"📊 Collection Stats:")
        print(f"   Total products: {stats.get('total_documents', 'Unknown')}")
        
        # Get some sample products to understand data structure
        print(f"\n📋 Sample Products Analysis...")
        
        # Try a simple search to get products
        results = await chromadb_client.search_products("flori", max_results=10)
        
        print(f"✅ Found {len(results)} sample products:")
        
        prices = []
        categories = set()
        
        for i, product in enumerate(results[:5], 1):
            name = product.get('name', 'Unknown')
            price = product.get('price', 0)
            category = product.get('category', 'Unknown')
            
            print(f"\n{i}. {name}")
            print(f"   💰 Price: {price} (type: {type(price)})")
            print(f"   📋 Category: {category}")
            print(f"   🔑 Keys: {list(product.keys())}")
            
            if price and str(price).replace('.', '').isdigit():
                prices.append(float(price))
            categories.add(category)
        
        if prices:
            print(f"\n💰 Price Analysis:")
            print(f"   Min price: {min(prices)} MDL")
            print(f"   Max price: {max(prices)} MDL")
            print(f"   Average: {sum(prices)/len(prices):.2f} MDL")
            print(f"   Under 500 MDL: {len([p for p in prices if p <= 500])}/{len(prices)}")
        
        print(f"\n📋 Categories found: {categories}")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Data analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_specific_searches():
    """Test specific search terms"""
    searches = [
        "buchet",
        "trandafir", 
        "floare",
        "nunta",
        "mireasa"
    ]
    
    print(f"\n🔍 Testing Specific Search Terms...")
    
    from src.data.chromadb_client import search_products
    
    for term in searches:
        try:
            results = await search_products(term, max_results=3)
            print(f"\n'{term}': {len(results)} results")
            
            for product in results[:2]:  # Show first 2
                name = product.get('name', 'Unknown')
                price = product.get('price', 'N/A')
                print(f"  • {name[:50]}... - {price} MDL")
                
        except Exception as e:
            print(f"  • '{term}': Error - {e}")

if __name__ == "__main__":
    print("🔬 CHROMADB DATA ANALYSIS")
    print("="*60)
    
    # Run analysis
    data_analyzed = asyncio.run(analyze_chromadb_data())
    
    if data_analyzed:
        asyncio.run(test_specific_searches())
    
    print(f"\nData analysis completed.")
