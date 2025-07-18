#!/usr/bin/env python3
"""
XOFlowers Product Button Test
=============================

Test the product recommendation with buttons functionality
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

async def test_product_buttons():
    """Test product button functionality"""
    print("🧪 Testing Product Button Functionality")
    print("=" * 40)
    
    try:
        # Import modules
        from src.intelligence.ai_engine import AIEngine
        from src.data.chromadb_client import ChromaDBClient
        
        # Initialize AI engine
        ai = AIEngine()
        print("✅ AI Engine initialized")
        
        # Test product search messages
        test_messages = [
            "vreau flori pentru iubita mea, buget 200 lei",
            "caut buchete pentru mama, ceva elegant", 
            "flori pentru ziua de nastere, 150 lei maxim",
            "flori de Martisor pentru colege"
        ]
        
        for msg in test_messages:
            print(f"\n🔍 Testing: '{msg}'")
            
            try:
                result = await ai.process_message_ai(
                    user_message=msg,
                    user_id="test_user"
                )
                
                print(f"Response: {result['response'][:100]}...")
                
                if 'products' in result and result['products']:
                    print(f"✅ Found {len(result['products'])} products:")
                    for p in result['products'][:3]:  # Show first 3
                        print(f"  - {p.get('name', 'Unknown')}: {p.get('price', 'N/A')} lei")
                        print(f"    URL: {p.get('url', 'No URL')}")
                else:
                    print("⚠️  No products found in result")
                    print(f"Result keys: {list(result.keys())}")
                
            except Exception as e:
                print(f"❌ Error processing message: {e}")
        
        print("\n" + "=" * 40)
        print("🎯 Product button test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_product_buttons())
