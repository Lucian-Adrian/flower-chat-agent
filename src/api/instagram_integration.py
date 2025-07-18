"""
Instagram Integration for XOFlowers AI Agent
Meta webhook verification and handling with AI processing pipeline integration
Platform-specific message formatting and delivery with proper error handling
"""

import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks, Query, Header
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field, validator

from src.helpers.system_definitions import get_service_config, get_security_config
from src.helpers.utils import setup_logger, log_performance_metrics, create_request_id
from src.intelligence.ai_engine import process_message_ai

# Initialize logger
logger = setup_logger(__name__)

# Pydantic models for Instagram webhook data
class InstagramUser(BaseModel):
    """Instagram user model"""
    id: str
    username: Optional[str] = None
    name: Optional[str] = None


class InstagramMessage(BaseModel):
    """Instagram message model"""
    id: str
    text: Optional[str] = None
    timestamp: str
    
    @validator('text')
    def validate_text(cls, v):
        if v is not None:
            # Check message length limits
            security_config = get_security_config()
            max_length = security_config.get('max_message_length', 1000)
            if len(v) > max_length:
                raise ValueError(f'Message too long (max {max_length} characters)')
        return v


class InstagramMessaging(BaseModel):
    """Instagram messaging event model"""
    sender: InstagramUser
    recipient: InstagramUser
    timestamp: int
    message: Optional[InstagramMessage] = None


class InstagramEntry(BaseModel):
    """Instagram webhook entry model"""
    id: str
    time: int
    messaging: Optional[List[InstagramMessaging]] = None


class InstagramWebhook(BaseModel):
    """Instagram webhook payload model"""
    object: str
    entry: List[InstagramEntry]


class InstagramResponse(BaseModel):
    """Response model for Instagram API calls"""
    recipient_id: str = Field(..., description="Recipient user ID")
    message_text: str = Field(..., description="Message text to send")
    message_type: str = Field("text", description="Message type")
    platform: str = Field("instagram", description="Platform identifier")


class InstagramIntegration:
    """Instagram webhook integration handler with Meta verification"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.service_config = get_service_config()
        self.security_config = get_security_config()
        
        # Instagram/Meta specific configuration
        self.verify_token = self._get_verify_token()
        self.app_secret = self._get_app_secret()
        
        # Rate limiting storage (in production, use Redis)
        self.rate_limit_storage = {}
        
        self.logger.info("Instagram integration initialized")
    
    def _get_verify_token(self) -> str:
        """Get Instagram webhook verify token from environment"""
        import os
        token = os.getenv('INSTAGRAM_VERIFY_TOKEN', 'xoflowers_verify_token_2024')
        if not token:
            self.logger.warning("Instagram verify token not set - using default")
        return token
    
    def _get_app_secret(self) -> Optional[str]:
        """Get Instagram app secret for signature verification"""
        import os
        secret = os.getenv('INSTAGRAM_APP_SECRET')
        if not secret:
            self.logger.warning("Instagram app secret not set - signature verification disabled")
        return secret
    
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Instagram webhook signature
        
        Args:
            payload: Raw webhook payload
            signature: X-Hub-Signature-256 header value
            
        Returns:
            bool: True if signature is valid
        """
        if not self.app_secret:
            self.logger.warning("App secret not configured - skipping signature verification")
            return True
        
        try:
            # Remove 'sha256=' prefix if present
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.app_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(expected_signature, signature)
            
            if not is_valid:
                self.logger.warning("Instagram webhook signature verification failed")
            
            return is_valid
            
        except Exception as e:
            self.logger.error(f"Error verifying Instagram webhook signature: {e}")
            return False
    
    async def process_webhook(self, webhook: InstagramWebhook, request_id: str) -> List[InstagramResponse]:
        """
        Process incoming Instagram webhook
        
        Args:
            webhook: Instagram webhook payload
            request_id: Unique request identifier
            
        Returns:
            List[InstagramResponse]: List of responses to send
        """
        start_time = time.time()
        responses = []
        
        try:
            self.logger.info(f"[{request_id}] Processing Instagram webhook with {len(webhook.entry)} entries")
            
            for entry in webhook.entry:
                if not entry.messaging:
                    continue
                
                for messaging_event in entry.messaging:
                    response = await self._process_messaging_event(messaging_event, request_id)
                    if response:
                        responses.append(response)
            
            processing_time = time.time() - start_time
            self.logger.info(f"[{request_id}] Instagram webhook processed in {processing_time:.3f}s - "
                           f"Generated {len(responses)} responses")
            
            return responses
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"[{request_id}] Error processing Instagram webhook: {e}")
            return responses
    
    async def _process_messaging_event(self, messaging: InstagramMessaging, request_id: str) -> Optional[InstagramResponse]:
        """
        Process individual messaging event
        
        Args:
            messaging: Instagram messaging event
            request_id: Request identifier
            
        Returns:
            Optional[InstagramResponse]: Response to send or None
        """
        try:
            # Only process text messages
            if not messaging.message or not messaging.message.text:
                self.logger.debug(f"[{request_id}] Ignoring non-text Instagram message")
                return None
            
            user_id = messaging.sender.id
            message_text = messaging.message.text.strip()
            
            self.logger.info(f"[{request_id}] Received Instagram message from user {user_id}: "
                           f"'{message_text[:50]}...'")
            
            # Rate limiting check
            if not self._check_rate_limit(user_id, request_id):
                return InstagramResponse(
                    recipient_id=user_id,
                    message_text="Te rog să aștepți puțin înainte să trimiți un alt mesaj. Mulțumesc pentru înțelegere!"
                )
            
            # Process message through AI pipeline
            ai_result = await process_message_ai(
                user_message=message_text,
                user_id=user_id,
                context=None  # Will be retrieved from Redis by AI engine
            )
            
            # Log AI processing result
            self.logger.info(f"[{request_id}] AI processing completed - "
                           f"Success: {ai_result.get('success', False)} - "
                           f"Intent: {ai_result.get('intent')} - "
                           f"Service: {ai_result.get('service_used')}")
            
            # Prepare response
            response_text = ai_result.get('response', 'Îmi pare rău, nu am putut procesa mesajul tău.')
            
            # Format response for Instagram
            formatted_response = self._format_instagram_response(response_text)
            
            # Log message delivery
            self.logger.info(f"[{request_id}] Sending Instagram response to user {user_id} "
                           f"({len(formatted_response)} chars)")
            
            return InstagramResponse(
                recipient_id=user_id,
                message_text=formatted_response
            )
            
        except Exception as e:
            self.logger.error(f"[{request_id}] Error processing Instagram messaging event: {e}")
            
            # Return error response
            return InstagramResponse(
                recipient_id=messaging.sender.id,
                message_text="Îmi pare rău, dar întâmpin dificultăți tehnice. Te rog să încerci din nou în câteva momente."
            )
    
    def _check_rate_limit(self, user_id: str, request_id: str) -> bool:
        """
        Check if user is within rate limits
        
        Args:
            user_id: User identifier
            request_id: Request identifier
            
        Returns:
            bool: True if within limits, False if rate limited
        """
        try:
            current_time = time.time()
            
            # Initialize user rate limit data if not exists
            if user_id not in self.rate_limit_storage:
                self.rate_limit_storage[user_id] = {
                    'minute_requests': [],
                    'hour_requests': []
                }
            
            user_data = self.rate_limit_storage[user_id]
            
            # Clean old requests (older than 1 hour)
            user_data['minute_requests'] = [
                req_time for req_time in user_data['minute_requests']
                if current_time - req_time < 60
            ]
            user_data['hour_requests'] = [
                req_time for req_time in user_data['hour_requests']
                if current_time - req_time < 3600
            ]
            
            # Check limits
            minute_limit = self.security_config.get('rate_limit_per_minute', 20)
            hour_limit = self.security_config.get('rate_limit_per_hour', 200)
            
            if len(user_data['minute_requests']) >= minute_limit:
                self.logger.warning(f"[{request_id}] Rate limit exceeded for Instagram user {user_id} "
                                  f"(minute limit: {minute_limit})")
                return False
            
            if len(user_data['hour_requests']) >= hour_limit:
                self.logger.warning(f"[{request_id}] Rate limit exceeded for Instagram user {user_id} "
                                  f"(hour limit: {hour_limit})")
                return False
            
            # Add current request
            user_data['minute_requests'].append(current_time)
            user_data['hour_requests'].append(current_time)
            
            return True
            
        except Exception as e:
            self.logger.error(f"[{request_id}] Error checking rate limit: {e}")
            # Allow request if rate limiting fails
            return True
    
    def _format_instagram_response(self, text: str) -> str:
        """
        Format response text for Instagram
        
        Args:
            text: Response text
            
        Returns:
            str: Formatted text for Instagram
        """
        # Instagram message limit is 1000 characters
        max_length = 950  # Leave some buffer
        
        if len(text) <= max_length:
            return text
        
        # Truncate and add continuation message
        truncated = text[:max_length - 80]
        
        # Try to break at a sentence or word boundary
        last_sentence = truncated.rfind('.')
        last_space = truncated.rfind(' ')
        
        if last_sentence > max_length - 150:
            truncated = truncated[:last_sentence + 1]
        elif last_space > max_length - 30:
            truncated = truncated[:last_space]
        
        return truncated + "\n\nPentru informații complete, te rog să mă întrebi din nou."
    
    async def send_message(self, recipient_id: str, message_text: str) -> bool:
        """
        Send message to Instagram user (for external use)
        
        Args:
            recipient_id: Instagram user ID
            message_text: Message text
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # This would typically use the Instagram Graph API
            # For now, we just log the message that would be sent
            self.logger.info(f"Would send Instagram message to user {recipient_id}: {message_text[:100]}...")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send Instagram message: {e}")
            return False
    
    def get_webhook_info(self) -> Dict[str, Any]:
        """
        Get webhook configuration information
        
        Returns:
            Dict[str, Any]: Webhook information
        """
        return {
            'platform': 'instagram',
            'webhook_active': True,
            'verify_token_configured': bool(self.verify_token),
            'app_secret_configured': bool(self.app_secret),
            'signature_verification': bool(self.app_secret),
            'rate_limiting': {
                'per_minute': self.security_config.get('rate_limit_per_minute', 20),
                'per_hour': self.security_config.get('rate_limit_per_hour', 200)
            },
            'message_limits': {
                'max_message_length': self.security_config.get('max_message_length', 1000),
                'instagram_response_limit': 950
            }
        }


# Global integration instance
instagram_integration = InstagramIntegration()

# Create FastAPI router for Instagram endpoints
instagram_router = APIRouter(prefix="/instagram", tags=["instagram"])


@instagram_router.get("/webhook")
async def instagram_webhook_verification(
    hub_mode: str = Query(alias="hub.mode"),
    hub_challenge: str = Query(alias="hub.challenge"),
    hub_verify_token: str = Query(alias="hub.verify_token")
) -> PlainTextResponse:
    """
    Instagram webhook verification endpoint
    
    Meta sends a GET request to verify the webhook URL
    """
    logger.info(f"Instagram webhook verification request - Mode: {hub_mode}, Token: {hub_verify_token}")
    
    # Verify the webhook
    if hub_mode == "subscribe" and hub_verify_token == instagram_integration.verify_token:
        logger.info("Instagram webhook verification successful")
        return PlainTextResponse(content=hub_challenge, status_code=200)
    else:
        logger.warning(f"Instagram webhook verification failed - Expected token: {instagram_integration.verify_token}")
        raise HTTPException(status_code=403, detail="Verification failed")


@instagram_router.post("/webhook")
async def instagram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
) -> JSONResponse:
    """
    Instagram webhook endpoint
    
    Receives updates from Instagram and processes them through the AI pipeline
    """
    request_id = create_request_id()
    start_time = time.time()
    
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Verify webhook signature if app secret is configured
        if x_hub_signature_256:
            if not instagram_integration.verify_webhook_signature(body, x_hub_signature_256):
                logger.warning(f"[{request_id}] Instagram webhook signature verification failed")
                raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse webhook payload
        try:
            payload_data = json.loads(body.decode('utf-8'))
            webhook = InstagramWebhook(**payload_data)
        except Exception as e:
            logger.error(f"[{request_id}] Failed to parse Instagram webhook payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid payload format")
        
        logger.info(f"[{request_id}] Received Instagram webhook - Object: {webhook.object}")
        
        # Process the webhook
        responses = await instagram_integration.process_webhook(webhook, request_id)
        
        processing_time = time.time() - start_time
        
        # Log performance metrics in background
        background_tasks.add_task(
            log_performance_metrics,
            logger,
            "instagram_webhook_processing",
            processing_time,
            len(responses) > 0,
            {
                "request_id": request_id,
                "entries_count": len(webhook.entry),
                "responses_generated": len(responses),
                "signature_verified": x_hub_signature_256 is not None
            }
        )
        
        logger.info(f"[{request_id}] Instagram webhook processed successfully in {processing_time:.3f}s - "
                   f"Generated {len(responses)} responses")
        
        # Return responses (in production, these would be sent via Instagram Graph API)
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "processed": True,
                "responses": [response.dict() for response in responses],
                "request_id": request_id
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"[{request_id}] Instagram webhook processing failed: {e}")
        
        # Log error in background
        background_tasks.add_task(
            log_performance_metrics,
            logger,
            "instagram_webhook_processing",
            processing_time,
            False,
            {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        
        # Return success to Instagram to avoid retries
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": "processed with error", "request_id": request_id}
        )


@instagram_router.get("/info")
async def instagram_info() -> Dict[str, Any]:
    """Get Instagram integration information"""
    return instagram_integration.get_webhook_info()


@instagram_router.post("/send-message")
async def send_instagram_message(
    recipient_id: str,
    message_text: str
) -> Dict[str, Any]:
    """
    Send message to Instagram user (for testing/admin use)
    
    Args:
        recipient_id: Instagram user ID
        message_text: Message text
    """
    try:
        success = await instagram_integration.send_message(recipient_id, message_text)
        
        return {
            "success": success,
            "recipient_id": recipient_id,
            "message_length": len(message_text),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to send Instagram message via API: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message: {str(e)}"
        )


# Convenience functions for external use
async def process_instagram_message(user_id: str, message_text: str) -> Optional[str]:
    """
    Process Instagram message and return response text
    
    Args:
        user_id: Instagram user ID
        message_text: Message text
        
    Returns:
        Optional[str]: Response text or None
    """
    try:
        ai_result = await process_message_ai(
            user_message=message_text,
            user_id=user_id,
            context=None
        )
        
        if ai_result.get('success'):
            return ai_result.get('response')
        else:
            return "Îmi pare rău, nu am putut procesa mesajul tău în acest moment."
    
    except Exception as e:
        logger.error(f"Error processing Instagram message: {e}")
        return "Îmi pare rău, dar întâmpin dificultăți tehnice."


def get_instagram_router() -> APIRouter:
    """Get the Instagram router for inclusion in main app"""
    return instagram_router