# test_cart_payment_flow.py

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from tools.cart_tools import CartTools
from tools.payment_tools import PaymentTools

async def test_cart_flow():
    """Test complete cart and payment functionality"""
    print("🧪 Starting Cart & Payment Flow Tests...")
    
    # Initialize tools
    cart_tools = CartTools()
    payment_tools = PaymentTools(cart_tools)
    
    test_user_id = "test_user_123"
    
    # Test 1: Add products to cart
    print("\n1. Testing add_to_cart...")
    result1 = cart_tools.add_to_cart(test_user_id, "Buchet de trandafiri roșii", 150.0, "https://xoflowers.md/trandafiri")
    print(f"Result: {result1}")
    
    result2 = cart_tools.add_to_cart(test_user_id, "Cutie cu flori mixte", 200.0, "https://xoflowers.md/mixte")
    print(f"Result: {result2}")
    
    # Test 2: Add same product again (quantity increment)
    print("\n2. Testing quantity increment...")
    result3 = cart_tools.add_to_cart(test_user_id, "Buchet de trandafiri roșii", 150.0)
    print(f"Result: {result3}")
    
    # Test 3: View cart
    print("\n3. Testing view_cart...")
    cart_view = cart_tools.view_cart(test_user_id)
    print(f"Cart contents:\n{cart_view}")
    
    # Test 4: Remove product
    print("\n4. Testing remove_from_cart...")
    remove_result = cart_tools.remove_from_cart(test_user_id, "Cutie cu flori mixte")
    print(f"Remove result: {remove_result}")
    
    # Test 5: View cart after removal
    print("\n5. Testing cart after removal...")
    cart_view2 = cart_tools.view_cart(test_user_id)
    print(f"Cart after removal:\n{cart_view2}")
    
    # Test 6: Process payment
    print("\n6. Testing payment processing...")
    payment_result = payment_tools.process_payment(test_user_id, "Ion Popescu", "+373 69 123 456")
    print(f"Payment result:\n{payment_result}")
    
    # Test 7: View cart after payment (should be empty)
    print("\n7. Testing cart after payment...")
    empty_cart = cart_tools.view_cart(test_user_id)
    print(f"Cart after payment:\n{empty_cart}")
    
    # Test 8: Try payment with empty cart
    print("\n8. Testing payment with empty cart...")
    empty_payment = payment_tools.process_payment(test_user_id)
    print(f"Empty cart payment: {empty_payment}")
    
    # Test 9: Clear cart functionality
    print("\n9. Testing clear cart...")
    cart_tools.add_to_cart(test_user_id, "Test product", 100.0)
    clear_result = cart_tools.clear_cart(test_user_id)
    print(f"Clear result: {clear_result}")
    
    # Test 10: Verify data persistence
    print("\n10. Testing data persistence...")
    if os.path.exists("data/user_carts.json"):
        with open("data/user_carts.json", 'r', encoding='utf-8') as f:
            carts_data = json.load(f)
            print(f"Carts file exists with data: {len(carts_data)} users")
    
    if os.path.exists("data/orders.json"):
        with open("data/orders.json", 'r', encoding='utf-8') as f:
            orders_data = json.load(f)
            print(f"Orders file exists with data: {len(orders_data)} orders")
            if orders_data:
                latest_order = list(orders_data.values())[-1]
                print(f"Latest order total: {latest_order['total_amount']} MDL")
    
    print("\n✅ All tests completed successfully!")

def test_edge_cases():
    """Test edge cases and error scenarios"""
    print("\n🔍 Testing Edge Cases...")
    
    cart_tools = CartTools()
    payment_tools = PaymentTools(cart_tools)
    
    # Test non-existent user cart
    empty_user_cart = cart_tools.view_cart("non_existent_user")
    print(f"Non-existent user cart: {empty_user_cart}")
    
    # Test removing non-existent product
    remove_fake = cart_tools.remove_from_cart("test_user", "fake_product")
    print(f"Remove fake product: {remove_fake}")
    
    # Test order status for non-existent order
    fake_status = payment_tools.get_order_status("FAKE_ORDER_123")
    print(f"Fake order status: {fake_status}")

if __name__ == "__main__":
    # Run main test flow
    asyncio.run(test_cart_flow())
    
    # Run edge case tests
    test_edge_cases()
    
    print("\n🎉 Testing completed! Check data/ folder for generated files.")
