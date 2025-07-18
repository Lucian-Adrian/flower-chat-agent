"""
Security filters for XOFlowers Conversational AI
Modular security validation with comprehensive logging
Each function has one responsibility and is testable
"""

import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

# Setup logging
logger = logging.getLogger(__name__)

# Import system definitions and debug manager
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'helpers'))
    from system_definitions import SECURITY_RULES
    HAS_DEFINITIONS = True
except ImportError:
    HAS_DEFINITIONS = False
    SECURITY_RULES = {}

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'intelligence'))
    from debug_manager import get_debug_manager
    HAS_DEBUG = True
except ImportError:
    HAS_DEBUG = False

# Rate limiting storage (in production, use Redis)
_rate_limit_storage = defaultdict(list)


def validate_message_security(message_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main security validation function
    Validates message security using all available checks
    
    Args:
        message_data: Dict with user_id, message_text, timestamp, platform
        
    Returns:
        Dict with security validation result
    """
    start_time = time.time()
    debug_manager = get_debug_manager() if HAS_DEBUG else None
    
    if debug_manager:
        debug_manager.log_info(
            f"Starting security validation for user {message_data.get('user_id', 'unknown')}",
            "SecurityFilter", "validate_start"
        )
    
    checks_performed = []
    security_score = 1.0  # Start with perfect score
    block_reason = None
    
    try:
        # Check 1: Rate limiting
        rate_limit_result = is_rate_limited(message_data.get('user_id', ''))
        checks_performed.append('rate_limiting')
        
        if rate_limit_result['is_limited']:
            security_score = 0.0
            block_reason = f"Rate limit exceeded: {rate_limit_result['reason']}"
        
        # Check 2: Message length validation
        length_result = validate_message_length(message_data.get('message_text', ''))
        checks_performed.append('message_length')
        
        if not length_result['is_valid']:
            security_score = 0.0
            block_reason = f"Invalid message length: {length_result['reason']}"
        
        # Check 3: Offensive content detection
        if security_score > 0:  # Only check if not already blocked
            offensive_result = contains_offensive_content(message_data.get('message_text', ''))
            checks_performed.append('offensive_content')
            
            if offensive_result['contains_offensive']:
                security_score *= 0.3  # Reduce score significantly
                if security_score < 0.5:
                    block_reason = f"Offensive content detected: {offensive_result['reason']}"
        
        # Check 4: Jailbreak attempt detection
        if security_score > 0:  # Only check if not already blocked
            jailbreak_result = is_jailbreak_attempt(message_data.get('message_text', ''))
            checks_performed.append('jailbreak_detection')
            
            if jailbreak_result['is_jailbreak']:
                security_score = 0.0
                block_reason = f"Jailbreak attempt detected: {jailbreak_result['reason']}"
        
        # Final decision
        is_allowed = security_score >= 0.5 and block_reason is None
        
        execution_time = time.time() - start_time
        
        result = {
            "is_allowed": is_allowed,
            "block_reason": block_reason,
            "security_score": security_score,
            "checks_performed": checks_performed,
            "execution_time": execution_time
        }
        
        # Debug logging
        if debug_manager:
            debug_manager.log_operation(
                component="SecurityFilter",
                operation="validate_message_security",
                input_data={
                    "user_id": message_data.get('user_id', 'unknown'),
                    "message_length": len(message_data.get('message_text', '')),
                    "platform": message_data.get('platform', 'unknown')
                },
                output_data={
                    "is_allowed": is_allowed,
                    "security_score": security_score,
                    "checks_count": len(checks_performed),
                    "block_reason": block_reason
                },
                execution_time=execution_time,
                success=True,
                metadata={"checks_performed": checks_performed}
            )
        
        logger.info(f"🔒 Security validation: {'ALLOWED' if is_allowed else 'BLOCKED'} (score: {security_score:.2f})")
        return result
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = f"Security validation error: {e}"
        logger.error(f"❌ {error_msg}")
        
        if debug_manager:
            debug_manager.log_operation(
                component="SecurityFilter",
                operation="validate_message_security",
                input_data={"user_id": message_data.get('user_id', 'unknown')},
                execution_time=execution_time,
                success=False,
                error_message=error_msg
            )
        
        # Fail secure - block on error
        return {
            "is_allowed": False,
            "block_reason": "Security validation error",
            "security_score": 0.0,
            "checks_performed": checks_performed,
            "execution_time": execution_time,
            "error": error_msg
        }


def is_rate_limited(user_id: str) -> Dict[str, Any]:
    """
    Check if user exceeded rate limits
    
    Args:
        user_id: User identifier
        
    Returns:
        Dict with rate limit check result
    """
    if not HAS_DEFINITIONS:
        return {"is_limited": False, "reason": "No rate limit rules configured"}
    
    current_time = datetime.now()
    user_requests = _rate_limit_storage[user_id]
    
    # Clean old requests (older than 1 hour)
    hour_ago = current_time - timedelta(hours=1)
    user_requests[:] = [req_time for req_time in user_requests if req_time > hour_ago]
    
    # Check per-minute limit
    minute_ago = current_time - timedelta(minutes=1)
    requests_last_minute = sum(1 for req_time in user_requests if req_time > minute_ago)
    
    if requests_last_minute >= SECURITY_RULES.get('rate_limit_per_minute', 10):
        return {
            "is_limited": True,
            "reason": f"Exceeded {SECURITY_RULES.get('rate_limit_per_minute', 10)} requests per minute",
            "requests_last_minute": requests_last_minute
        }
    
    # Check per-hour limit
    requests_last_hour = len(user_requests)
    if requests_last_hour >= SECURITY_RULES.get('rate_limit_per_hour', 100):
        return {
            "is_limited": True,
            "reason": f"Exceeded {SECURITY_RULES.get('rate_limit_per_hour', 100)} requests per hour",
            "requests_last_hour": requests_last_hour
        }
    
    # Add current request to storage
    user_requests.append(current_time)
    
    return {
        "is_limited": False,
        "reason": None,
        "requests_last_minute": requests_last_minute,
        "requests_last_hour": requests_last_hour + 1
    }


def validate_message_length(message_text: str) -> Dict[str, Any]:
    """
    Validate message length
    
    Args:
        message_text: Message to validate
        
    Returns:
        Dict with length validation result
    """
    if not HAS_DEFINITIONS:
        return {"is_valid": True, "reason": "No length rules configured"}
    
    message_length = len(message_text)
    min_length = SECURITY_RULES.get('min_message_length', 1)
    max_length = SECURITY_RULES.get('max_message_length', 1000)
    
    if message_length < min_length:
        return {
            "is_valid": False,
            "reason": f"Message too short (minimum {min_length} characters)",
            "actual_length": message_length
        }
    
    if message_length > max_length:
        return {
            "is_valid": False,
            "reason": f"Message too long (maximum {max_length} characters)",
            "actual_length": message_length
        }
    
    return {
        "is_valid": True,
        "reason": None,
        "actual_length": message_length
    }


def contains_offensive_content(message_text: str) -> Dict[str, Any]:
    """
    Scan for offensive content using keyword matching
    
    Args:
        message_text: Message to scan
        
    Returns:
        Dict with offensive content check result
    """
    if not HAS_DEFINITIONS:
        return {"contains_offensive": False, "reason": "No offensive keywords configured"}
    
    message_lower = message_text.lower()
    offensive_keywords = SECURITY_RULES.get('offensive_keywords', [])
    
    found_keywords = []
    for keyword in offensive_keywords:
        if keyword.lower() in message_lower:
            found_keywords.append(keyword)
    
    if found_keywords:
        return {
            "contains_offensive": True,
            "reason": f"Found offensive keywords: {', '.join(found_keywords)}",
            "keywords_found": found_keywords
        }
    
    return {
        "contains_offensive": False,
        "reason": None,
        "keywords_found": []
    }


def is_jailbreak_attempt(message_text: str) -> Dict[str, Any]:
    """
    Detect jailbreak attempt patterns
    
    Args:
        message_text: Message to analyze
        
    Returns:
        Dict with jailbreak detection result
    """
    if not HAS_DEFINITIONS:
        return {"is_jailbreak": False, "reason": "No jailbreak patterns configured"}
    
    message_lower = message_text.lower()
    jailbreak_patterns = SECURITY_RULES.get('jailbreak_patterns', [])
    
    found_patterns = []
    for pattern in jailbreak_patterns:
        if pattern.lower() in message_lower:
            found_patterns.append(pattern)
    
    if found_patterns:
        return {
            "is_jailbreak": True,
            "reason": f"Found jailbreak patterns: {', '.join(found_patterns)}",
            "patterns_found": found_patterns
        }
    
    return {
        "is_jailbreak": False,
        "reason": None,
        "patterns_found": []
    }