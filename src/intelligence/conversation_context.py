"""
Conversation Context Management for XOFlowers Conversational AI
Simplified and effective context tracking for natural conversations
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Single message in conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary"""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )


@dataclass
class UserPreferences:
    """User preferences extracted from conversations"""
    favorite_colors: List[str] = None
    favorite_flowers: List[str] = None
    budget_range: Optional[tuple] = None
    preferred_occasions: List[str] = None
    style_preferences: List[str] = None
    recipient_types: List[str] = None
    
    def __post_init__(self):
        if self.favorite_colors is None:
            self.favorite_colors = []
        if self.favorite_flowers is None:
            self.favorite_flowers = []
        if self.preferred_occasions is None:
            self.preferred_occasions = []
        if self.style_preferences is None:
            self.style_preferences = []
        if self.recipient_types is None:
            self.recipient_types = []
    
    def update_from_message(self, message: str, search_intent: Optional[Any] = None):
        """Update preferences based on user message and search intent"""
        message_lower = message.lower()
        
        # Extract colors
        color_keywords = {
            'roșu': ['roșu', 'rosu', 'red'],
            'roz': ['roz', 'pink'],
            'alb': ['alb', 'white'],
            'galben': ['galben', 'yellow'],
            'violet': ['violet', 'purple']
        }
        
        for color, keywords in color_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if color not in self.favorite_colors:
                    self.favorite_colors.append(color)
        
        # Extract flower types
        flower_keywords = ['trandafir', 'bujor', 'lalele', 'crizanteme']
        for flower in flower_keywords:
            if flower in message_lower and flower not in self.favorite_flowers:
                self.favorite_flowers.append(flower)
        
        # Extract style preferences
        style_keywords = {
            'elegant': ['elegant', 'rafinat'],
            'romantic': ['romantic', 'tandru'],
            'modern': ['modern', 'contemporan'],
            'classic': ['clasic', 'tradițional']
        }
        
        for style, keywords in style_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                if style not in self.style_preferences:
                    self.style_preferences.append(style)
        
        # Update from search intent if provided
        if search_intent:
            if hasattr(search_intent, 'colors') and search_intent.colors:
                for color in search_intent.colors:
                    if color not in self.favorite_colors:
                        self.favorite_colors.append(color)
            
            if hasattr(search_intent, 'budget_min') and hasattr(search_intent, 'budget_max'):
                if search_intent.budget_min or search_intent.budget_max:
                    self.budget_range = (search_intent.budget_min, search_intent.budget_max)


@dataclass
class ConversationSession:
    """Current conversation session state"""
    user_id: str
    messages: List[Message]
    preferences: UserPreferences
    current_search_context: Optional[Dict[str, Any]] = None
    mentioned_products: List[str] = None
    conversation_stage: str = 'greeting'  # greeting, exploring, deciding, ordering
    last_activity: datetime = None
    
    def __post_init__(self):
        if self.mentioned_products is None:
            self.mentioned_products = []
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation"""
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )
        self.messages.append(message)
        self.last_activity = datetime.now()
        
        # Update preferences if it's a user message
        if role == 'user':
            self.preferences.update_from_message(content)
    
    def get_recent_messages(self, limit: int = 10) -> List[Message]:
        """Get recent messages for context"""
        return self.messages[-limit:] if self.messages else []
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation for AI context"""
        if not self.messages:
            return "No previous conversation."
        
        recent_messages = self.get_recent_messages(6)
        summary_parts = []
        
        for msg in recent_messages:
            role_label = "Client" if msg.role == 'user' else "XOFlowers"
            summary_parts.append(f"{role_label}: {msg.content}")
        
        return "\n".join(summary_parts)
    
    def is_active(self, timeout_minutes: int = 30) -> bool:
        """Check if conversation is still active"""
        if not self.last_activity:
            return False
        
        timeout = timedelta(minutes=timeout_minutes)
        return datetime.now() - self.last_activity < timeout


class ConversationContextManager:
    """
    Manages conversation contexts for all users
    Simplified and focused on natural conversation flow
    """
    
    def __init__(self, storage_path: str = "data"):
        """
        Initialize conversation context manager
        
        Args:
            storage_path: Path to store conversation data
        """
        self.storage_path = storage_path
        self.active_sessions: Dict[str, ConversationSession] = {}
        
        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)
        
        # Load existing sessions
        self._load_sessions()
    
    def get_or_create_session(self, user_id: str) -> ConversationSession:
        """Get existing session or create new one"""
        if user_id not in self.active_sessions:
            # Try to load from storage
            session = self._load_session(user_id)
            if not session or not session.is_active():
                # Create new session
                session = ConversationSession(
                    user_id=user_id,
                    messages=[],
                    preferences=UserPreferences()
                )
            
            self.active_sessions[user_id] = session
        
        return self.active_sessions[user_id]
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to user's conversation"""
        session = self.get_or_create_session(user_id)
        session.add_message(role, content, metadata)
        
        # Save session
        self._save_session(session)
    
    def get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get conversation context for AI"""
        session = self.get_or_create_session(user_id)
        
        return {
            'user_id': user_id,
            'conversation_summary': session.get_conversation_summary(),
            'preferences': asdict(session.preferences),
            'mentioned_products': session.mentioned_products,
            'conversation_stage': session.conversation_stage,
            'is_returning_user': len(session.messages) > 2,
            'recent_messages': [msg.to_dict() for msg in session.get_recent_messages(5)]
        }
    
    def update_search_context(self, user_id: str, search_intent: Any, results: List[Any]):
        """Update search context after a product search"""
        session = self.get_or_create_session(user_id)
        
        session.current_search_context = {
            'search_intent': str(search_intent),
            'results_count': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add product IDs to mentioned products
        for result in results:
            if hasattr(result, 'product') and 'id' in result.product:
                product_id = result.product['id']
                if product_id not in session.mentioned_products:
                    session.mentioned_products.append(product_id)
        
        # Update conversation stage
        if session.conversation_stage == 'greeting':
            session.conversation_stage = 'exploring'
        
        self._save_session(session)
    
    def get_personalized_greeting(self, user_id: str) -> str:
        """Get personalized greeting based on user history"""
        session = self.get_or_create_session(user_id)
        
        if len(session.messages) == 0:
            return "🌸 Bună ziua! Bine ați venit la XOFlowers! Sunt aici să vă ajut să găsiți florile perfecte pentru orice ocazie."
        
        if len(session.messages) < 5:
            return "🌸 Bună ziua din nou! Mă bucur să vă revăd la XOFlowers! Cu ce vă pot ajuta astăzi?"
        
        # Personalized greeting based on preferences
        greeting = "🌸 Bună ziua! Îmi pare bine să vă revăd!"
        
        if session.preferences.favorite_colors:
            colors = ", ".join(session.preferences.favorite_colors[:2])
            greeting += f" Văd că vă plac florile în {colors}."
        
        if session.preferences.favorite_flowers:
            flowers = ", ".join(session.preferences.favorite_flowers[:2])
            greeting += f" Și știu că apreciați {flowers}."
        
        greeting += " Cu ce vă pot ajuta astăzi?"
        
        return greeting
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = 60):
        """Remove inactive sessions from memory"""
        inactive_users = []
        
        for user_id, session in self.active_sessions.items():
            if not session.is_active(timeout_minutes):
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            # Save before removing
            self._save_session(self.active_sessions[user_id])
            del self.active_sessions[user_id]
        
        if inactive_users:
            logger.info(f"🧹 Cleaned up {len(inactive_users)} inactive sessions")
    
    def _load_sessions(self):
        """Load active sessions from storage"""
        try:
            sessions_file = os.path.join(self.storage_path, "active_sessions.json")
            if os.path.exists(sessions_file):
                with open(sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for user_id, session_data in data.items():
                    session = self._deserialize_session(session_data)
                    if session and session.is_active():
                        self.active_sessions[user_id] = session
                
                logger.info(f"✅ Loaded {len(self.active_sessions)} active sessions")
        except Exception as e:
            logger.warning(f"⚠️ Error loading sessions: {e}")
    
    def _save_session(self, session: ConversationSession):
        """Save individual session"""
        try:
            user_file = os.path.join(self.storage_path, f"user_{session.user_id}.json")
            session_data = self._serialize_session(session)
            
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.warning(f"⚠️ Error saving session for {session.user_id}: {e}")
    
    def _load_session(self, user_id: str) -> Optional[ConversationSession]:
        """Load individual session"""
        try:
            user_file = os.path.join(self.storage_path, f"user_{user_id}.json")
            if os.path.exists(user_file):
                with open(user_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    return self._deserialize_session(session_data)
        except Exception as e:
            logger.warning(f"⚠️ Error loading session for {user_id}: {e}")
        
        return None
    
    def _serialize_session(self, session: ConversationSession) -> Dict[str, Any]:
        """Convert session to JSON-serializable format"""
        return {
            'user_id': session.user_id,
            'messages': [msg.to_dict() for msg in session.messages],
            'preferences': asdict(session.preferences),
            'current_search_context': session.current_search_context,
            'mentioned_products': session.mentioned_products,
            'conversation_stage': session.conversation_stage,
            'last_activity': session.last_activity.isoformat()
        }
    
    def _deserialize_session(self, data: Dict[str, Any]) -> Optional[ConversationSession]:
        """Convert JSON data back to session"""
        try:
            messages = [Message.from_dict(msg_data) for msg_data in data.get('messages', [])]
            
            preferences_data = data.get('preferences', {})
            preferences = UserPreferences(
                favorite_colors=preferences_data.get('favorite_colors', []),
                favorite_flowers=preferences_data.get('favorite_flowers', []),
                budget_range=tuple(preferences_data['budget_range']) if preferences_data.get('budget_range') else None,
                preferred_occasions=preferences_data.get('preferred_occasions', []),
                style_preferences=preferences_data.get('style_preferences', []),
                recipient_types=preferences_data.get('recipient_types', [])
            )
            
            return ConversationSession(
                user_id=data['user_id'],
                messages=messages,
                preferences=preferences,
                current_search_context=data.get('current_search_context'),
                mentioned_products=data.get('mentioned_products', []),
                conversation_stage=data.get('conversation_stage', 'greeting'),
                last_activity=datetime.fromisoformat(data['last_activity'])
            )
        except Exception as e:
            logger.warning(f"⚠️ Error deserializing session: {e}")
            return None


# Global context manager instance
_context_manager = None

def get_context_manager() -> ConversationContextManager:
    """Get the global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ConversationContextManager()
    return _context_manager