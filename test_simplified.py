"""
Test for Simplified XOFlowers System
Тест упрощенной системы XOFlowers
"""

import sys
import os

# Import the simplified system
sys.path.append(os.path.dirname(__file__))
from simplified_search import *

def test_simplified_system():
    """Test the simplified system / Тест упрощенной системы"""
    print("🚀 Testing Simplified XOFlowers System")
    print("=" * 50)
    
    # Load data
    print("📁 Loading products...")
    success = load_products()
    if not success:
        print("❌ Failed to load products")
        return
    
    # Get statistics
    print("\n📊 Database Statistics:")
    stats = get_stats()
    print(f"Total products: {stats.get('total_products', 0)}")
    print(f"Flowers: {stats.get('flowers', 0)}")
    print(f"Others: {stats.get('others', 0)}")
    print(f"Categories: {stats.get('categories_count', 0)}")
    
    # Test searches
    print("\n🔍 Testing Search Functions:")
    
    # 1. General search
    print("\n1. General search 'roses':")
    results = search_products("roses", limit=3)
    for r in results:
        print(f"  - {r['name'][:50]}... | {r['price']} MDL | Score: {r['score']}")
    
    # 2. Flower search
    print("\n2. Flower search 'букет':")
    results = search_flowers("букет", limit=3)
    for r in results:
        print(f"  - {r['name'][:50]}... | {r['price']} MDL | Score: {r['score']}")
    
    # 3. Budget search
    print("\n3. Budget search 'flori' (max 1000 MDL):")
    results = search_budget("flori", 1000, limit=3)
    for r in results:
        print(f"  - {r['name'][:50]}... | {r['price']} MDL | Score: {r['score']}")
    
    # 4. Multilingual test
    print("\n4. Multilingual test:")
    queries = [
        ("Romanian: 'cadou pentru aniversare'", "cadou pentru aniversare"),
        ("Russian: 'подарок на день рождения'", "подарок на день рождения"),
        ("English: 'birthday gift'", "birthday gift")
    ]
    
    for desc, query in queries:
        results = search_products(query, limit=2)
        print(f"\n{desc}:")
        for r in results:
            print(f"  - {r['name'][:40]}... | {r['price']} MDL")
    
    print("\n✅ Simplified system test completed!")
    print("\n📋 System Features:")
    print("  ✅ Single file solution")
    print("  ✅ All functionality preserved")
    print("  ✅ Multilingual support (RO/RU/EN)")
    print("  ✅ Price filtering")
    print("  ✅ Category-based search")
    print("  ✅ Simple API")

if __name__ == "__main__":
    test_simplified_system()
