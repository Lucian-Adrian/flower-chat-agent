#!/usr/bin/env python3
"""
Integration test for logging functionality
Tests that logging works correctly across all components
"""

import os
import sys
import logging
from io import StringIO

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from intelligence.action_handler import ActionHandler
from intelligence.intent_classifier import IntentClassifier


def test_logging_integration():
    """Test that logging works correctly for intent classification and action handling"""
    print("🌸 XOFlowers Logging Integration Test")
    print("=" * 50)
    
    # Capture logs
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.INFO)
    
    # Add handler to loggers
    action_logger = logging.getLogger('intelligence.action_handler')
    intent_logger = logging.getLogger('intelligence.intent_classifier')
    
    action_logger.addHandler(handler)
    intent_logger.addHandler(handler)
    
    # Initialize components
    action_handler = ActionHandler()
    intent_classifier = IntentClassifier()
    
    # Test messages
    test_messages = [
        "Salut! Vreau trandafiri roși",
        "Caut flori pentru aniversare",
        "Ce prețuri aveți?",
        "Programul de lucru?",
        "Mulțumesc, la revedere!"
    ]
    
    user_id = "test_user_123"
    
    print(f"\n🧪 Testing {len(test_messages)} messages...\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"--- Test {i} ---")
        print(f"Message: '{message}'")
        
        # Clear previous logs
        log_capture.truncate(0)
        log_capture.seek(0)
        
        # Test intent classification
        intent, confidence = intent_classifier.classify_intent(message, user_id)
        print(f"Intent: {intent} (confidence: {confidence:.2f})")
        
        # Test action handler
        response, detected_intent, detected_confidence = action_handler.handle_message(message, user_id)
        print(f"Response length: {len(response)} chars")
        print(f"Detected intent: {detected_intent} (confidence: {detected_confidence:.2f})")
        
        # Check logs
        log_content = log_capture.getvalue()
        if log_content:
            print("✅ Logging working correctly")
        else:
            print("❌ No logs captured")
        
        print()
    
    # Cleanup
    action_logger.removeHandler(handler)
    intent_logger.removeHandler(handler)
    
    print("✅ Logging integration test completed!")


if __name__ == "__main__":
    test_logging_integration()
