"""
Action Handler for XOFlowers Conversational AI
This module is the entry point for handling user actions and messages,
connecting them to the new conversational AI system.
"""

import logging
from typing import Dict, Any

# Import modular components
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'helpers'))
    from system_definitions import ACTION_MAPPINGS, BUSINESS_INFO
    HAS_DEFINITIONS = True
except ImportError:
    HAS_DEFINITIONS = False
    ACTION_MAPPINGS = {}
    BUSINESS_INFO = {}

try:
    from llm_client import call_llm
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def route_action(intent_result: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Routes action based on intent using modular approach
    
    Args:
        intent_result: Result from intent classification
        user_context: User context information
        
    Returns:
        Dict with action result
    """
    intent_type = intent_result.get('intent_type', 'question')
    
    if not HAS_DEFINITIONS:
        logger.warning("⚠️ No action mappings available, using default handler")
        return _handle_default_action(intent_result, user_context)
    
    # Map intent to handler
    handler_name = ACTION_MAPPINGS.get(intent_type, 'DefaultHandler')
    
    logger.info(f"🎯 Routing intent '{intent_type}' to handler '{handler_name}'")
    
    # Route to specific handler
    if intent_type == 'greeting':
        return _handle_greeting(intent_result, user_context)
    elif intent_type == 'product_search':
        return _handle_product_search(intent_result, user_context)
    elif intent_type == 'question':
        return _handle_question(intent_result, user_context)
    elif intent_type == 'compliment':
        return _handle_compliment(intent_result, user_context)
    elif intent_type == 'complaint':
        return _handle_complaint(intent_result, user_context)
    else:
        return _handle_default_action(intent_result, user_context)


def _handle_greeting(intent_result: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle greeting intent"""
    business_name = BUSINESS_INFO.get('name', 'XOFlowers') if HAS_DEFINITIONS else 'XOFlowers'
    
    response = f"🌸 Bună ziua! Bine ați venit la {business_name}! Cu ce vă pot ajuta astăzi?"
    
    return {
        "action_type": "greeting_response",
        "handler_used": "GreetingHandler",
        "execution_data": {"response_text": response},
        "next_step": "await_user_request"
    }


def _handle_product_search(intent_result: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle product search intent"""
    entities = intent_result.get('entities', {})
    
    # Extract search parameters from entities
    colors = entities.get('colors', [])
    budget_max = entities.get('budget_max')
    occasions = entities.get('occasions', [])
    
    # Build search context
    search_context = {
        "colors": colors,
        "budget_max": budget_max,
        "occasions": occasions,
        "requires_search": True
    }
    
    response = "🌸 Înțeleg că căutați flori! Permiteți-mi să vă ajut să găsesc ceva frumos pentru dumneavoastră."
    
    return {
        "action_type": "product_search",
        "handler_used": "ProductSearchHandler", 
        "execution_data": {
            "response_text": response,
            "search_context": search_context
        },
        "next_step": "execute_product_search"
    }


def _handle_question(intent_result: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle general question intent"""
    business_info = BUSINESS_INFO if HAS_DEFINITIONS else {}
    
    response = f"🌸 Cu plăcere vă răspund la întrebare! Suntem {business_info.get('name', 'XOFlowers')} din {business_info.get('location', 'Chișinău')} și oferim cele mai frumoase flori."
    
    return {
        "action_type": "question_response",
        "handler_used": "QuestionHandler",
        "execution_data": {"response_text": response},
        "next_step": "provide_business_info"
    }


def _handle_compliment(intent_result: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle compliment intent"""
    response = "🌸 Vă mulțumesc pentru cuvintele frumoase! Îmi face plăcere să vă ajut să găsiți florile perfecte. Mai aveți nevoie de ceva?"
    
    return {
        "action_type": "compliment_response",
        "handler_used": "ComplimentHandler",
        "execution_data": {"response_text": response},
        "next_step": "continue_conversation"
    }


def _handle_complaint(intent_result: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle complaint intent"""
    response = "🌸 Îmi pare foarte rău pentru inconvenient. Vă rog să îmi spuneți mai multe detalii pentru a vă putea ajuta să rezolvăm situația."
    
    return {
        "action_type": "complaint_response", 
        "handler_used": "ComplaintHandler",
        "execution_data": {"response_text": response},
        "next_step": "gather_complaint_details"
    }


def _handle_default_action(intent_result: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """Handle unknown or default actions"""
    if HAS_LLM:
        # Use LLM for complex responses
        original_message = intent_result.get('original_message', '')
        llm_result = call_llm(f"Generate a helpful response for XOFlowers customer who said: {original_message}")
        
        if llm_result['success']:
            response = llm_result['response']
        else:
            response = "🌸 Îmi pare rău, am întâmpinat o problemă tehnică. Cu ce vă pot ajuta?"
    else:
        response = "🌸 Înțeleg! Sunt aici să vă ajut cu orice aveți nevoie legat de flori. Cu ce vă pot ajuta?"
    
    return {
        "action_type": "default_response",
        "handler_used": "DefaultHandler",
        "execution_data": {"response_text": response},
        "next_step": "continue_conversation"
    }


# Legacy function for backward compatibility
async def handle_action(action: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Legacy function for backward compatibility
    Redirects to modular approach
    """
    logger.warning("⚠️ Using legacy handle_action - consider using route_action instead")
    
    # Convert legacy format to modular format
    intent_result = {
        "intent_type": "question",
        "confidence": 0.5,
        "entities": {},
        "original_message": context.get("message_text", "")
    }
    
    user_context = {
        "user_id": context.get("user_id"),
        "platform": "legacy"
    }
    
    action_result = route_action(intent_result, user_context)
    
    return {
        "response": action_result["execution_data"]["response_text"]
    }
