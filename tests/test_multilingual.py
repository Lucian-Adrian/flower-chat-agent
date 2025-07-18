#!/usr/bin/env python3
"""
Multilingual Test Suite for XOFlowers AI Agent
Tests language detection and response language matching
"""

import asyncio
import sys
import os

# Add path to src modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.intelligence.conversation_manager import get_conversation_manager

def detect_response_language(response):
    """Detect the language of the response"""
    # Romanian indicators
    ro_indicators = ['bună', 'ziua', 'flori', 'buchete', 'vreau', 'aveți', 'pentru', 'mulțumesc']
    # Russian indicators  
    ru_indicators = ['здравствуйте', 'цветы', 'букеты', 'хочу', 'есть', 'для', 'спасибо', 'рублей', 'лей']
    # English indicators
    en_indicators = ['hello', 'flowers', 'bouquets', 'want', 'have', 'for', 'thank', 'you']
    
    response_lower = response.lower()
    
    ro_count = sum(1 for word in ro_indicators if word in response_lower)
    ru_count = sum(1 for word in ru_indicators if word in response_lower)  
    en_count = sum(1 for word in en_indicators if word in response_lower)
    
    if ro_count > ru_count and ro_count > en_count:
        return 'ro'
    elif ru_count > ro_count and ru_count > en_count:
        return 'ru'
    elif en_count > ro_count and en_count > ru_count:
        return 'en'
    else:
        return 'unknown'

def test_language_matching():
    """Test if bot responds in the same language as user input"""
    
    print("🌐 Testing Multilingual Response Matching...")
    print("=" * 60)
    
    cm = get_conversation_manager()
    
    # Test cases: (input, expected_language, description)
    test_cases = [
        # Romanian tests
        ("Salut!", "ro", "Romanian greeting"),
        ("Vreau un buchet frumos", "ro", "Romanian product request"),
        ("Caut flori până la 500 lei", "ro", "Romanian budget request"),
        
        # Russian tests  
        ("Привет!", "ru", "Russian greeting"),
        ("Хочу красивый букет", "ru", "Russian product request"),
        ("Нужны цветы до 1000 лей", "ru", "Russian budget request"),
        
        # English tests
        ("Hello!", "en", "English greeting"),
        ("I want a beautiful bouquet", "en", "English product request"),
        ("Need flowers under 500 lei", "en", "English budget request"),
        
        # Mixed language tests
        ("Flori до 800 лей", "mixed", "Mixed Romanian-Russian"),
        ("Buchete under 600", "mixed", "Mixed Romanian-English"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (user_input, expected_lang, description) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {description}")
        print(f"   Input: '{user_input}'")
        print(f"   Expected language: {expected_lang}")
        
        try:
            # Get response from conversation manager
            response = cm.process_message_sync(f"test_user_lang_{i}", user_input)
            
            # Detect response language
            detected_lang = detect_response_language(response)
            
            print(f"   Response: '{response[:100]}{'...' if len(response) > 100 else ''}'")
            print(f"   Detected language: {detected_lang}")
            
            # Check if languages match (or mixed is acceptable)
            if expected_lang == "mixed":
                if detected_lang in ["ro", "ru", "en"]:
                    print("   ✅ PASS - Mixed language handled appropriately")
                    passed += 1
                else:
                    print("   ❌ FAIL - Mixed language not handled properly")
                    failed += 1
            elif detected_lang == expected_lang:
                print("   ✅ PASS - Language matches")
                passed += 1
            else:
                print(f"   ❌ FAIL - Expected {expected_lang}, got {detected_lang}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR - Exception occurred: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success rate: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("🎉 All language tests passed!")
    else:
        print("⚠️  Some language tests failed - check AI prompts")
    
    return failed == 0

def test_budget_extraction_multilingual():
    """Test budget extraction in multiple languages"""
    
    print("\n💰 Testing Multilingual Budget Extraction...")
    print("=" * 60)
    
    cm = get_conversation_manager()
    
    # Test cases: (input, expected_budget, language)
    budget_tests = [
        # Romanian
        ("Vreau buchete sub 500 lei", 500, "ro"),
        ("Flori până la 1000 MDL", 1000, "ro"),
        ("Nu mai mult de 800 lei", 800, "ro"),
        
        # Russian
        ("Букеты до 1000 лей", 1000, "ru"),
        ("Цветы под 500 лей", 500, "ru"),
        ("Не более 600 лей", 600, "ru"),
        
        # English
        ("Bouquets under 500 lei", 500, "en"),
        ("Flowers up to 1000 MDL", 1000, "en"),
        ("No more than 800 lei", 800, "en"),
    ]
    
    passed = 0
    failed = 0
    
    for i, (user_input, expected_budget, lang) in enumerate(budget_tests, 1):
        print(f"\n{i}. Testing budget extraction ({lang})")
        print(f"   Input: '{user_input}'")
        print(f"   Expected budget: {expected_budget}")
        
        try:
            # Extract budget using conversation manager
            extracted_budget = cm._extract_budget(user_input)
            
            print(f"   Extracted budget: {extracted_budget}")
            
            if extracted_budget == expected_budget:
                print("   ✅ PASS - Budget extracted correctly")
                passed += 1
            else:
                print(f"   ❌ FAIL - Expected {expected_budget}, got {extracted_budget}")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ ERROR - Exception occurred: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Budget Extraction Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success rate: {passed/(passed+failed)*100:.1f}%")
    
    return failed == 0

if __name__ == "__main__":
    print("🧪 XOFlowers Multilingual Test Suite")
    print("Testing language detection and response matching...")
    print()
    
    # Run language matching tests
    lang_success = test_language_matching()
    
    # Run budget extraction tests
    budget_success = test_budget_extraction_multilingual()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    
    if lang_success and budget_success:
        print("🎉 ALL TESTS PASSED - Multilingual functionality working correctly!")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED - Review AI prompts and language detection")
        if not lang_success:
            print("   - Language response matching needs improvement")
        if not budget_success:
            print("   - Budget extraction patterns need updating")
        sys.exit(1)
