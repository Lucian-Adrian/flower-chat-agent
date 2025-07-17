#!/usr/bin/env python3
"""
Quick test for XOFlowers functionality
"""

import sys
import os
sys.path.insert(0, 'src')

def test_basic_imports():
    """Test basic imports"""
    print("🧪 Testing basic imports...")
    
    try:
        print("1. Testing ChromaDB search engine...")
        from database.chromadb_search_engine import search_products, get_stats
        stats = get_stats()
        print(f"   ✅ Database stats: {stats.get('total_products', 0)} products")
        
        print("2. Testing product search...")
        results = search_products("trandafiri", limit=3)
        print(f"   ✅ Search results: {len(results)} found")
        
        print("3. Testing conversation manager...")
        from intelligence.conversation_manager import get_conversation_manager
        cm = get_conversation_manager()
        print("   ✅ Conversation manager loaded")
        
        print("4. Testing simple conversation...")
        response = cm.process_message_sync("test_user", "Salut!")
        print(f"   ✅ Response: {response[:100]}...")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_basic_imports()
