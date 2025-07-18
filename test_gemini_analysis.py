#!/usr/bin/env python3
"""
Test the exact Gemini analysis that's used in the AI engine
"""

import asyncio
import json
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append('.')

async def test_gemini_analysis():
    """Test Gemini analysis to see what search terms it's generating"""
    
    try:
        from google import genai
        import os
        
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        test_messages = [
            "Caut un buchet pentru o nuntă, vreau ceva elegant",
            "Aveți trandafiri roșii până în 1000 lei?",
            "Vreau flori pentru mama"
        ]
        
        print("🧠 TESTING GEMINI ANALYSIS FOR PRODUCT SEARCH")
        print("=" * 60)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n🔬 TEST {i}: '{message}'")
            print("-" * 40)
            
            analysis_prompt = f"""
Analizează acest mesaj de la un client al florăriei XOFlowers și determină dacă este nevoie de căutare de produse:

Mesajul clientului: "{message}"
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

Exemple:
- "Salut" → needs_product_search: false, intent: "greeting"
- "Caut buchete roșii" → needs_product_search: true, intent: "product_search"
- "Care e programul?" → needs_product_search: false, intent: "business_info"
"""
            
            try:
                analysis_response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=analysis_prompt,
                    config={'temperature': 0.3}
                )
                
                print(f"🤖 Raw Gemini Response:")
                print(f"'{analysis_response.text}'")
                
                # Parse the analysis
                try:
                    analysis_text = analysis_response.text
                    if "```json" in analysis_text:
                        json_start = analysis_text.find("```json") + 7
                        json_end = analysis_text.find("```", json_start)
                        analysis_text = analysis_text[json_start:json_end].strip()
                    
                    analysis = json.loads(analysis_text)
                    
                    print(f"\n📊 Parsed Analysis:")
                    print(f"  🔍 Needs search: {analysis.get('needs_product_search')}")
                    print(f"  🔎 Search terms: '{analysis.get('search_terms', 'N/A')}'")
                    print(f"  💰 Price range: {analysis.get('price_range', 'N/A')}")
                    print(f"  📂 Category: {analysis.get('category', 'N/A')}")
                    print(f"  🎯 Intent: {analysis.get('intent', 'N/A')}")
                    
                    # Test the search terms that Gemini generated
                    if analysis.get('needs_product_search') and analysis.get('search_terms'):
                        print(f"\n🔍 Testing generated search terms in ChromaDB...")
                        
                        from src.data.chromadb_client import search_products_with_filters
                        
                        search_terms = analysis.get('search_terms')
                        filters = {}
                        
                        price_range = analysis.get('price_range', {})
                        if price_range and price_range.get('max'):
                            filters['max_price'] = price_range['max']
                        
                        results = await search_products_with_filters(
                            query=search_terms,
                            filters=filters,
                            max_results=3
                        )
                        
                        print(f"  📦 ChromaDB Results: {len(results)} products")
                        for j, product in enumerate(results[:2], 1):
                            name = product.get('name', 'N/A')
                            price = product.get('price', 'N/A')
                            print(f"    {j}. {name} - {price} MDL")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
                    
            except Exception as e:
                print(f"❌ Gemini analysis failed: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_analysis())
