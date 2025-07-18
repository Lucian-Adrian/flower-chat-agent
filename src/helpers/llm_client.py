"""
LLM Client for XOFlowers AI Agent
Simple, direct calls to OpenAI/Gemini with fallback
Modular and testable LLM integration
"""

import os
import logging
import time
from typing import Dict, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Import debug manager
try:
    from debug_manager import get_debug_manager
    HAS_DEBUG = True
except ImportError:
    HAS_DEBUG = False

# AI service imports
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    OpenAI = None
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    genai = None
    HAS_GEMINI = False


class LLMClient:
    """
    Simple, direct LLM client with OpenAI/Gemini fallback
    Each function has one responsibility and is testable
    """
    
    def __init__(self):
        """Initialize LLM client with available services"""
        self.openai_client = None
        self.gemini_model = None
        
        # Initialize OpenAI
        if HAS_OPENAI:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("✅ OpenAI client initialized")
        
        # Initialize Gemini
        if HAS_GEMINI:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("✅ Gemini client initialized")
    
    def call_llm(self, prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Direct call to LLM with fallback
        
        Args:
            prompt: The prompt to send to LLM
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict with response and metadata
        """
        start_time = time.time()
        debug_manager = get_debug_manager() if HAS_DEBUG else None
        
        if debug_manager:
            debug_manager.log_info(f"Starting LLM call with prompt length: {len(prompt)}", "LLMClient", "call_llm_start")
        
        # Try OpenAI first
        if self.openai_client:
            try:
                response = self._call_openai(prompt, max_tokens)
                execution_time = time.time() - start_time
                
                if debug_manager:
                    debug_manager.log_operation(
                        component="LLMClient",
                        operation="openai_call",
                        input_data={"prompt_length": len(prompt), "max_tokens": max_tokens},
                        output_data={"response_length": len(response), "service": "openai"},
                        execution_time=execution_time,
                        success=True
                    )
                
                return {
                    "response": response,
                    "service_used": "openai",
                    "execution_time": execution_time,
                    "success": True
                }
                
            except Exception as e:
                logger.warning(f"⚠️ OpenAI request failed: {e}")
                if debug_manager:
                    debug_manager.log_error(f"OpenAI call failed: {e}", "LLMClient", "openai_call", e)
        
        # Fallback to Gemini
        if self.gemini_model:
            try:
                response = self._call_gemini(prompt)
                execution_time = time.time() - start_time
                
                if debug_manager:
                    debug_manager.log_operation(
                        component="LLMClient",
                        operation="gemini_call",
                        input_data={"prompt_length": len(prompt)},
                        output_data={"response_length": len(response), "service": "gemini"},
                        execution_time=execution_time,
                        success=True
                    )
                
                return {
                    "response": response,
                    "service_used": "gemini",
                    "execution_time": execution_time,
                    "success": True
                }
                
            except Exception as e:
                logger.warning(f"⚠️ Gemini request failed: {e}")
                if debug_manager:
                    debug_manager.log_error(f"Gemini call failed: {e}", "LLMClient", "gemini_call", e)
        
        # Both services failed
        execution_time = time.time() - start_time
        error_msg = "Both AI services unavailable"
        
        if debug_manager:
            debug_manager.log_operation(
                component="LLMClient",
                operation="call_llm",
                input_data={"prompt_length": len(prompt)},
                execution_time=execution_time,
                success=False,
                error_message=error_msg
            )
        
        return {
            "response": None,
            "service_used": None,
            "execution_time": execution_time,
            "success": False,
            "error": error_msg
        }
    
    def _call_openai(self, prompt: str, max_tokens: int) -> str:
        """Call OpenAI API directly"""
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for XOFlowers florist."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API directly"""
        response = self.gemini_model.generate_content(prompt)
        return response.text.strip()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of LLM services"""
        return {
            'openai_available': self.openai_client is not None,
            'gemini_available': self.gemini_model is not None,
            'has_openai_lib': HAS_OPENAI,
            'has_gemini_lib': HAS_GEMINI,
            'openai_key_configured': bool(os.getenv('OPENAI_API_KEY')),
            'gemini_key_configured': bool(os.getenv('GEMINI_API_KEY'))
        }


# Global LLM client instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get the global LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client

def call_llm(prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
    """Direct function to call LLM - used by other modules"""
    client = get_llm_client()
    return client.call_llm(prompt, max_tokens)