#!/usr/bin/env python3
"""
Enhanced AI System - Gemini Chat + ChromaDB Integration
Combines natural Gemini chat with smart product search
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables  
load_dotenv()

# Add current directory to Python path
sys.path.append('.')

async def test_enhanced_search():
    """Test AI-enhanced search query generation"""
    try:
        print("🧠 Testing AI-Enhanced Search...")
        
        from google import genai
        
        # Initialize Gemini
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        # User's original query
        user_query = "Este pentru mireasa, pana in 500 lei, vreau ceva frumos si ieftin"
        print(f"👤 User Query: {user_query}")
        
        # AI-enhanced search query generation
        search_prompt = f"""
Analizează această cerere de la un client pentru florărie și creează o căutare optimizată:

Cererea clientului: "{user_query}"

Generează:
1. Termeni de căutare optimizați pentru baza de date (în română)
2. Filtre de preț (max_price în MDL)
3. Categoria de produs

Răspunde în format JSON:
{{
    "search_terms": "termeni optimizați",
    "max_price": număr,
    "category": "categorie",
    "reasoning": "explicație"
}}
"""
        
        print(f"\n🤖 Generating enhanced search...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=search_prompt
        )
        
        print(f"✅ AI Enhanced Search:")
        print(response.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced search failed: {e}")
        return False

async def test_price_filtered_search():
    """Test ChromaDB search with price filtering"""
    try:
        print("\n💰 Testing Price-Filtered Search...")
        
        # Import ChromaDB client
        from src.data.chromadb_client import search_products_with_filters
        
        # Search with price filter
        filters = {
            "price_max": 500,  # Under 500 MDL
            "category": "buchete"  # Bouquets category
        }
        
        results = await search_products_with_filters(
            query="buchet mireasa nunta",
            filters=filters,
            max_results=5
        )
        
        print(f"✅ Filtered Results: {len(results)} products")
        
        for i, product in enumerate(results, 1):
            price = product.get('price', 0)
            print(f"{i}. {product.get('name', 'Unknown')}")
            print(f"   💰 {price} MDL")
            print(f"   📋 {product.get('category', 'N/A')}")
            
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Price filtered search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 ENHANCED AI + CHROMADB INTEGRATION TEST")
    print("="*60)
    
    # Run tests
    enhanced_search_works = asyncio.run(test_enhanced_search())
    price_filter_works = asyncio.run(test_price_filtered_search())
    
    print(f"\n📊 INTEGRATION TEST SUMMARY")
    print("="*60)
    print(f"🧠 AI Enhanced Search: {'✅ WORKING' if enhanced_search_works else '❌ FAILED'}")
    print(f"💰 Price Filtering: {'✅ WORKING' if price_filter_works else '❌ FAILED'}")
    
    if enhanced_search_works and price_filter_works:
        print(f"\n🎉 PERFECT! Ready for full integration!")
        print("✅ Gemini can enhance search queries")
        print("✅ ChromaDB can filter by price and category") 
        print("✅ Now we can combine them in the AI engine")
    else:
        print(f"\n🔧 Need to fix issues before full integration")
    
    print(f"\nEnhanced integration test completed.")
