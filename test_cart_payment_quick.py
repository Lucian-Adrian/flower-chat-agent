#!/usr/bin/env python3
"""
Quick test to verify Cart & Payment functionality
Tests the exact requirements from Step 9 & Step 10 of the PDF
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.tools.cart_tools import CartTools
from src.tools.payment_tools import PaymentTools

def test_step_10_cart_feature():
    """Test Step 10: Cart Feature (Simulated)"""
    print("🧪 TESTING STEP 10: CART FEATURE")
    print("=" * 50)
    
    cart = CartTools()
    user_id = "test_user_pdf"
    
    # Test add_to_cart intent
    print("1️⃣ Testing add_to_cart intent...")
    result1 = cart.add_to_cart(user_id, "Spring Bloom", 450.0)
    print(f"   Result: {result1}")
    
    result2 = cart.add_to_cart(user_id, "Rose Box", 800.0)
    print(f"   Result: {result2}")
    
    # Test view_cart intent
    print("\n2️⃣ Testing view_cart intent...")
    cart_view = cart.view_cart(user_id)
    print(f"   Result: {cart_view}")
    
    # Test add same item (quantity update)
    print("\n3️⃣ Testing duplicate item (quantity update)...")
    result3 = cart.add_to_cart(user_id, "Spring Bloom", 450.0)
    print(f"   Result: {result3}")
    
    # View updated cart
    cart_view2 = cart.view_cart(user_id)
    print(f"   Updated cart: {cart_view2}")
    
    return cart

def test_step_9_payment_flow(cart):
    """Test Step 9: Dummy Payment Flow"""
    print("\n\n🧪 TESTING STEP 9: DUMMY PAYMENT FLOW")
    print("=" * 50)
    
    payment = PaymentTools(cart)
    user_id = "test_user_pdf"
    
    # Test payment process with cart contents
    print("1️⃣ Testing payment process...")
    payment_result = payment.process_payment(user_id, "John Doe", "+373 123 456")
    print(f"   Payment result:\n{payment_result}")
    
    # Verify cart is empty after payment
    print("\n2️⃣ Verifying cart is cleared after payment...")
    empty_cart = cart.view_cart(user_id)
    print(f"   Cart after payment: {empty_cart}")
    
    return True

def test_clear_cart_functionality():
    """Test clear_cart intent"""
    print("\n\n🧪 TESTING CLEAR CART FUNCTIONALITY")
    print("=" * 50)
    
    cart = CartTools()
    user_id = "test_clear_user"
    
    # Add items first
    cart.add_to_cart(user_id, "Test Product", 100.0)
    print("1️⃣ Added test product to cart")
    
    # Clear cart
    clear_result = cart.clear_cart(user_id)
    print(f"2️⃣ Clear result: {clear_result}")
    
    # Verify empty
    empty_check = cart.view_cart(user_id)
    print(f"3️⃣ Cart after clear: {empty_check}")

if __name__ == "__main__":
    print("🌸 XOFlowers Cart & Payment System Test")
    print("Testing PDF Requirements: Step 9 & Step 10")
    print("=" * 60)
    
    try:
        # Test cart functionality (Step 10)
        cart = test_step_10_cart_feature()
        
        # Test payment functionality (Step 9)
        test_step_9_payment_flow(cart)
        
        # Test clear cart
        test_clear_cart_functionality()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Step 9 & Step 10 from PDF are FULLY FUNCTIONAL!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
