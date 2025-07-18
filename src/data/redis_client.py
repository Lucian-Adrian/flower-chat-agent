"""
Redis Client for XOFlowers AI Agent
Handles conversation context storage and retrieval with automatic serialization
Provides connection pooling and graceful degradation when Redis is unavailable
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from src.utils.system_definitions import get_service_config
from src.utils.utils import setup_logger

logger = setup_logger(__name__)

# Try to import Redis dependencies
try:
    import redis
    from redis.connection import ConnectionPool
    HAS_REDIS = True
    logger.info("Redis dependencies available")
except ImportError:
    redis = None
    ConnectionPool = None
    HAS_REDIS = False
    logger.warning("Redis dependencies not available - using fallback mode")

class RedisClient:
    """
    Redis client for conversation context storage
    Provides automatic serialization and graceful degradation
    """
    
    def __init__(self):
        """Initialize Redis client with configuration from system_definitions"""
        self.config = get_service_config()['redis']
        
        # Client state
        self.client = None
        self.connection_pool = None
        self.initialized = False
        
        # Context key prefix
        self.context_prefix = "xoflowers:context:"
        self.session_prefix = "xoflowers:session:"
        
        # In-memory fallback storage for when Redis is unavailable
        self._fallback_storage = {}
        self._fallback_ttl = {}
        
        # Initialize with graceful degradation
        if HAS_REDIS:
            self._initialize_client()
        else:
            logger.warning("Redis dependencies not available - using in-memory fallback mode")
            self.initialized = False
    
    def _initialize_client(self) -> None:
        """
        Initialize Redis client with optimized connection pooling
        """
        try:
            # Create optimized connection pool with performance settings
            self.connection_pool = ConnectionPool(
                host=self.config['host'],
                port=self.config['port'],
                db=self.config['db'],
                decode_responses=self.config['decode_responses'],
                socket_timeout=self.config.get('socket_timeout', 5),
                socket_connect_timeout=self.config.get('socket_connect_timeout', 5),
                retry_on_timeout=self.config.get('retry_on_timeout', True),
                max_connections=50,  # Increased for better performance
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30  # Health check every 30 seconds
            )
            
            # Create Redis client
            self.client = redis.Redis(connection_pool=self.connection_pool)
            
            # Test connection
            self.client.ping()
            
            self.initialized = True
            logger.info(f"Redis client initialized successfully at {self.config['host']}:{self.config['port']}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis client: {e}")
            logger.info("Redis unavailable - system will use Gemini chat for context management")
            self.initialized = False
    
    def store_context(self, user_id: str, context_data: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """
        Store conversation context for a user with fallback to in-memory storage
        
        Args:
            user_id: Unique user identifier
            context_data: Context data to store
            ttl_hours: Time to live in hours
            
        Returns:
            bool: True if stored successfully, False otherwise
        """
        try:
            key = f"{self.context_prefix}{user_id}"
            
            # Add timestamp to context
            context_data['last_updated'] = datetime.now().isoformat()
            context_data['user_id'] = user_id
            
            # Try Redis first
            if self.is_available():
                serialized_data = json.dumps(context_data, ensure_ascii=False)
                ttl_seconds = ttl_hours * 3600
                
                result = self.client.setex(key, ttl_seconds, serialized_data)
                
                if result:
                    logger.debug(f"Context stored in Redis for user {user_id}")
                    return True
                else:
                    logger.warning(f"Failed to store context in Redis for user {user_id}")
            
            # Fallback to in-memory storage
            self._fallback_storage[key] = context_data
            self._fallback_ttl[key] = datetime.now() + timedelta(hours=ttl_hours)
            logger.debug(f"Context stored in fallback memory for user {user_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error storing context for user {user_id}: {e}")
            # Still try fallback storage
            try:
                key = f"{self.context_prefix}{user_id}"
                self._fallback_storage[key] = context_data
                self._fallback_ttl[key] = datetime.now() + timedelta(hours=ttl_hours)
                logger.debug(f"Context stored in fallback memory for user {user_id} after error")
                return True
            except:
                return False
    
    def retrieve_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation context for a user with fallback to in-memory storage
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Optional[Dict[str, Any]]: Context data or None if not found
        """
        try:
            key = f"{self.context_prefix}{user_id}"
            
            # Try Redis first
            if self.is_available():
                serialized_data = self.client.get(key)
                
                if serialized_data:
                    context_data = json.loads(serialized_data)
                    logger.debug(f"Context retrieved from Redis for user {user_id}")
                    return context_data
            
            # Fallback to in-memory storage
            if key in self._fallback_storage:
                # Check if not expired
                if key in self._fallback_ttl and datetime.now() < self._fallback_ttl[key]:
                    logger.debug(f"Context retrieved from fallback memory for user {user_id}")
                    return self._fallback_storage[key]
                else:
                    # Remove expired entry
                    if key in self._fallback_storage:
                        del self._fallback_storage[key]
                    if key in self._fallback_ttl:
                        del self._fallback_ttl[key]
                    logger.debug(f"Expired context removed from fallback memory for user {user_id}")
            
            logger.debug(f"No context found for user {user_id}")
            return None
                    
        except Exception as e:
            logger.error(f"Error retrieving context for user {user_id}: {e}")
            # Try fallback storage even on error
            try:
                key = f"{self.context_prefix}{user_id}"
                if key in self._fallback_storage and key in self._fallback_ttl:
                    if datetime.now() < self._fallback_ttl[key]:
                        return self._fallback_storage[key]
            except:
                pass
            return None
    
    def update_context(self, user_id: str, updates: Dict[str, Any], ttl_hours: int = 24) -> bool:
        """
        Update existing context with new data
        
        Args:
            user_id: Unique user identifier
            updates: Dictionary of updates to apply
            ttl_hours: Time to live in hours
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            # Get existing context
            existing_context = self.retrieve_context(user_id) or {}
            
            # Apply updates
            existing_context.update(updates)
            
            # Store updated context
            return self.store_context(user_id, existing_context, ttl_hours)
            
        except Exception as e:
            logger.error(f"Error updating context for user {user_id}: {e}")
            return False
    
    def add_message_to_context(self, user_id: str, user_message: str, assistant_response: str, 
                              intent: str = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a message exchange to the conversation context
        
        Args:
            user_id: Unique user identifier
            user_message: User's message
            assistant_response: Assistant's response
            intent: Detected intent (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            context = self.retrieve_context(user_id) or {
                'user_id': user_id,
                'messages': [],
                'preferences': {},
                'session_start': datetime.now().isoformat()
            }
            
            # Create message entry
            message_entry = {
                'user': user_message,
                'assistant': assistant_response,
                'timestamp': datetime.now().isoformat(),
                'intent': intent,
                'metadata': metadata or {}
            }
            
            # Add to messages list
            if 'messages' not in context:
                context['messages'] = []
            
            context['messages'].append(message_entry)
            
            # Keep only last 10 messages to prevent context from growing too large
            if len(context['messages']) > 10:
                context['messages'] = context['messages'][-10:]
            
            # Store updated context
            return self.store_context(user_id, context)
            
        except Exception as e:
            logger.error(f"Error adding message to context for user {user_id}: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent conversation history for a user
        
        Args:
            user_id: Unique user identifier
            limit: Maximum number of messages to return
            
        Returns:
            List[Dict[str, Any]]: List of recent messages
        """
        try:
            context = self.retrieve_context(user_id)
            
            if not context or 'messages' not in context:
                return []
            
            messages = context['messages']
            
            # Return last 'limit' messages
            return messages[-limit:] if len(messages) > limit else messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history for user {user_id}: {e}")
            return []
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences in context
        
        Args:
            user_id: Unique user identifier
            preferences: Dictionary of preferences to update
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        try:
            context = self.retrieve_context(user_id) or {'user_id': user_id}
            
            if 'preferences' not in context:
                context['preferences'] = {}
            
            context['preferences'].update(preferences)
            
            return self.store_context(user_id, context)
            
        except Exception as e:
            logger.error(f"Error updating preferences for user {user_id}: {e}")
            return False
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user preferences from context
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dict[str, Any]: User preferences or empty dict
        """
        try:
            context = self.retrieve_context(user_id)
            
            if context and 'preferences' in context:
                return context['preferences']
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error getting preferences for user {user_id}: {e}")
            return {}
    
    def delete_context(self, user_id: str) -> bool:
        """
        Delete conversation context for a user
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            key = f"{self.context_prefix}{user_id}"
            
            # Check if Redis is available, return False if not (graceful degradation)
            if not self.is_available():
                logger.debug(f"Redis unavailable, cannot delete context for user {user_id}")
                return False
            
            # Delete from Redis
            result = self.client.delete(key)
            logger.debug(f"Context deleted from Redis for user {user_id}")
            return result > 0
                
        except Exception as e:
            logger.error(f"Error deleting context for user {user_id}: {e}")
            return False
    
    def cleanup_expired_contexts(self) -> int:
        """
        Clean up expired contexts from Redis
        
        Returns:
            int: Number of contexts cleaned up
        """
        cleaned_count = 0
        
        try:
            # Check if Redis is available, return 0 if not (graceful degradation)
            if not self.is_available():
                logger.debug("Redis unavailable, cannot perform context cleanup")
                return 0
            
            # Redis handles TTL automatically, so this is mainly for manual cleanup
            # We can scan for expired keys if needed, but Redis TTL handles most cases
            logger.debug("Context cleanup completed (Redis handles TTL automatically)")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during context cleanup: {e}")
            return 0
    
    def is_available(self) -> bool:
        """
        Check if Redis is available and properly initialized
        
        Returns:
            bool: True if Redis is available, False otherwise
        """
        if not HAS_REDIS or not self.initialized:
            return False
        
        try:
            # Test connection with ping
            self.client.ping()
            return True
        except Exception:
            return False
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get Redis connection statistics
        
        Returns:
            Dict[str, Any]: Connection statistics
        """
        stats = {
            'redis_available': HAS_REDIS,
            'client_initialized': self.initialized,
            'connection_active': self.is_available(),
            'host': self.config['host'],
            'port': self.config['port'],
            'db': self.config['db']
        }
        
        if not self.is_available():
            stats['fallback_mode'] = True
            stats['fallback_contexts'] = len(getattr(self, '_fallback_storage', {}))
        
        if self.is_available():
            try:
                info = self.client.info()
                stats.update({
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', 'unknown'),
                    'redis_version': info.get('redis_version', 'unknown')
                })
            except Exception as e:
                stats['info_error'] = str(e)
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on Redis connection
        
        Returns:
            Dict[str, Any]: Health check results
        """
        health_status = {
            'redis_available': HAS_REDIS,
            'client_initialized': self.initialized,
            'connection_active': self.is_available()
        }
        
        if self.is_available():
            try:
                # Test basic operations
                test_key = "xoflowers:health_check"
                test_value = "test"
                
                # Set and get test
                self.client.setex(test_key, 10, test_value)
                retrieved_value = self.client.get(test_key)
                self.client.delete(test_key)
                
                if retrieved_value == test_value:
                    health_status['status'] = 'healthy'
                    health_status['test_operations'] = 'success'
                else:
                    health_status['status'] = 'error'
                    health_status['test_operations'] = 'failed'
                    
            except Exception as e:
                health_status['status'] = 'error'
                health_status['error'] = str(e)
        else:
            health_status['status'] = 'unavailable'
            health_status['fallback_mode'] = True
        
        return health_status

# Global instance for easy access
redis_client = RedisClient()

# Convenience functions for direct access
def store_user_context(user_id: str, context_data: Dict[str, Any], ttl_hours: int = 24) -> bool:
    """Store conversation context for a user"""
    return redis_client.store_context(user_id, context_data, ttl_hours)

def get_user_context(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve conversation context for a user"""
    return redis_client.retrieve_context(user_id)

def add_conversation_message(user_id: str, user_message: str, assistant_response: str, 
                           intent: str = None, metadata: Dict[str, Any] = None) -> bool:
    """Add a message exchange to conversation context"""
    return redis_client.add_message_to_context(user_id, user_message, assistant_response, intent, metadata)

def get_conversation_history(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent conversation history for a user"""
    return redis_client.get_conversation_history(user_id, limit)

def update_user_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """Update user preferences"""
    return redis_client.update_user_preferences(user_id, preferences)

def get_user_preferences(user_id: str) -> Dict[str, Any]:
    """Get user preferences"""
    return redis_client.get_user_preferences(user_id)

def is_redis_available() -> bool:
    """Check if Redis is available"""
    return redis_client.is_available()

def health_check_redis() -> Dict[str, Any]:
    """Perform Redis health check"""
    return redis_client.health_check()

async def test_redis_connection() -> bool:
    """Test Redis connection for health checks"""
    try:
        return redis_client.is_available()
    except Exception:
        return False