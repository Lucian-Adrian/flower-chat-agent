#!/usr/bin/env python3
"""
XOFlowers System Verification
============================

Final comprehensive test to verify all systems working
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

async def verify_complete_system():
    """Complete system verification"""
    print("🔍 XOFlowers Complete System Verification")
    print("=" * 50)
    
    test_cases = [
        # Budget constraints
        {"msg": "vreau buchete pentru mama, buget 200 lei", "expect": "products"},
        {"msg": "flori pentru ziua de nastere, maxim 150 lei", "expect": "products"},
        
        # Category searches  
        {"msg": "caut flori pentru ziua de nastere", "expect": "products"},
        {"msg": "flori de 8 martie pentru colege", "expect": "products"},
        {"msg": "buchete elegante pentru iubita", "expect": "products"},
        
        # General queries
        {"msg": "ce flori recomandati pentru aniversare", "expect": "products"},
        {"msg": "vreau ceva frumos pentru sotia mea", "expect": "products"},
        
        # Edge cases
        {"msg": "buna ziua", "expect": "greeting"},
        {"msg": "multumesc", "expect": "thanks"}
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    try:
        from src.intelligence.ai_engine import process_message_ai
        print("✅ AI engine imported successfully")
        
        for i, test in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}/{total_tests}: '{test['msg']}'")
            
            try:
                result = await process_message_ai(
                    user_message=test['msg'],
                    user_id=f"verify_user_{i}"
                )
                
                response_len = len(result.get('response', ''))
                intent = result.get('intent', 'unknown')
                products_found = result.get('products_found', 0)
                products = result.get('products', [])
                
                print(f"   ✅ Response: {response_len} chars")
                print(f"   📋 Intent: {intent}")
                print(f"   🛒 Products: {products_found} found")
                
                if test['expect'] == 'products':
                    if products_found > 0 and len(products) > 0:
                        print(f"   🎯 SUCCESS - Found {len(products)} products with buttons")
                        # Show first product
                        if products:
                            p = products[0]
                            print(f"      Example: {p.get('name', 'N/A')[:40]}...")
                            print(f"      URL: {p.get('url', 'No URL')}")
                        success_count += 1
                    else:
                        print(f"   ⚠️  Expected products but got {products_found}")
                else:
                    if response_len > 0:
                        print(f"   ✅ SUCCESS - Got response as expected")
                        success_count += 1
                    else:
                        print(f"   ❌ No response received")
                        
            except Exception as e:
                print(f"   ❌ ERROR: {e}")
        
        print(f"\n" + "=" * 50)
        print(f"🎯 VERIFICATION COMPLETE")
        print(f"✅ Success Rate: {success_count}/{total_tests} ({100*success_count//total_tests}%)")
        
        if success_count == total_tests:
            print("🎉 ALL TESTS PASSED - System Ready for Production!")
        elif success_count >= total_tests * 0.8:
            print("🟡 MOSTLY WORKING - Minor issues detected")
        else:
            print("🔴 ISSUES DETECTED - Need further debugging")
            
    except Exception as e:
        print(f"❌ System verification failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify_complete_system())
