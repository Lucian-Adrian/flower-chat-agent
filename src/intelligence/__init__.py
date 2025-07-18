"""
Intelligence module for XOFlowers AI Agent
Contains AI processing, security, and context management components
"""

from .ai_engine import process_message_ai, get_ai_engine, AIEngine, AIResponse
from .security_ai import check_message_security, is_message_safe, generate_security_response, SecurityResult
from .context_manager import get_user_context, add_conversation_message, get_context_for_ai, update_user_preferences

__all__ = [
    'process_message_ai',
    'get_ai_engine', 
    'AIEngine',
    'AIResponse',
    'check_message_security',
    'is_message_safe',
    'generate_security_response',
    'SecurityResult',
    'get_user_context',
    'add_conversation_message',
    'get_context_for_ai',
    'update_user_preferences'
]