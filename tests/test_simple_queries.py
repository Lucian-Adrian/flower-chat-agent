#!/usr/bin/env python3
"""
Simple Query Test Suite for XOFlowers AI Agent
Tests understanding of simple, natural language requests
"""

import asyncio
import sys
import os

# Add path to src modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.intelligence.conversation_manager import get_conversation_manager

def test_simple_queries():
    """Test if bot understands simple, natural queries"""
    
    print("🧪 Testing Simple Query Understanding...")
    print("=" * 60)
    
    cm = get_conversation_manager()
    
    # Test cases: (input, should_find_products, description)
    test_cases = [
        # Very simple requests
        ("розы", True, "Single word Russian - roses"),
        ("roses", True, "Single word English - roses"),
        ("trandafiri", True, "Single word Romanian - roses"),
        ("цветы", True, "Single word Russian - flowers"),
        ("flowers", True, "Single word English - flowers"),
        ("flori", True, "Single word Romanian - flowers"),
        
        # Simple with colors
        ("красные розы", True, "Russian: red roses"),
        ("red roses", True, "English: red roses"),
        ("trandafiri roșii", True, "Romanian: red roses"),
        
        # Simple with recipients
        ("розы для девушки", True, "Russian: roses for girlfriend"),
        ("roses for girlfriend", True, "English: roses for girlfriend"),
        ("trandafiri pentru soție", True, "Romanian: roses for wife"),
        
        # Natural expressions
        ("дай мне розы", True, "Russian: give me roses"),
        ("i need some roses", True, "English: I need roses"),
        ("vreau trandafiri", True, "Romanian: I want roses"),
        
        # From user examples
        ("i need some roses for girlfriend", True, "English: complex request"),
        ("Цветок роза", True, "Russian: flower rose"),
        
        # Mixed language (should still work)
        ("roses для девушки", True, "Mixed: roses for girlfriend"),
        ("розы for girlfriend", True, "Mixed: roses for girlfriend"),
        
        # Non-product queries (should not trigger search)
        ("привет", False, "Russian greeting"),
        ("hello", False, "English greeting"),
        ("что это", False, "Russian: what is this"),
        ("как дела", False, "Russian: how are you"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (user_input, should_find_products, description) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {description}")
        print(f"   Input: '{user_input}'")
        print(f"   Should find products: {should_find_products}")
        
        try:
            # Get response from conversation manager
            response = cm.process_message_sync(f"test_simple_{i}", user_input)
            
            # Check if response indicates product search
            has_products = any(phrase in response.lower() for phrase in [
                'găsit', 'найден', 'found', 'опций', 'options', 'результат', 
                'preț', 'цена', 'price', 'mdl', 'лей', 'bouquet', 'букет'
            ])
            
            print(f"   Response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            print(f"   Has products: {has_products}")
            
            if should_find_products and has_products:
                print("   ✅ PASS - Found products as expected")
                passed += 1
            elif not should_find_products and not has_products:
                print("   ✅ PASS - No products as expected")
                passed += 1
            elif should_find_products and not has_products:
                print("   ❌ FAIL - Should have found products but didn't")
                failed += 1
            else:
                print("   ❌ FAIL - Found products when shouldn't have")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR - Exception occurred: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Simple Query Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("🎉 All simple query tests passed!")
        return True
    else:
        print("⚠️  Some simple query tests failed - check understanding logic")
        return False

if __name__ == "__main__":
    print("🧪 XOFlowers Simple Query Test Suite")
    print("Testing natural language understanding for simple requests...")
    print()
    
    # Run simple query tests
    success = test_simple_queries()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    
    if success:
        print("🎉 ALL TESTS PASSED - Simple query understanding working correctly!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Review understanding prompts and logic")
        sys.exit(1)
