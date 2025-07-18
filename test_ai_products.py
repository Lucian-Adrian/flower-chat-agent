#!/usr/bin/env python3
"""
Test AI Engine Product Integration
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from src.intelligence.ai_engine import process_message_ai

async def test_ai_engine():
    print("Testing AI engine with product search...")
    
    # Test with a message that should trigger product search
    result = await process_message_ai(
        user_message="vreau un buchet pana in 900 lei, cu bujori sau cu ceva gingas",
        user_id="test_user_123"
    )
    
    print(f"AI Engine Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Intent: {result.get('intent')}")
    print(f"  Products found: {result.get('products_found', 0)}")
    print(f"  Products available: {len(result.get('products', []))}")
    print(f"  Service used: {result.get('service_used')}")
    
    products = result.get('products', [])
    if products:
        print(f"\nFirst 3 products:")
        for i, product in enumerate(products[:3], 1):
            name = product.get('name', 'No name')
            price = product.get('price', 0)
            url = product.get('url', 'No URL')
            print(f"  {i}. {name} - {price} MDL")
            print(f"     URL: {url}")
    else:
        print("No products returned!")
    
    print(f"\nFull response text (first 200 chars):")
    response = result.get('response', '')
    print(f"  {response[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_ai_engine())
