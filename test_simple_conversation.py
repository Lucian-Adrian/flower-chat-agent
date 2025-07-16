"""
Simple test for the conversational AI system
"""

import sys
import os
sys.path.append('src/intelligence')

def test_basic_functionality():
    """Test basic functionality of each component"""
    
    print("🧪 Testing ChromaDB Manager...")
    try:
        from chromadb_manager import get_chromadb_manager
        chromadb = get_chromadb_manager()
        print(f"✅ ChromaDB initialized: {chromadb.initialized}")
        
        # Test search
        results = chromadb.search_products("trandafiri roșii", n_results=3)
        print(f"✅ Search test: found {len(results)} results")
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
    
    print("\n🧪 Testing Semantic Search...")
    try:
        from product_search import get_search_engine
        search_engine = get_search_engine()
        
        # Test search intent extraction
        search_intent = search_engine.extract_search_intent("vreau trandafiri roșii sub 500 lei")
        print(f"✅ Search intent: {search_intent}")
        
        # Test product search
        results = search_engine.search_products(search_intent, n_results=2)
        print(f"✅ Semantic search: found {len(results)} results")
        
    except Exception as e:
        print(f"❌ Semantic search test failed: {e}")
    
    print("\n🧪 Testing Context Manager...")
    try:
        from conversation_context import get_context_manager
        context_manager = get_context_manager()
        
        # Test session creation
        session = context_manager.get_or_create_session("test_user")
        session.add_message("user", "Salut!")
        session.add_message("assistant", "Bună ziua!")
        
        context = context_manager.get_conversation_context("test_user")
        print(f"✅ Context test: {len(context['recent_messages'])} messages")
        
    except Exception as e:
        print(f"❌ Context manager test failed: {e}")
    
    print("\n🧪 Testing AI Engine...")
    try:
        from ai_conversation_engine import get_ai_engine
        ai_engine = get_ai_engine()
        
        health = ai_engine.get_health_status()
        print(f"✅ AI Engine health: {health}")
        
    except Exception as e:
        print(f"❌ AI engine test failed: {e}")
    
    print("\n🎉 Basic functionality tests completed!")

def test_simple_conversation():
    """Test a simple conversation flow"""
    print("\n💬 Testing simple conversation...")
    
    try:
        # Import the updated conversation manager
        from conversation_manager import get_conversation_manager
        manager = get_conversation_manager()
        print("✅ Conversation manager loaded")
        
        # Test simple search
        results = manager.search_products("trandafiri")
        print(f"✅ Product search: found {len(results)} results")
        
        if results:
            print(f"   Example: {results[0].get('name', 'Unknown')} - {results[0].get('price', 0)} MDL")
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality()
    test_simple_conversation()