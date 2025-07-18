#!/usr/bin/env python3
"""
XOFlowers Telegram Bot Integration Test
======================================

Test the complete Telegram bot workflow including product buttons
"""

import sys
import os
from pathlib import Path
import asyncio

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv()

async def test_telegram_workflow():
    """Test the complete Telegram bot workflow"""
    print("🧪 Testing Complete Telegram Bot Workflow")
    print("=" * 50)
    
    try:
        # Import AI processing function
        from src.intelligence.ai_engine import process_message_ai
        
        print("✅ AI processing module imported")
        
        # Test product search messages
        test_messages = [
            "vreau buchete pentru mama, buget 200 lei",
            "caut flori pentru ziua de nastere",
            "flori de 8 martie pentru colege"
        ]
        
        for msg in test_messages:
            print(f"\n🔍 Testing message: '{msg}'")
            
            try:
                # Process message exactly like Telegram bot does
                ai_result = await process_message_ai(
                    user_message=msg,
                    user_id="test_user_telegram"
                )
                
                print(f"✅ AI processing successful")
                print(f"   Response length: {len(ai_result.get('response', ''))}")
                print(f"   Intent: {ai_result.get('intent', 'unknown')}")
                print(f"   Products found: {ai_result.get('products_found', False)}")
                
                # Check if products are available for buttons
                if ai_result and ai_result.get('products'):
                    products = ai_result.get('products', [])
                    print(f"   🎯 Found {len(products)} products for buttons:")
                    
                    for i, product in enumerate(products[:3]):
                        name = product.get('name', 'Unknown')
                        price = product.get('price', 'N/A')
                        url = product.get('url', 'No URL')
                        print(f"     {i+1}. {name} - {price} lei")
                        print(f"        URL: {url}")
                    
                    # Simulate button creation
                    print(f"   ✅ Would create {min(len(products), 5)} product buttons")
                    
                else:
                    print(f"   ⚠️  No products found for buttons")
                    print(f"       ai_result keys: {list(ai_result.keys()) if ai_result else 'No ai_result'}")
                    if ai_result:
                        print(f"       products field: {ai_result.get('products', 'Missing')}")
                
            except Exception as e:
                print(f"   ❌ Error processing message: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("🎯 Telegram workflow test complete!")
        
        # Test button creation function
        print("\n🔘 Testing Button Creation Function...")
        
        try:
            from src.api.telegram_app import XOFlowersTelegramBot
            
            # Create test products
            test_products = [
                {
                    'name': 'Buchet elegant de trandafiri',
                    'price': 150.0,
                    'url': 'https://xoflowers.md/buchet-trandafiri'
                },
                {
                    'name': 'Aranjament floral pentru ziua de nastere',
                    'price': 200.0,
                    'url': 'https://xoflowers.md/aranjament-ziua-nastere'
                }
            ]
            
            bot = XOFlowersTelegramBot()
            reply_markup = bot._create_product_buttons(test_products, max_buttons=5)
            
            if reply_markup:
                print("✅ Button creation successful!")
                print(f"   Created {len(reply_markup.inline_keyboard)} buttons")
                for i, row in enumerate(reply_markup.inline_keyboard):
                    button = row[0]  # First button in row
                    print(f"   Button {i+1}: '{button.text}' -> {button.url}")
            else:
                print("❌ Button creation failed")
                
        except Exception as e:
            print(f"❌ Button creation test failed: {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram_workflow())
