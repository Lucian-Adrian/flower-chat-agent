"""
Intent Classification for XOFlowers Conversational AI
Modular AI-only intent classification with comprehensive logging
Each function has one responsibility and is testable
"""

import json
import time
import logging
from typing import Dict, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Import system definitions with correct path
try:
    from src.helpers.system_definitions import INTENT_TYPES, AI_PROMPTS, EXPECTED_JSON_FORMATS
    HAS_DEFINITIONS = True
except ImportError:
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'helpers'))
        from system_definitions import INTENT_TYPES, AI_PROMPTS, EXPECTED_JSON_FORMATS
        HAS_DEFINITIONS = True
    except ImportError:
        # Fallback with basic intent types
        INTENT_TYPES = {
            'product_search': {'keywords': ['flori', 'buchete', 'trandafiri']},
            'price_inquiry': {'keywords': ['pret', 'cost', 'mdl', 'ieftin']},
            'business_info': {'keywords': ['program', 'contact', 'adresa']},
            'greeting': {'keywords': ['salut', 'buna', 'hello']},
            'farewell': {'keywords': ['pa', 'bye', 'multumesc']}
        }
        AI_PROMPTS = {}
        EXPECTED_JSON_FORMATS = {}
        HAS_DEFINITIONS = False

# Import LLM client and debug manager
try:
    from src.helpers.llm_client import call_llm
    HAS_LLM = True
except ImportError:
    try:
        from llm_client import call_llm
        HAS_LLM = True
    except ImportError:
        HAS_LLM = False
        def call_llm(*args, **kwargs):
            return {"response": "AI not available", "success": False}

try:
    from src.helpers.debug_manager import get_debug_manager
    HAS_DEBUG = True
except ImportError:
    try:
        from debug_manager import get_debug_manager
        HAS_DEBUG = True
    except ImportError:
        HAS_DEBUG = False
        def get_debug_manager():
            return None


def classify_intent(message_text: str, user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main intent classification function using AI only
    
    Args:
        message_text: User's message to classify
        user_context: Optional user context for better classification
        
    Returns:
        Dict with intent classification result
    """
    start_time = time.time()
    debug_manager = get_debug_manager() if HAS_DEBUG else None
    
    if debug_manager:
        debug_manager.log_info(
            f"Starting intent classification for message: '{message_text[:50]}...'",
            "IntentClassifier", "classify_intent_start"
        )
    
    try:
        # Step 1: Build classification prompt
        prompt = build_classification_prompt(message_text, user_context)
        
        if debug_manager:
            debug_manager.log_operation(
                component="IntentClassifier",
                operation="build_prompt",
                input_data={
                    "message_length": len(message_text),
                    "has_context": bool(user_context),
                    "prompt_length": len(prompt)
                },
                success=True
            )
        
        # Step 2: Call LLM
        if not HAS_LLM:
            return _create_fallback_intent(message_text, "LLM client not available")
        
        llm_start_time = time.time()
        llm_result = call_llm(prompt, max_tokens=500)
        llm_time = time.time() - llm_start_time
        
        if not llm_result['success']:
            return _create_fallback_intent(message_text, llm_result.get('error', 'LLM call failed'))
        
        if debug_manager:
            debug_manager.log_operation(
                component="IntentClassifier",
                operation="llm_call",
                input_data={"prompt_length": len(prompt)},
                output_data={
                    "response_length": len(llm_result['response']),
                    "service_used": llm_result['service_used']
                },
                execution_time=llm_time,
                success=True
            )
        
        # Step 3: Parse LLM response
        intent_result = parse_intent_response(llm_result['response'])
        
        # Step 4: Validate confidence score
        validated_result = validate_confidence_score(intent_result)
        
        total_time = time.time() - start_time
        validated_result['execution_time'] = total_time
        
        # Final debug logging
        if debug_manager:
            debug_manager.log_operation(
                component="IntentClassifier",
                operation="classify_intent",
                input_data={
                    "message": message_text,
                    "has_context": bool(user_context)
                },
                output_data={
                    "intent_type": validated_result['intent_type'],
                    "confidence": validated_result['confidence'],
                    "requires_search": validated_result['requires_search'],
                    "entities_count": len(validated_result.get('entities', {}))
                },
                execution_time=total_time,
                success=True,
                metadata={
                    "llm_time": llm_time,
                    "service_used": llm_result['service_used']
                }
            )
        
        logger.info(f"🧠 Intent classified: {validated_result['intent_type']} (confidence: {validated_result['confidence']:.2f})")
        return validated_result
        
    except Exception as e:
        total_time = time.time() - start_time
        error_msg = f"Intent classification error: {e}"
        logger.error(f"❌ {error_msg}")
        
        if debug_manager:
            debug_manager.log_operation(
                component="IntentClassifier",
                operation="classify_intent",
                input_data={"message": message_text},
                execution_time=total_time,
                success=False,
                error_message=error_msg
            )
        
        return _create_fallback_intent(message_text, error_msg)


def build_classification_prompt(message_text: str, user_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Build classification prompt using system definitions
    
    Args:
        message_text: User's message
        user_context: Optional user context
        
    Returns:
        Formatted prompt string
    """
    if not HAS_DEFINITIONS:
        return f"Classify this message: {message_text}"
    
    # Get intent types and format them
    intent_types = '|'.join(INTENT_TYPES.keys())
    
    # Get base prompt template
    base_prompt = AI_PROMPTS.get('intent_classification_prompt', '')
    
    # Format prompt with actual values
    formatted_prompt = base_prompt.format(
        intent_types=intent_types,
        colors=list(INTENT_TYPES.get('product_search', {}).get('entities', {}).get('colors', [])),
        occasions=list(INTENT_TYPES.get('product_search', {}).get('entities', {}).get('occasions', []))
    )
    
    # Add context if available
    context_info = ""
    if user_context:
        context_info = f"\nCONTEXT UTILIZATOR:\n{json.dumps(user_context, ensure_ascii=False, indent=2)}"
    
    # Build final prompt
    final_prompt = f"""
{formatted_prompt}

{context_info}

MESAJUL DE ANALIZAT:
"{message_text}"

Răspunde doar cu JSON-ul cerut:
    """.strip()
    
    return final_prompt


def parse_intent_response(llm_response: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured intent result
    
    Args:
        llm_response: Raw response from LLM
        
    Returns:
        Parsed intent result dict
    """
    try:
        # Try to parse JSON directly
        parsed = json.loads(llm_response)
        
        # Validate required fields
        required_fields = ['intent_type', 'confidence']
        for field in required_fields:
            if field not in parsed:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure proper types
        result = {
            'intent_type': str(parsed.get('intent_type', 'question')),
            'confidence': float(parsed.get('confidence', 0.5)),
            'entities': dict(parsed.get('entities', {})),
            'requires_search': bool(parsed.get('requires_search', False)),
            'reasoning': str(parsed.get('reasoning', 'AI classification')),
            'sentiment': str(parsed.get('sentiment', 'neutral'))
        }
        
        return result
        
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        logger.warning(f"⚠️ Failed to parse LLM response: {e}")
        logger.warning(f"Raw response: {llm_response}")
        
        # Try to extract intent from response text
        return _extract_intent_from_text(llm_response)


def _extract_intent_from_text(response_text: str) -> Dict[str, Any]:
    """
    Fallback: try to extract intent from unstructured response
    
    Args:
        response_text: Raw LLM response
        
    Returns:
        Best-guess intent result
    """
    response_lower = response_text.lower()
    
    # Simple keyword matching for fallback
    if any(word in response_lower for word in ['search', 'find', 'caut', 'vreau']):
        intent_type = 'product_search'
        requires_search = True
    elif any(word in response_lower for word in ['hello', 'hi', 'salut', 'bună']):
        intent_type = 'greeting'
        requires_search = False
    elif any(word in response_lower for word in ['question', 'întrebare', 'ce', 'cum']):
        intent_type = 'question'
        requires_search = False
    else:
        intent_type = 'question'
        requires_search = False
    
    return {
        'intent_type': intent_type,
        'confidence': 0.3,  # Low confidence for fallback
        'entities': {},
        'requires_search': requires_search,
        'reasoning': 'Fallback text extraction due to JSON parsing failure',
        'sentiment': 'neutral'
    }


def validate_confidence_score(intent_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and adjust confidence score
    
    Args:
        intent_result: Intent result to validate
        
    Returns:
        Validated intent result
    """
    confidence = intent_result.get('confidence', 0.5)
    
    # Ensure confidence is within valid range
    confidence = max(0.0, min(1.0, confidence))
    
    # Adjust confidence based on intent type validation
    intent_type = intent_result.get('intent_type', 'question')
    
    if HAS_DEFINITIONS and intent_type not in INTENT_TYPES:
        # Unknown intent type, reduce confidence and default to 'question'
        confidence *= 0.5
        intent_type = 'question'
        logger.warning(f"⚠️ Unknown intent type, defaulting to 'question' with reduced confidence")
    
    # Update result
    intent_result['confidence'] = confidence
    intent_result['intent_type'] = intent_type
    
    return intent_result


def _create_fallback_intent(message_text: str, error_reason: str) -> Dict[str, Any]:
    """
    Create fallback intent when AI classification fails
    
    Args:
        message_text: Original message
        error_reason: Reason for fallback
        
    Returns:
        Fallback intent result
    """
    message_lower = message_text.lower()
    
    # Simple keyword-based fallback
    if any(word in message_lower for word in ['caut', 'vreau', 'doresc', 'buchet', 'flori']):
        intent_type = 'product_search'
        requires_search = True
    elif any(word in message_lower for word in ['salut', 'bună', 'hello', 'hi']):
        intent_type = 'greeting'
        requires_search = False
    else:
        intent_type = 'question'
        requires_search = False
    
    logger.warning(f"⚠️ Using fallback intent classification: {intent_type} (reason: {error_reason})")
    
    return {
        'intent_type': intent_type,
        'confidence': 0.4,  # Low confidence for fallback
        'entities': {},
        'requires_search': requires_search,
        'reasoning': f'Fallback classification - {error_reason}',
        'sentiment': 'neutral',
        'execution_time': 0.0,
        'fallback_used': True,
        'fallback_reason': error_reason
    }