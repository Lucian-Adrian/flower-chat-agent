#!/usr/bin/env python3
"""
Quick AI Engine Test for XOFlowers
Tests the core AI functionality end-to-end
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append('.')

async def test_ai_engine():
    """Test the AI engine with a realistic query"""
    try:
        print("🤖 Testing XOFlowers AI Engine...")
        
        # Import AI engine
        from src.intelligence.ai_engine import process_message_ai
        
        # Test query in Romanian
        test_message = "Salut! Caut buchete de trandafiri roșii pentru Valentine's Day. Care e prețul?"
        test_user_id = "test_user_123"
        
        print(f"📝 Test Query: {test_message}")
        print(f"👤 Test User: {test_user_id}")
        print("⏳ Processing...")
        
        # Process the message
        result = await process_message_ai(
            user_message=test_message,
            user_id=test_user_id
        )
        
        # Display results
        print("\n" + "="*60)
        print("🎉 AI ENGINE TEST RESULTS")
        print("="*60)
        print(f"✅ Success: {result.get('success', False)}")
        print(f"🔧 Service Used: {result.get('service_used', 'unknown')}")
        print(f"🎯 Intent Detected: {result.get('intent', 'unknown')}")
        print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"🛍️  Products Found: {len(result.get('products', []))}")
        
        print(f"\n💬 AI Response:")
        print("-" * 40)
        response = result.get('response', 'No response received')
        print(response[:300] + "..." if len(response) > 300 else response)
        print("-" * 40)
        
        if result.get('success'):
            print("\n🎊 AI ENGINE IS WORKING PERFECTLY!")
            return True
        else:
            print("\n⚠️  AI ENGINE HAD ISSUES")
            return False
            
    except Exception as e:
        print(f"\n❌ AI ENGINE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_ai_engine())
    
    if success:
        print("\n🚀 READY TO LAUNCH TELEGRAM BOT!")
        print("The AI engine is working correctly.")
    else:
        print("\n🔧 SYSTEM NEEDS ATTENTION")
        print("Please check the AI engine configuration.")
    
    print(f"\nTest completed.")
