"""
Gemini Chat-based Context Management for XOFlowers AI Agent
Uses Gemini's built-in chat functionality for conversation context with Redis fallback
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import google.generativeai as genai

from src.utils.system_definitions import get_service_config, get_ai_prompts
from src.utils.utils import setup_logger, log_performance_metrics
from .context_manager import ContextManager, get_context_manager


@dataclass
class GeminiChatSession:
    """Gemini chat session wrapper for new API"""
    user_id: str
    chat_session: Any  # Gemini chat session object
    message_count: int
    created_at: str
    last_used: str


class GeminiChatManager:
    """
    Enhanced context management using Gemini's built-in chat functionality
    Falls back to Redis-based context when needed
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.service_config = get_service_config()
        self.ai_prompts = get_ai_prompts()
        
        # Initialize Gemini client
        self.gemini_client = None
        self.gemini_available = self._setup_gemini()
        
        # Chat session storage (in-memory with Redis backup)
        self.active_chats: Dict[str, GeminiChatSession] = {}
        self.max_active_chats = 100  # Limit memory usage
        
        # Fallback to Redis-based context manager
        self.redis_context_manager = get_context_manager()
        
        self.logger.info(f"Gemini Chat Manager initialized (Gemini available: {self.gemini_available})")
    
    def _setup_gemini(self) -> bool:
        """Initialize Gemini client using working API"""
        try:
            gemini_config = self.service_config['gemini']
            
            if gemini_config['api_key']:
                genai.configure(api_key=gemini_config['api_key'])
                self.gemini_model = genai.GenerativeModel(
                    model_name=gemini_config['model'],
                    system_instruction=self.ai_prompts['main_system_prompt']
                )
                self.logger.info("Gemini client configured for chat management")
                return True
            else:
                self.logger.warning("Gemini API key not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini for chat: {e}")
            return False
    
    async def get_or_create_chat(self, user_id: str) -> Optional[Any]:
        """
        Get existing chat session or create new one for user using new API
        
        Args:
            user_id: User identifier
            
        Returns:
            Gemini chat session object or None if unavailable
        """
        if not self.gemini_available or not self.gemini_model:
            return None
        
        # Check if we have an active chat session
        if user_id in self.active_chats:
            session = self.active_chats[user_id]
            session.last_used = datetime.now().isoformat()
            self.logger.debug(f"Using existing chat session for user {user_id}")
            return session.chat_session
        
        # Create new chat session using working API
        try:
            # Create chat session - the model already has system instructions
            chat_session = self.gemini_model.start_chat(history=[])
            
            # Store chat session
            session = GeminiChatSession(
                user_id=user_id,
                chat_session=chat_session,
                message_count=0,
                created_at=datetime.now().isoformat(),
                last_used=datetime.now().isoformat()
            )
            
            self.active_chats[user_id] = session
            
            # Clean up old sessions if we have too many
            if len(self.active_chats) > self.max_active_chats:
                self._cleanup_old_sessions()
            
            self.logger.info(f"Created new Gemini chat session for user {user_id}")
            return chat_session
            
        except Exception as e:
            self.logger.error(f"Failed to create Gemini chat session for user {user_id}: {e}")
            return None
    
    async def send_message_with_context(self, user_id: str, message: str) -> Optional[str]:
        """
        Send message using Gemini chat with full conversation context
        
        Args:
            user_id: User identifier
            message: User message
            
        Returns:
            AI response or None if failed
        """
        start_time = time.time()
        
        try:
            chat_session = await self.get_or_create_chat(user_id)
            
            if chat_session is None:
                # Fallback to Redis-based context
                self.logger.debug(f"Gemini chat unavailable, falling back to Redis context for user {user_id}")
                return None
            
            # Send message to chat using working API
            response = await asyncio.to_thread(
                chat_session.send_message,
                message
            )
            
            # Update session info
            if user_id in self.active_chats:
                self.active_chats[user_id].message_count += 1
                self.active_chats[user_id].last_used = datetime.now().isoformat()
            
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "gemini_chat_message", duration, True, 
                                  {"user_id": user_id, "message_length": len(message)})
            
            # Extract response text
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    response_text = candidate.content.parts[0].text
                    self.logger.debug(f"Gemini chat response for user {user_id} in {duration:.2f}s")
                    return response_text.strip()
            
            self.logger.warning(f"No valid response from Gemini chat for user {user_id}")
            return None
            
        except Exception as e:
            duration = time.time() - start_time
            log_performance_metrics(self.logger, "gemini_chat_message", duration, False, 
                                  {"error": str(e), "user_id": user_id})
            self.logger.error(f"Gemini chat message failed for user {user_id}: {e}")
            return None
    
    async def get_conversation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history from Gemini chat
        
        Args:
            user_id: User identifier
            
        Returns:
            List of conversation messages
        """
        if not self.gemini_available or user_id not in self.active_chats:
            # Fallback to Redis context
            redis_context = await self.redis_context_manager.get_context(user_id)
            if redis_context:
                return [
                    {
                        "role": "user",
                        "content": msg.user,
                        "timestamp": msg.timestamp
                    }
                    for msg in redis_context.messages[-5:]  # Last 5 messages
                ]
            return []
        
        try:
            chat = self.active_chats[user_id].chat
            history = []
            
            # Get chat history
            for message in chat.get_history():
                history.append({
                    "role": message.role,
                    "content": message.parts[0].text if message.parts else "",
                    "timestamp": datetime.now().isoformat()  # Gemini doesn't provide timestamps
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation history for user {user_id}: {e}")
            return []
    
    async def clear_conversation(self, user_id: str) -> bool:
        """
        Clear conversation for user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if cleared successfully
        """
        try:
            # Remove from active chats
            if user_id in self.active_chats:
                del self.active_chats[user_id]
                self.logger.info(f"Cleared Gemini chat session for user {user_id}")
            
            # Also clear Redis context as backup
            await self.redis_context_manager.clear_context(user_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clear conversation for user {user_id}: {e}")
            return False
    
    def _cleanup_old_sessions(self) -> None:
        """Clean up old chat sessions to manage memory"""
        try:
            # Sort sessions by last used time
            sessions_by_time = sorted(
                self.active_chats.items(),
                key=lambda x: x[1].last_used
            )
            
            # Remove oldest 20% of sessions
            cleanup_count = len(sessions_by_time) // 5
            
            for user_id, _ in sessions_by_time[:cleanup_count]:
                del self.active_chats[user_id]
                self.logger.debug(f"Cleaned up old chat session for user {user_id}")
            
            self.logger.info(f"Cleaned up {cleanup_count} old chat sessions")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old sessions: {e}")
    
    async def backup_to_redis(self, user_id: str) -> bool:
        """
        Backup current conversation to Redis for persistence
        
        Args:
            user_id: User identifier
            
        Returns:
            True if backup successful
        """
        if user_id not in self.active_chats:
            return False
        
        try:
            # Get conversation history
            history = await self.get_conversation_history(user_id)
            
            if not history:
                return False
            
            # Convert to Redis format and save
            for i in range(0, len(history) - 1, 2):  # Process pairs of user/assistant messages
                if i + 1 < len(history):
                    user_msg = history[i]
                    assistant_msg = history[i + 1]
                    
                    if user_msg['role'] == 'user' and assistant_msg['role'] == 'model':
                        await self.redis_context_manager.add_message(
                            user_id,
                            user_msg['content'],
                            assistant_msg['content']
                        )
            
            self.logger.debug(f"Backed up conversation to Redis for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup conversation to Redis for user {user_id}: {e}")
            return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about active chat sessions"""
        return {
            "active_sessions": len(self.active_chats),
            "max_sessions": self.max_active_chats,
            "gemini_available": self.gemini_available,
            "total_messages": sum(session.message_count for session in self.active_chats.values())
        }


# Global Gemini chat manager instance
_gemini_chat_manager = None

def get_gemini_chat_manager() -> GeminiChatManager:
    """Get global Gemini chat manager instance"""
    global _gemini_chat_manager
    if _gemini_chat_manager is None:
        _gemini_chat_manager = GeminiChatManager()
    return _gemini_chat_manager


# Enhanced context functions that use Gemini chat first, Redis as fallback
async def get_enhanced_context_for_ai(user_id: str) -> Dict[str, Any]:
    """
    Get conversation context using Gemini chat with Redis fallback
    
    Args:
        user_id: User identifier
        
    Returns:
        Enhanced context for AI processing
    """
    gemini_manager = get_gemini_chat_manager()
    
    # Try to get context from Gemini chat first
    if gemini_manager.gemini_available and user_id in gemini_manager.active_chats:
        try:
            history = await gemini_manager.get_conversation_history(user_id)
            
            if history:
                return {
                    "recent_messages": history[-6:],  # Last 6 messages (3 exchanges)
                    "conversation_type": "gemini_chat",
                    "total_messages": len(history),
                    "session_active": True
                }
        except Exception as e:
            gemini_manager.logger.warning(f"Failed to get Gemini context, falling back to Redis: {e}")
    
    # Fallback to Redis-based context
    from .context_manager import get_context_for_ai
    redis_context = await get_context_for_ai(user_id)
    
    if redis_context:
        redis_context["conversation_type"] = "redis_fallback"
        redis_context["session_active"] = False
        return redis_context
    
    # No context available
    return {
        "recent_messages": [],
        "conversation_type": "none",
        "total_messages": 0,
        "session_active": False
    }


async def send_message_with_enhanced_context(user_id: str, message: str) -> Optional[str]:
    """
    Send message using enhanced context management (Gemini chat + Redis fallback)
    
    Args:
        user_id: User identifier
        message: User message
        
    Returns:
        AI response or None if failed
    """
    gemini_manager = get_gemini_chat_manager()
    
    # Try Gemini chat first
    response = await gemini_manager.send_message_with_context(user_id, message)
    
    if response:
        # Optionally backup to Redis for persistence
        await gemini_manager.backup_to_redis(user_id)
        return response
    
    # If Gemini chat fails, we'll handle this in the main AI engine
    return None