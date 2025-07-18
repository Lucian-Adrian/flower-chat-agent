#!/usr/bin/env python3
"""
Enhanced Gemini Chat with ChromaDB Integration  
Perfect combination: Natural chat + Smart product search
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List

async def enhanced_gemini_chat_with_products(user_message: str, user_id: str) -> Dict[str, Any]:
    """
    Enhanced Gemini Chat that can intelligently call ChromaDB when needed
    
    Args:
        user_message: User's message
        user_id: User identifier
        
    Returns:
        Response with products if relevant
    """
    
    try:
        print(f"🤖 Enhanced Gemini Chat Processing...")
        print(f"👤 User: {user_message}")
        
        # Step 1: Use Gemini to analyze if product search is needed
        from google import genai
        import os
        
        client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
        
        analysis_prompt = f"""
Analizează acest mesaj de la un client al florăriei XOFlowers și determină dacă este nevoie de căutare de produse:

Mesajul clientului: "{user_message}"

Răspunde în format JSON:
{{
    "needs_product_search": true/false,
    "search_terms": "termeni de căutare optimizați (dacă este necesar)",
    "price_range": {{"min": număr, "max": număr}} (dacă este menționat),
    "category": "categorie de produse (dacă este relevantă)",
    "intent": "product_search/greeting/question/other",
    "reasoning": "de ce este/nu este nevoie de căutare"
}}

Exemple:
- "Salut" → needs_product_search: false, intent: "greeting"
- "Caut buchete roșii" → needs_product_search: true, intent: "product_search"
- "Care e programul?" → needs_product_search: false, intent: "question"
"""
        
        print(f"🧠 Analyzing message with Gemini...")
        analysis_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=analysis_prompt
        )
        
        print(f"✅ Analysis: {analysis_response.text[:200]}...")
        
        # Parse the analysis
        try:
            # Extract JSON from response
            analysis_text = analysis_response.text
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                analysis_text = analysis_text[json_start:json_end].strip()
            
            analysis = json.loads(analysis_text)
        except:
            # Fallback if JSON parsing fails
            analysis = {
                "needs_product_search": "buchet" in user_message.lower() or "flor" in user_message.lower(),
                "intent": "general"
            }
        
        # Step 2: Search products if needed
        products = []
        if analysis.get("needs_product_search", False):
            print(f"🔍 Product search needed - searching ChromaDB...")
            
            try:
                from src.data.chromadb_client import search_products
                
                search_terms = analysis.get("search_terms", user_message)
                print(f"📝 Search terms: {search_terms}")
                
                products = await search_products(search_terms, max_results=5)
                print(f"✅ Found {len(products)} products")
                
                # Filter by price if specified
                price_range = analysis.get("price_range", {})
                if price_range.get("max"):
                    max_price = price_range["max"]
                    products = [p for p in products if float(p.get('price', 0)) <= max_price]
                    print(f"💰 After price filtering (≤{max_price}): {len(products)} products")
                    
            except Exception as e:
                print(f"⚠️ Product search failed: {e}")
                products = []
        
        # Step 3: Generate response with Gemini using context
        context_prompt = f"""
Tu ești consultantul floral al XOFlowers din Chișinău, Moldova. Răspunde natural și prietenos în română.

Mesajul clientului: "{user_message}"

{"PRODUSE GĂSITE:" if products else "NU S-AU GĂSIT PRODUSE SPECIFICE."}
{chr(10).join([f"• {p.get('name', 'Produs')} - {p.get('price', 'N/A')} MDL ({p.get('category', 'N/A')})" for p in products[:3]]) if products else ""}

Răspunde natural, mentionând produsele relevante dacă există, sau oferind alternative și sfaturi generale despre flori.
Păstrează tonul prietenos și profesional al unui consultant floral expert.
Nu folosi markdown sau formatare specială - doar text simplu.
"""
        
        print(f"💬 Generating natural response...")
        final_response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=context_prompt
        )
        
        response_text = final_response.text
        print(f"✅ Response generated: {len(response_text)} characters")
        
        return {
            "response": response_text,
            "success": True,
            "products": products,
            "intent": analysis.get("intent", "general"),
            "needs_product_search": analysis.get("needs_product_search", False),
            "products_found": len(products),
            "service_used": "enhanced_gemini_chat",
            "processing_time": 0  # Will be calculated externally
        }
        
    except Exception as e:
        print(f"❌ Enhanced chat failed: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "response": "Îmi pare rău, am întâmpinat o problemă tehnică. Cu ce vă pot ajuta?",
            "success": False,
            "products": [],
            "error": str(e),
            "service_used": "enhanced_gemini_chat_fallback"
        }

# Test the enhanced system
async def test_enhanced_system():
    """Test the enhanced Gemini + ChromaDB system"""
    
    test_cases = [
        "Salut!",
        "Vreau un buchet pentru o nunta maine",
        "Este pentru mireasa, pana in 1500 lei, vreau ceva frumos",
        "Care e programul vostru?",
        "Aveți trandafiri roșii?"
    ]
    
    print("🚀 TESTING ENHANCED GEMINI CHAT + CHROMADB")
    print("="*70)
    
    for i, test_message in enumerate(test_cases, 1):
        print(f"\n🔬 TEST {i}/{len(test_cases)}")
        print("="*50)
        
        start_time = time.time()
        result = await enhanced_gemini_chat_with_products(test_message, f"test_user_{i}")
        processing_time = time.time() - start_time
        
        print(f"\n📊 RESULTS:")
        print(f"✅ Success: {result.get('success')}")
        print(f"🎯 Intent: {result.get('intent')}")
        print(f"🔍 Needed Search: {result.get('needs_product_search')}")
        print(f"🛍️ Products Found: {result.get('products_found', 0)}")
        print(f"⏱️ Time: {processing_time:.2f}s")
        
        print(f"\n💬 Response:")
        print(f"'{result.get('response', 'No response')[:200]}...'")
        
        if result.get('products'):
            print(f"\n🛍️ Products:")
            for product in result['products'][:2]:
                print(f"  • {product.get('name')} - {product.get('price')} MDL")

if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Add current directory to Python path
    sys.path.append('.')
    
    # Run the test
    asyncio.run(test_enhanced_system())
