"""
AI-Powered Security System for XOFlowers
AI-based jailbreak detection and message appropriateness evaluation using modern Gemini API
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pydantic import BaseModel, Field

from openai import OpenAI
# Use the NEW Gemini API as specified in the AI guide
from google import genai
from google.genai import types

from src.utils.system_definitions import get_service_config, get_ai_prompts, get_security_config
from src.utils.utils import (
    setup_logger, log_security_check, log_fallback_activation, log_performance_metrics,
    log_error_with_monitoring, PerformanceTimer, get_performance_monitor
)


@dataclass
class SecurityResult:
    """Security check result data structure"""
    is_safe: bool
    risk_level: str  # "low", "medium", "high"
    detected_issues: List[str]
    should_proceed: bool
    reason: str
    confidence: float
    processing_time: float
    service_used: str


class SecurityAnalysis(BaseModel):
    """Pydantic model for structured security analysis output"""
    is_safe: bool = Field(description="Whether the message is safe and appropriate")
    risk_level: str = Field(description="Risk level: low, medium, or high")
    detected_issues: List[str] = Field(description="List of detected security issues")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    reason: str = Field(description="Detailed explanation of the security assessment")


class SecurityAI:
    """AI-powered security system for message evaluation"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.service_config = get_service_config()
        self.ai_prompts = get_ai_prompts()
        self.security_config = get_security_config()
        
        # Initialize AI services (reuse from ai_engine pattern)
        self._setup_openai()
        self._setup_gemini()
        
        self.logger.info("Security AI system initialized")
    
    def _setup_openai(self) -> None:
        """Initialize OpenAI client"""
        try:
            openai_config = self.service_config['openai']
            if openai_config['api_key']:
                self.openai_client = OpenAI(api_key=openai_config['api_key'])
                self.openai_available = True
                self.logger.info("OpenAI client initialized for security checks")
            else:
                self.openai_client = None
                self.openai_available = False
                self.logger.warning("OpenAI API key not found, security AI unavailable")
        except Exception as e:
            self.openai_client = None
            self.openai_available = False
            self.logger.error(f"Failed to initialize OpenAI for security: {e}")
    
    def _setup_gemini(self) -> None:
        """Initialize Gemini client using the NEW Gemini API as specified in AI guide"""
        try:
            gemini_config = self.service_config['gemini']
            
            self.logger.info(f"Setting up Gemini with model: {gemini_config['model']}")
            
            # Try primary key first using NEW API
            if gemini_config['api_key']:
                try:
                    self.logger.info("Trying primary Gemini API key with NEW API...")
                    self.gemini_client = genai.Client(api_key=gemini_config['api_key'])
                    self.gemini_model = gemini_config['model']  # Just store model name
                    self.gemini_available = True
                    self.gemini_current_key = 'primary'
                    self.logger.info("[OK] Gemini client initialized for security checks with primary key")
                    return
                except Exception as e:
                    self.logger.warning(f"[ERROR] Primary Gemini key failed for security: {e}")
            else:
                self.logger.warning("Primary Gemini API key not found")
            
            # Try backup key if primary fails
            if gemini_config['api_key_backup']:
                try:
                    self.logger.info("Trying backup Gemini API key with NEW API...")
                    self.gemini_client = genai.Client(api_key=gemini_config['api_key_backup'])
                    self.gemini_model = gemini_config['model']  # Just store model name
                    self.gemini_available = True
                    self.gemini_current_key = 'backup'
                    self.logger.info("[OK] Gemini client initialized for security checks with backup key")
                    return
                except Exception as e:
                    self.logger.warning(f"[ERROR] Backup Gemini key failed for security: {e}")
            else:
                self.logger.warning("Backup Gemini API key not found")
            
            # No working keys
            self.gemini_available = False
            self.gemini_current_key = None
            self.logger.error("No working Gemini API keys found for security")
            
        except Exception as e:
            self.gemini_available = False
            self.gemini_current_key = None
            self.logger.error(f"Failed to initialize Gemini for security: {e}")
    
    async def check_message_security(self, message: str, user_id: str) -> SecurityResult:
        """
        Main security check entry point with enhanced monitoring
        
        Args:
            message: User message to check
            user_id: User identifier for logging
        
        Returns:
            SecurityResult with safety assessment
        """
        # Record user activity for monitoring
        monitor = get_performance_monitor()
        monitor.record_user_activity(user_id)
        
        start_time = time.time()
        
        self.logger.info(f"Starting security check for user {user_id}")
        
        try:
            # Step 1: Basic pattern matching (fast pre-filter)
            basic_check = self._basic_security_check(message)
            
            # If basic check fails, no need for AI
            if not basic_check['is_safe']:
                processing_time = time.time() - start_time
                result = SecurityResult(
                    is_safe=False,
                    risk_level="high",
                    detected_issues=basic_check['issues'],
                    should_proceed=False,
                    reason="Failed basic security patterns",
                    confidence=0.9,
                    processing_time=processing_time,
                    service_used="pattern_matching"
                )
                
                log_security_check(self.logger, user_id, message, False, "high", basic_check['issues'])
                return result
            
            # Step 2: AI-powered security analysis - REQUIRED
            ai_result = await self._ai_security_analysis(message)
            
            processing_time = time.time() - start_time
            
            if ai_result:
                result = SecurityResult(
                    is_safe=ai_result['is_safe'],
                    risk_level=ai_result['risk_level'],
                    detected_issues=ai_result['detected_issues'],
                    should_proceed=ai_result['should_proceed'],
                    reason=ai_result['reason'],
                    confidence=0.8,
                    processing_time=processing_time,
                    service_used=ai_result.get('service_used', 'ai')
                )
            else:
                # AI MUST work - no fallback allowed
                raise Exception("AI security analysis failed - both OpenAI and Gemini unavailable. System requires AI security checks.")
            
            log_security_check(self.logger, user_id, message, result.is_safe, 
                             result.risk_level, result.detected_issues)
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"Security check failed for user {user_id}: {e}")
            
            # NO FALLBACK - Security system MUST work
            raise Exception(f"Security system failed - system requires functional AI security: {e}")
    
    def _basic_security_check(self, message: str) -> Dict[str, Any]:
        """
        Basic pattern-based security check (fast pre-filter)
        
        Args:
            message: Message to check
        
        Returns:
            Dict with is_safe status and detected issues
        """
        issues = []
        message_lower = message.lower()
        
        # Check message length
        if len(message) > self.security_config['max_message_length']:
            issues.append("Message too long")
        
        # Check for known jailbreak patterns
        for pattern in self.security_config['jailbreak_patterns']:
            if pattern in message_lower:
                issues.append(f"Jailbreak pattern detected: {pattern}")
        
        # Check for obvious inappropriate content
        inappropriate_patterns = [
            'hack', 'exploit', 'bypass', 'override',
            'system prompt', 'ignore instructions',
            'pretend you are', 'act as if you are',
            'forget everything', 'new instructions'
        ]
        
        for pattern in inappropriate_patterns:
            if pattern in message_lower:
                issues.append(f"Inappropriate pattern: {pattern}")
        
        return {
            'is_safe': len(issues) == 0,
            'issues': issues
        }
    
    async def _ai_security_analysis(self, message: str) -> Optional[Dict[str, Any]]:
        """
        AI-powered security analysis using fallback chain
        
        Args:
            message: Message to analyze
        
        Returns:
            Security analysis result or None if all AI services fail
        """
        prompt = self.ai_prompts['security_system_prompt'] + f"\n\nMESSAGE TO ANALYZE: {message}"
        
        # Try Gemini first (primary AI service)
        if self.gemini_available:
            result = await self._call_gemini_security(prompt)
            if result:
                result['service_used'] = 'gemini'
                return result
        
        # Try OpenAI as backup
        if self.openai_available:
            result = await self._call_openai_security(prompt)
            if result:
                result['service_used'] = 'openai'
                return result
        
        # NO FALLBACK - AI services MUST work for security
        raise Exception("All AI services failed for security analysis - system requires functional AI security checks")
    
    async def _call_openai_security(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI for security analysis"""
        try:
            start_time = time.time()
            
            response = await asyncio.to_thread(
                self.openai_client.chat.completions.create,
                model=self.service_config['openai']['model'],
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent security decisions
                max_tokens=300,
                timeout=self.service_config['openai']['timeout']
            )
            
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "openai_security_check", duration, True)
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"OpenAI security response not valid JSON: {e}")
            return None
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            log_performance_metrics(self.logger, "openai_security_check", duration, False, {"error": str(e)})
            log_fallback_activation(self.logger, "OpenAI", "Gemini", f"Security check failed: {e}")
            return None
    
    async def _call_gemini_security(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Gemini for security analysis using NEW API with structured output"""
        try:
            start_time = time.time()
            
            # Use the NEW Gemini API with structured output as shown in AI guide
            response = await asyncio.to_thread(
                self.gemini_client.models.generate_content,
                model=self.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=SecurityAnalysis,
                    temperature=0.1,  # Low temperature for consistent security decisions
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
                )
            )
            
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "gemini_security_check", duration, True)
            
            # Use the parsed structured output directly
            security_analysis = response.parsed
            
            if security_analysis:
                # Convert Pydantic model to dict
                result = {
                    'is_safe': security_analysis.is_safe,
                    'risk_level': security_analysis.risk_level,
                    'detected_issues': security_analysis.detected_issues,
                    'should_proceed': security_analysis.is_safe,  # Safe = can proceed
                    'reason': security_analysis.reason,
                    'confidence': security_analysis.confidence
                }
                return result
            else:
                raise Exception("No parsed result from Gemini structured output")
            
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            log_performance_metrics(self.logger, "gemini_security_check", duration, False, {"error": str(e)})
            self.logger.error(f"Gemini security check failed: {e}")
            return None
    
    def generate_safe_response(self, detected_issues: List[str], risk_level: str) -> str:
        """
        Generate appropriate response for blocked messages
        
        Args:
            detected_issues: List of security issues detected
            risk_level: Risk level (low/medium/high)
        
        Returns:
            Safe response message
        """
        if risk_level == "high":
            return ("Îmi pare rău, dar nu pot să răspund la acest tip de mesaj. "
                   "Te rog să îmi pui întrebări despre florile noastre, serviciile "
                   "sau informații despre magazin. Sunt aici să te ajut cu tot ce "
                   "ține de XOFlowers!")
        
        elif risk_level == "medium":
            return ("Să ne concentrăm pe florile noastre frumoase! "
                   "Cum te pot ajuta să găsești aranjamentul perfect pentru tine? "
                   "Avem o gamă largă de flori proaspete și servicii personalizate.")
        
        else:  # low risk
            return ("Te înțeleg, dar prefer să vorbim despre florile noastre. "
                   "Ce fel de flori te interesează? Pot să îți recomand ceva special!")
    
    async def is_message_safe(self, message: str, user_id: str) -> bool:
        """
        Simple boolean check if message is safe
        
        Args:
            message: Message to check
            user_id: User identifier
        
        Returns:
            True if message is safe, False otherwise
        """
        result = await self.check_message_security(message, user_id)
        return result.is_safe


# Global security AI instance
_security_ai = None

def get_security_ai() -> SecurityAI:
    """Get global security AI instance"""
    global _security_ai
    if _security_ai is None:
        _security_ai = SecurityAI()
    return _security_ai


# Convenience functions
async def check_message_security(message: str, user_id: str) -> SecurityResult:
    """
    Check message security using AI
    
    Args:
        message: Message to check
        user_id: User identifier
    
    Returns:
        SecurityResult with safety assessment
    """
    security_ai = get_security_ai()
    return await security_ai.check_message_security(message, user_id)


async def is_message_safe(message: str, user_id: str) -> bool:
    """
    Simple boolean check if message is safe
    
    Args:
        message: Message to check
        user_id: User identifier
    
    Returns:
        True if message is safe, False otherwise
    """
    security_ai = get_security_ai()
    return await security_ai.is_message_safe(message, user_id)


def generate_security_response(detected_issues: List[str], risk_level: str) -> str:
    """
    Generate appropriate response for blocked messages
    
    Args:
        detected_issues: List of security issues detected
        risk_level: Risk level (low/medium/high)
    
    Returns:
        Safe response message
    """
    security_ai = get_security_ai()
    return security_ai.generate_safe_response(detected_issues, risk_level)