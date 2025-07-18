"""
Redis-based Context Management for XOFlowers AI Agent
Conversation history storage, retrieval, and context compression
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

try:
    import redis
    from redis.exceptions import ConnectionError, TimeoutError, RedisError
    REDIS_AVAILABLE = True
except ImportError:
    print("Warning: Redis not available, using in-memory fallback")
    REDIS_AVAILABLE = False
    # Mock redis exceptions for type hints
    class ConnectionError(Exception): pass
    class TimeoutError(Exception): pass
    class RedisError(Exception): pass

from src.utils.system_definitions import get_service_config, get_performance_config
from src.utils.utils import setup_logger, log_performance_metrics, log_fallback_activation


@dataclass
class ConversationMessage:
    """Single conversation message"""
    user: str
    assistant: str
    timestamp: str
    intent: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class ConversationContext:
    """Complete conversation context"""
    user_id: str
    messages: List[ConversationMessage]
    preferences: Dict[str, Any]
    last_updated: str
    total_messages: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_id': self.user_id,
            'messages': [asdict(msg) for msg in self.messages],
            'preferences': self.preferences,
            'last_updated': self.last_updated,
            'total_messages': self.total_messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """Create from dictionary"""
        messages = [ConversationMessage(**msg) for msg in data.get('messages', [])]
        return cls(
            user_id=data['user_id'],
            messages=messages,
            preferences=data.get('preferences', {}),
            last_updated=data['last_updated'],
            total_messages=data.get('total_messages', len(messages))
        )


class ContextManager:
    """Redis-based conversation context management"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.service_config = get_service_config()
        self.performance_config = get_performance_config()
        
        # Initialize Redis connection
        self.redis_client = None
        self.redis_available = self._setup_redis()
        
        # Context settings
        self.max_messages = self.performance_config['max_conversation_history']
        self.cleanup_interval = self.performance_config['context_cleanup_interval_hours']
        
        self.logger.info(f"Context Manager initialized (Redis available: {self.redis_available})")
    
    def _setup_redis(self) -> bool:
        """Initialize Redis connection with error handling"""
        if not REDIS_AVAILABLE:
            self.logger.warning("Redis module not available, using in-memory fallback")
            return False
            
        try:
            redis_config = self.service_config['redis']
            self.redis_client = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['db'],
                decode_responses=redis_config['decode_responses'],
                socket_timeout=redis_config['socket_timeout'],
                socket_connect_timeout=redis_config['socket_connect_timeout'],
                retry_on_timeout=redis_config['retry_on_timeout']
            )
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established successfully")
            return True
            
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
            return False
    
    def _get_context_key(self, user_id: str) -> str:
        """Generate Redis key for user context"""
        return f"xoflowers:context:{user_id}"
    
    async def get_context(self, user_id: str) -> Optional[ConversationContext]:
        """
        Retrieve conversation context for user
        
        Args:
            user_id: User identifier
        
        Returns:
            ConversationContext or None if not found/Redis unavailable
        """
        if not self.redis_available:
            self.logger.debug(f"Redis unavailable, returning empty context for user {user_id}")
            return None
        
        start_time = time.time()
        
        try:
            key = self._get_context_key(user_id)
            context_data = self.redis_client.get(key)
            
            duration = time.time() - start_time
            
            if context_data:
                context_dict = json.loads(context_data)
                context = ConversationContext.from_dict(context_dict)
                
                log_performance_metrics(self.logger, "redis_context_get", duration, True, 
                                      {"user_id": user_id, "messages_count": len(context.messages)})
                
                self.logger.debug(f"Retrieved context for user {user_id}: {len(context.messages)} messages")
                return context
            else:
                log_performance_metrics(self.logger, "redis_context_get", duration, True,
                                      {"user_id": user_id, "messages_count": 0})
                
                self.logger.debug(f"No context found for user {user_id}")
                return None
                
        except (ConnectionError, TimeoutError) as e:
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "redis_context_get", duration, False, 
                                  {"error": str(e), "user_id": user_id})
            log_fallback_activation(self.logger, "Redis", "no_context", f"Context retrieval failed: {e}", user_id)
            return None
            
        except Exception as e:
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "redis_context_get", duration, False,
                                  {"error": str(e), "user_id": user_id})
            self.logger.error(f"Failed to retrieve context for user {user_id}: {e}")
            return None
    
    async def save_context(self, context: ConversationContext, ttl_hours: int = 24) -> bool:
        """
        Save conversation context to Redis
        
        Args:
            context: ConversationContext to save
            ttl_hours: Time to live in hours
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.redis_available:
            self.logger.debug(f"Redis unavailable, cannot save context for user {context.user_id}")
            return False
        
        start_time = time.time()
        
        try:
            key = self._get_context_key(context.user_id)
            context_json = json.dumps(context.to_dict(), ensure_ascii=False)
            
            # Set with TTL
            ttl_seconds = ttl_hours * 3600
            self.redis_client.setex(key, ttl_seconds, context_json)
            
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "redis_context_save", duration, True,
                                  {"user_id": context.user_id, "messages_count": len(context.messages)})
            
            self.logger.debug(f"Saved context for user {context.user_id}: {len(context.messages)} messages")
            return True
            
        except (ConnectionError, TimeoutError) as e:
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "redis_context_save", duration, False,
                                  {"error": str(e), "user_id": context.user_id})
            log_fallback_activation(self.logger, "Redis", "no_save", f"Context save failed: {e}", context.user_id)
            return False
            
        except Exception as e:
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "redis_context_save", duration, False,
                                  {"error": str(e), "user_id": context.user_id})
            self.logger.error(f"Failed to save context for user {context.user_id}: {e}")
            return False
    
    async def add_message(self, user_id: str, user_message: str, assistant_response: str,
                         intent: Optional[str] = None, confidence: Optional[float] = None) -> bool:
        """
        Add new message to conversation context
        
        Args:
            user_id: User identifier
            user_message: User's message
            assistant_response: Assistant's response
            intent: Detected intent (optional)
            confidence: Intent confidence (optional)
        
        Returns:
            True if added successfully, False otherwise
        """
        # Get existing context or create new one
        context = await self.get_context(user_id)
        
        if context is None:
            context = ConversationContext(
                user_id=user_id,
                messages=[],
                preferences={},
                last_updated=datetime.now().isoformat(),
                total_messages=0
            )
        
        # Create new message
        new_message = ConversationMessage(
            user=user_message,
            assistant=assistant_response,
            timestamp=datetime.now().isoformat(),
            intent=intent,
            confidence=confidence
        )
        
        # Add message and update context
        context.messages.append(new_message)
        context.total_messages += 1
        context.last_updated = datetime.now().isoformat()
        
        # Apply context compression if needed
        context = self._compress_context(context)
        
        # Save updated context
        return await self.save_context(context)
    
    def _compress_context(self, context: ConversationContext) -> ConversationContext:
        """
        Compress context by keeping only recent messages
        
        Args:
            context: ConversationContext to compress
        
        Returns:
            Compressed ConversationContext
        """
        if len(context.messages) <= self.max_messages:
            return context
        
        # Keep only the most recent messages
        context.messages = context.messages[-self.max_messages:]
        
        self.logger.debug(f"Compressed context for user {context.user_id} to {len(context.messages)} messages")
        return context
    
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences in context
        
        Args:
            user_id: User identifier
            preferences: Preferences to update/merge
        
        Returns:
            True if updated successfully, False otherwise
        """
        context = await self.get_context(user_id)
        
        if context is None:
            context = ConversationContext(
                user_id=user_id,
                messages=[],
                preferences=preferences,
                last_updated=datetime.now().isoformat(),
                total_messages=0
            )
        else:
            # Merge preferences
            context.preferences.update(preferences)
            context.last_updated = datetime.now().isoformat()
        
        return await self.save_context(context)
    
    async def get_recent_messages(self, user_id: str, count: int = 5) -> List[ConversationMessage]:
        """
        Get recent messages for context
        
        Args:
            user_id: User identifier
            count: Number of recent messages to return
        
        Returns:
            List of recent ConversationMessage objects
        """
        context = await self.get_context(user_id)
        
        if context is None:
            return []
        
        return context.messages[-count:] if context.messages else []
    
    async def clear_context(self, user_id: str) -> bool:
        """
        Clear conversation context for user
        
        Args:
            user_id: User identifier
        
        Returns:
            True if cleared successfully, False otherwise
        """
        if not self.redis_available:
            return False
        
        try:
            key = self._get_context_key(user_id)
            result = self.redis_client.delete(key)
            
            self.logger.info(f"Cleared context for user {user_id}")
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Failed to clear context for user {user_id}: {e}")
            return False
    
    async def cleanup_old_contexts(self) -> int:
        """
        Clean up old conversation contexts
        
        Returns:
            Number of contexts cleaned up
        """
        if not self.redis_available:
            return 0
        
        try:
            # Get all context keys
            pattern = "xoflowers:context:*"
            keys = self.redis_client.keys(pattern)
            
            cleaned_count = 0
            cutoff_time = datetime.now() - timedelta(hours=self.cleanup_interval)
            
            for key in keys:
                try:
                    context_data = self.redis_client.get(key)
                    if context_data:
                        context_dict = json.loads(context_data)
                        last_updated = datetime.fromisoformat(context_dict['last_updated'])
                        
                        if last_updated < cutoff_time:
                            self.redis_client.delete(key)
                            cleaned_count += 1
                            
                except Exception as e:
                    self.logger.warning(f"Error processing context key {key}: {e}")
                    continue
            
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old contexts")
            
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Context cleanup failed: {e}")
            return 0
    
    def get_context_summary(self, context: ConversationContext) -> Dict[str, Any]:
        """
        Get summary of conversation context for AI processing
        
        Args:
            context: ConversationContext to summarize
        
        Returns:
            Context summary for AI processing
        """
        if not context or not context.messages:
            return {}
        
        recent_messages = context.messages[-3:]  # Last 3 exchanges
        
        return {
            "recent_messages": [
                {
                    "user": msg.user,
                    "assistant": msg.assistant,
                    "intent": msg.intent,
                    "timestamp": msg.timestamp
                }
                for msg in recent_messages
            ],
            "preferences": context.preferences,
            "total_messages": context.total_messages,
            "conversation_started": context.messages[0].timestamp if context.messages else None
        }


# Global context manager instance
_context_manager = None

def get_context_manager() -> ContextManager:
    """Get global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


# Convenience functions
async def get_user_context(user_id: str) -> Optional[ConversationContext]:
    """Get conversation context for user"""
    manager = get_context_manager()
    return await manager.get_context(user_id)


async def add_conversation_message(user_id: str, user_message: str, assistant_response: str,
                                 intent: Optional[str] = None, confidence: Optional[float] = None) -> bool:
    """Add message to conversation context"""
    manager = get_context_manager()
    return await manager.add_message(user_id, user_message, assistant_response, intent, confidence)


async def get_context_for_ai(user_id: str) -> Dict[str, Any]:
    """Get context summary for AI processing"""
    manager = get_context_manager()
    context = await manager.get_context(user_id)
    return manager.get_context_summary(context) if context else {}


async def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """Update user preferences"""
    manager = get_context_manager()
    return await manager.update_preferences(user_id, preferences)