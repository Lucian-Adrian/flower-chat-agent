#!/usr/bin/env python3
"""
Compare direct ChromaDB calls vs AI engine calls
"""

import asyncio
import json
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('.')

async def compare_chromadb_calls():
    """Compare direct ChromaDB calls vs what AI engine is doing"""
    
    try:
        from src.data.chromadb_client import search_products_with_filters, search_products
        from google import genai
        import os
        
        # Step 1: Get Gemini analysis like AI engine does
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        test_message = "Aveți trandafiri roșii până în 1000 lei?"
        
        analysis_prompt = f"""
Analizează acest mesaj de la un client al florăriei XOFlowers și determină dacă este nevoie de căutare de produse:

Mesajul clientului: "{test_message}"
Context conversație: []

Răspunde în format JSON exact:
{{
    "needs_product_search": true/false,
    "search_terms": "termeni de căutare optimizați (dacă este necesar)",
    "price_range": {{"min": număr, "max": număr}} (doar dacă este menționat explicit),
    "category": "categorie de produse (dacă este relevantă)",
    "intent": "product_search/greeting/question/business_info/other",
    "confidence": 0.0-1.0,
    "reasoning": "de ce este/nu este nevoie de căutare"
}}
"""
        
        print("🔍 COMPARING CHROMADB CALLS")
        print("=" * 50)
        print(f"👤 Test message: '{test_message}'")
        
        analysis_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=analysis_prompt,
            config={'temperature': 0.3}
        )
        
        # Parse analysis
        analysis_text = analysis_response.text
        if "```json" in analysis_text:
            json_start = analysis_text.find("```json") + 7
            json_end = analysis_text.find("```", json_start)
            analysis_text = analysis_text[json_start:json_end].strip()
        
        analysis = json.loads(analysis_text)
        
        search_terms = analysis.get("search_terms", test_message)
        price_range = analysis.get("price_range", {})
        category = analysis.get("category")
        
        print(f"\n🧠 Gemini Analysis:")
        print(f"  Search terms: '{search_terms}'")
        print(f"  Price range: {price_range}")
        print(f"  Category: {category}")
        
        # Step 2: Build filters like AI engine does
        filters = {}
        
        if price_range:
            if price_range.get('max'):
                filters['max_price'] = price_range['max']
            if price_range.get('min'):
                filters['min_price'] = price_range['min']
        
        if category:
            filters['category'] = category
        
        print(f"\n🔧 Filters built: {filters}")
        
        # Step 3: Test different search approaches
        print(f"\n📊 TESTING DIFFERENT SEARCH APPROACHES:")
        
        # Test 1: Basic search (what works)
        print(f"\n1️⃣ Basic search:")
        basic_results = await search_products(search_terms, max_results=3)
        print(f"   Results: {len(basic_results)}")
        for i, p in enumerate(basic_results[:2], 1):
            print(f"   {i}. {p.get('name', 'N/A')} - {p.get('price', 'N/A')} MDL")
        
        # Test 2: Filtered search with empty filters
        print(f"\n2️⃣ Filtered search with empty filters:")
        empty_filter_results = await search_products_with_filters(
            query=search_terms,
            filters={},
            max_results=3
        )
        print(f"   Results: {len(empty_filter_results)}")
        for i, p in enumerate(empty_filter_results[:2], 1):
            print(f"   {i}. {p.get('name', 'N/A')} - {p.get('price', 'N/A')} MDL")
        
        # Test 3: Filtered search with actual filters (what AI engine does)
        print(f"\n3️⃣ Filtered search with price filters:")
        filtered_results = await search_products_with_filters(
            query=search_terms,
            filters=filters,
            max_results=3
        )
        print(f"   Results: {len(filtered_results)}")
        for i, p in enumerate(filtered_results[:2], 1):
            print(f"   {i}. {p.get('name', 'N/A')} - {p.get('price', 'N/A')} MDL")
        
        # Test 4: Try different price values
        print(f"\n4️⃣ Testing different price values:")
        for max_price in [1000, 2000, 5000]:
            test_results = await search_products_with_filters(
                query=search_terms,
                filters={"max_price": max_price},
                max_results=3
            )
            print(f"   max_price={max_price}: {len(test_results)} results")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(compare_chromadb_calls())
