#!/usr/bin/env python3
"""
Test budget filtering functionality
"""

import sys
import os
sys.path.insert(0, 'src')

def test_budget_filtering():
    """Test budget extraction and filtering"""
    print("💰 Testing Budget Filtering...")
    
    try:
        from intelligence.conversation_manager import get_conversation_manager
        cm = get_conversation_manager()
        
        # Test cases with different budget formats
        test_cases = [
            ("нужны цветы для мамы до 1000 лей", 1000),
            ("хочу букет под 500 лей", 500),
            ("flowers under 800 lei", 800),
            ("bouquet sub 300 MDL", 300),
            ("trandafiri maximum 1200", 1200),
            ("roses max 600", 600),
            ("flori не более 900 лей", 900),
            ("buchete nu mai mult de 750", 750),
        ]
        
        print("\n🧪 Testing budget extraction...")
        for message, expected_budget in test_cases:
            extracted = cm._extract_budget(message)
            status = "✅" if extracted == expected_budget else "❌"
            print(f"   {status} '{message}' → {extracted} (expected {expected_budget})")
        
        print("\n🧪 Testing real search with budget...")
        test_searches = [
            "цветы для мамы до 500 лей",
            "букет под 1000 лей", 
            "trandafiri до 800",
        ]
        
        for search_query in test_searches:
            print(f"\n🔍 Testing: '{search_query}'")
            response = cm.process_message_sync("test_user_budget", search_query)
            
            # Check if response mentions budget
            if "bugetul" in response or "budget" in response or "MDL" in response:
                print("   ✅ Budget mentioned in response")
            else:
                print("   ⚠️ Budget not mentioned in response")
                
            # Extract prices from response for verification
            import re
            prices = re.findall(r'(\d+\.?\d*)\s*MDL', response)
            if prices:
                max_price = max(float(p) for p in prices)
                budget = cm._extract_budget(search_query)
                if budget and max_price <= budget:
                    print(f"   ✅ All prices ({max_price} max) within budget ({budget})")
                else:
                    print(f"   ❌ Price {max_price} exceeds budget {budget}")
            
        print("\n🎉 Budget filtering test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in budget test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_budget_filtering()
