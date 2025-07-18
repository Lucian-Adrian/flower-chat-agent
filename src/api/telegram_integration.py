"""
Telegram Integration for XOFlowers AI Agent
Webhook handling with AI processing pipeline integration using async calls
Comprehensive logging for message reception and delivery
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from src.helpers.system_definitions import get_service_config, get_security_config
from src.helpers.utils import setup_logger, log_performance_metrics, create_request_id
from src.intelligence.ai_engine import process_message_ai

# Initialize logger
logger = setup_logger(__name__)

# Pydantic models for Telegram webhook data
class TelegramUser(BaseModel):
    """Telegram user model"""
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    """Telegram chat model"""
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class TelegramMessage(BaseModel):
    """Telegram message model"""
    message_id: int
    from_: Optional[TelegramUser] = Field(None, alias="from")
    chat: TelegramChat
    date: int
    text: Optional[str] = None
    
    @validator('text')
    def validate_text(cls, v):
        if v is not None:
            # Check message length limits
            security_config = get_security_config()
            max_length = security_config.get('max_message_length', 1000)
            if len(v) > max_length:
                raise ValueError(f'Message too long (max {max_length} characters)')
        return v


class TelegramUpdate(BaseModel):
    """Telegram update model"""
    update_id: int
    message: Optional[TelegramMessage] = None
    edited_message: Optional[TelegramMessage] = None
    callback_query: Optional[Dict[str, Any]] = None


class TelegramResponse(BaseModel):
    """Response model for Telegram API calls"""
    method: str = Field(..., description="Telegram API method")
    chat_id: int = Field(..., description="Chat ID to send message to")
    text: str = Field(..., description="Message text to send")
    parse_mode: Optional[str] = Field("HTML", description="Message parse mode")
    reply_to_message_id: Optional[int] = Field(None, description="Message ID to reply to")


class TelegramIntegration:
    """Telegram webhook integration handler"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.service_config = get_service_config()
        self.security_config = get_security_config()
        
        # Rate limiting storage (in production, use Redis)
        self.rate_limit_storage = {}
        
        self.logger.info("Telegram integration initialized")
    
    async def process_webhook(self, update: TelegramUpdate, request_id: str) -> Optional[TelegramResponse]:
        """
        Process incoming Telegram webhook update
        
        Args:
            update: Telegram update object
            request_id: Unique request identifier
            
        Returns:
            Optional[TelegramResponse]: Response to send back to Telegram
        """
        start_time = time.time()
        
        try:
            # Extract message from update
            message = update.message or update.edited_message
            
            if not message or not message.text:
                self.logger.debug(f"[{request_id}] Ignoring non-text message or empty update")
                return None
            
            # Extract user and chat information
            user_id = str(message.from_.id) if message.from_ else str(message.chat.id)
            chat_id = message.chat.id
            message_text = message.text.strip()
            
            self.logger.info(f"[{request_id}] Received Telegram message from user {user_id} "
                           f"in chat {chat_id}: '{message_text[:50]}...'")
            
            # Rate limiting check
            if not self._check_rate_limit(user_id, request_id):
                return TelegramResponse(
                    method="sendMessage",
                    chat_id=chat_id,
                    text="Te rog să aștepți puțin înainte să trimiți un alt mesaj. Mulțumesc pentru înțelegere!",
                    reply_to_message_id=message.message_id
                )
            
            # Process message through AI pipeline
            ai_result = await process_message_ai(
                user_message=message_text,
                user_id=user_id,
                context=None  # Will be retrieved from Redis by AI engine
            )
            
            processing_time = time.time() - start_time
            
            # Log the interaction
            self.logger.info(f"[{request_id}] AI processing completed in {processing_time:.3f}s - "
                           f"Success: {ai_result.get('success', False)} - "
                           f"Intent: {ai_result.get('intent')} - "
                           f"Service: {ai_result.get('service_used')}")
            
            # Prepare response
            response_text = ai_result.get('response', 'Îmi pare rău, nu am putut procesa mesajul tău.')
            
            # Format response for Telegram (handle long messages)
            formatted_response = self._format_telegram_response(response_text)
            
            # Log message delivery
            self.logger.info(f"[{request_id}] Sending Telegram response to chat {chat_id} "
                           f"({len(formatted_response)} chars)")
            
            return TelegramResponse(
                method="sendMessage",
                chat_id=chat_id,
                text=formatted_response,
                parse_mode="HTML",
                reply_to_message_id=message.message_id
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.error(f"[{request_id}] Error processing Telegram webhook: {e}")
            
            # Return error response
            if 'message' in locals() and message:
                return TelegramResponse(
                    method="sendMessage",
                    chat_id=message.chat.id,
                    text="Îmi pare rău, dar întâmpin dificultăți tehnice. Te rog să încerci din nou în câteva momente.",
                    reply_to_message_id=message.message_id
                )
            
            return None
    
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
                self.logger.warning(f"[{request_id}] Rate limit exceeded for user {user_id} "
                                  f"(minute limit: {minute_limit})")
                return False
            
            if len(user_data['hour_requests']) >= hour_limit:
                self.logger.warning(f"[{request_id}] Rate limit exceeded for user {user_id} "
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
    
    def _format_telegram_response(self, text: str) -> str:
        """
        Format response text for Telegram
        
        Args:
            text: Response text
            
        Returns:
            str: Formatted text for Telegram
        """
        # Telegram message limit is 4096 characters
        max_length = 4000  # Leave some buffer
        
        if len(text) <= max_length:
            return text
        
        # Truncate and add continuation message
        truncated = text[:max_length - 100]
        
        # Try to break at a sentence or word boundary
        last_sentence = truncated.rfind('.')
        last_space = truncated.rfind(' ')
        
        if last_sentence > max_length - 200:
            truncated = truncated[:last_sentence + 1]
        elif last_space > max_length - 50:
            truncated = truncated[:last_space]
        
        return truncated + "\n\n<i>Mesajul a fost scurtat pentru Telegram. Pentru informații complete, te rog să mă întrebi din nou.</i>"
    
    async def send_message(self, chat_id: int, text: str, reply_to_message_id: Optional[int] = None) -> bool:
        """
        Send message to Telegram chat (for external use)
        
        Args:
            chat_id: Telegram chat ID
            text: Message text
            reply_to_message_id: Optional message ID to reply to
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # This would typically use the Telegram Bot API
            # For now, we just log the message that would be sent
            self.logger.info(f"Would send Telegram message to chat {chat_id}: {text[:100]}...")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
    
    def get_webhook_info(self) -> Dict[str, Any]:
        """
        Get webhook configuration information
        
        Returns:
            Dict[str, Any]: Webhook information
        """
        return {
            'platform': 'telegram',
            'webhook_active': True,
            'rate_limiting': {
                'per_minute': self.security_config.get('rate_limit_per_minute', 20),
                'per_hour': self.security_config.get('rate_limit_per_hour', 200)
            },
            'message_limits': {
                'max_message_length': self.security_config.get('max_message_length', 1000),
                'telegram_response_limit': 4000
            }
        }


# Global integration instance
telegram_integration = TelegramIntegration()

# Create FastAPI router for Telegram endpoints
telegram_router = APIRouter(prefix="/telegram", tags=["telegram"])


@telegram_router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    update: TelegramUpdate
) -> JSONResponse:
    """
    Telegram webhook endpoint
    
    Receives updates from Telegram and processes them through the AI pipeline
    """
    request_id = create_request_id()
    start_time = time.time()
    
    logger.info(f"[{request_id}] Received Telegram webhook update: {update.update_id}")
    
    try:
        # Process the webhook update
        response = await telegram_integration.process_webhook(update, request_id)
        
        processing_time = time.time() - start_time
        
        # Log performance metrics in background
        background_tasks.add_task(
            log_performance_metrics,
            logger,
            "telegram_webhook_processing",
            processing_time,
            response is not None,
            {
                "request_id": request_id,
                "update_id": update.update_id,
                "has_message": update.message is not None,
                "response_generated": response is not None
            }
        )
        
        if response:
            logger.info(f"[{request_id}] Telegram webhook processed successfully in {processing_time:.3f}s")
            return JSONResponse(
                status_code=200,
                content=response.dict()
            )
        else:
            logger.info(f"[{request_id}] Telegram webhook processed but no response needed")
            return JSONResponse(
                status_code=200,
                content={"status": "ok", "message": "processed"}
            )
    
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"[{request_id}] Telegram webhook processing failed: {e}")
        
        # Log error in background
        background_tasks.add_task(
            log_performance_metrics,
            logger,
            "telegram_webhook_processing",
            processing_time,
            False,
            {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        
        # Return success to Telegram to avoid retries
        return JSONResponse(
            status_code=200,
            content={"status": "error", "message": "processed with error"}
        )


@telegram_router.get("/info")
async def telegram_info() -> Dict[str, Any]:
    """Get Telegram integration information"""
    return telegram_integration.get_webhook_info()


@telegram_router.post("/send-message")
async def send_telegram_message(
    chat_id: int,
    text: str,
    reply_to_message_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Send message to Telegram chat (for testing/admin use)
    
    Args:
        chat_id: Telegram chat ID
        text: Message text
        reply_to_message_id: Optional message ID to reply to
    """
    try:
        success = await telegram_integration.send_message(chat_id, text, reply_to_message_id)
        
        return {
            "success": success,
            "chat_id": chat_id,
            "message_length": len(text),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to send Telegram message via API: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message: {str(e)}"
        )


# Convenience functions for external use
async def process_telegram_message(user_id: str, message_text: str, chat_id: int) -> Optional[str]:
    """
    Process Telegram message and return response text
    
    Args:
        user_id: Telegram user ID
        message_text: Message text
        chat_id: Telegram chat ID
        
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
        logger.error(f"Error processing Telegram message: {e}")
        return "Îmi pare rău, dar întâmpin dificultăți tehnice."


def get_telegram_router() -> APIRouter:
    """Get the Telegram router for inclusion in main app"""
    return telegram_router