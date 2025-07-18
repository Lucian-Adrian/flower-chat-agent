"""
Unit tests for Context Manager
Tests Redis-based conversation context management
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import asdict

from src.intelligence.context_manager import (
    ContextManager, ConversationContext, ConversationMessage,
    get_context_manager, get_user_context, add_conversation_message,
    get_context_for_ai, update_user_preferences
)


class TestConversationMessage:
    """Test ConversationMessage dataclass"""
    
    def test_conversation_message_creation(self):
        """Test ConversationMessage creation"""
        message = ConversationMessage(
            user="Vreau trandafiri",
            assistant="Am găsit câteva opțiuni...",
            timestamp="2025-07-16T10:30:00",
            intent="product_search",
            confidence=0.8
        )
        
        assert message.user == "Vreau trandafiri"
        assert message.assistant == "Am găsit câteva opțiuni..."
        assert message.timestamp == "2025-07-16T10:30:00"
        assert message.intent == "product_search"
        assert message.confidence == 0.8
    
    def test_conversation_message_optional_fields(self):
        """Test ConversationMessage with optional fields"""
        message = ConversationMessage(
            user="Salut",
            assistant="Bună ziua!",
            timestamp="2025-07-16T10:30:00"
        )
        
        assert message.intent is None
        assert message.confidence is None


class TestConversationContext:
    """Test ConversationContext dataclass"""
    
    def test_conversation_context_creation(self):
        """Test ConversationContext creation"""
        messages = [
            ConversationMessage(
                user="Test", 
                assistant="Response", 
                timestamp="2025-07-16T10:30:00"
            )
        ]
        
        context = ConversationContext(
            user_id="test_user",
            messages=messages,
            preferences={"budget": 500},
            last_updated="2025-07-16T10:30:00",
            total_messages=1
        )
        
        assert context.user_id == "test_user"
        assert len(context.messages) == 1
        assert context.preferences == {"budget": 500}
        assert context.total_messages == 1
    
    def test_conversation_context_to_dict(self):
        """Test ConversationContext to_dict method"""
        message = ConversationMessage(
            user="Test", 
            assistant="Response", 
            timestamp="2025-07-16T10:30:00",
            intent="test",
            confidence=0.5
        )
        
        context = ConversationContext(
            user_id="test_user",
            messages=[message],
            preferences={"budget": 500},
            last_updated="2025-07-16T10:30:00",
            total_messages=1
        )
        
        context_dict = context.to_dict()
        
        assert isinstance(context_dict, dict)
        assert context_dict['user_id'] == "test_user"
        assert len(context_dict['messages']) == 1
        assert context_dict['messages'][0]['user'] == "Test"
        assert context_dict['preferences'] == {"budget": 500}
        assert context_dict['total_messages'] == 1
    
    def test_conversation_context_from_dict(self):
        """Test ConversationContext from_dict method"""
        context_dict = {
            'user_id': 'test_user',
            'messages': [
                {
                    'user': 'Test',
                    'assistant': 'Response',
                    'timestamp': '2025-07-16T10:30:00',
                    'intent': 'test',
                    'confidence': 0.5
                }
            ],
            'preferences': {'budget': 500},
            'last_updated': '2025-07-16T10:30:00',
            'total_messages': 1
        }
        
        context = ConversationContext.from_dict(context_dict)
        
        assert context.user_id == "test_user"
        assert len(context.messages) == 1
        assert context.messages[0].user == "Test"
        assert context.messages[0].intent == "test"
        assert context.preferences == {"budget": 500}
        assert context.total_messages == 1
    
    def test_conversation_context_from_dict_missing_fields(self):
        """Test ConversationContext from_dict with missing optional fields"""
        context_dict = {
            'user_id': 'test_user',
            'last_updated': '2025-07-16T10:30:00'
        }
        
        context = ConversationContext.from_dict(context_dict)
        
        assert context.user_id == "test_user"
        assert context.messages == []
        assert context.preferences == {}
        assert context.total_messages == 0


class TestContextManager:
    """Test cases for ContextManager class"""
    
    @pytest.fixture
    def context_manager(self, mock_redis_client):
        """Create ContextManager instance for testing"""
        with patch('src.intelligence.context_manager.setup_logger'), \
             patch('src.intelligence.context_manager.get_service_config') as mock_config, \
             patch('src.intelligence.context_manager.get_performance_config') as mock_perf_config, \
             patch('redis.Redis') as mock_redis_class:
            
            mock_config.return_value = {
                'redis': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                    'decode_responses': True,
                    'socket_timeout': 5,
                    'socket_connect_timeout': 5,
                    'retry_on_timeout': True
                }
            }
            
            mock_perf_config.return_value = {
                'max_conversation_history': 10,
                'context_cleanup_interval_hours': 24
            }
            
            mock_redis_class.return_value = mock_redis_client
            
            manager = ContextManager()
            manager.logger = Mock()
            return manager
    
    def test_context_manager_initialization_redis_success(self, mock_redis_client):
        """Test ContextManager initialization with Redis success"""
        with patch('src.intelligence.context_manager.setup_logger'), \
             patch('src.intelligence.context_manager.get_service_config') as mock_config, \
             patch('src.intelligence.context_manager.get_performance_config') as mock_perf_config, \
             patch('redis.Redis') as mock_redis_class:
            
            mock_config.return_value = {
                'redis': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                    'decode_responses': True,
                    'socket_timeout': 5,
                    'socket_connect_timeout': 5,
                    'retry_on_timeout': True
                }
            }
            
            mock_perf_config.return_value = {
                'max_conversation_history': 10,
                'context_cleanup_interval_hours': 24
            }
            
            mock_redis_class.return_value = mock_redis_client
            mock_redis_client.ping.return_value = True
            
            manager = ContextManager()
            
            assert manager.redis_available is True
            assert manager.max_messages == 10
            assert manager.cleanup_interval == 24
    
    def test_context_manager_initialization_redis_failure(self):
        """Test ContextManager initialization with Redis failure"""
        with patch('src.intelligence.context_manager.setup_logger'), \
             patch('src.intelligence.context_manager.get_service_config') as mock_config, \
             patch('src.intelligence.context_manager.get_performance_config') as mock_perf_config, \
             patch('redis.Redis') as mock_redis_class:
            
            mock_config.return_value = {
                'redis': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                    'decode_responses': True,
                    'socket_timeout': 5,
                    'socket_connect_timeout': 5,
                    'retry_on_timeout': True
                }
            }
            
            mock_perf_config.return_value = {
                'max_conversation_history': 10,
                'context_cleanup_interval_hours': 24
            }
            
            mock_redis_instance = Mock()
            mock_redis_instance.ping.side_effect = Exception("Connection failed")
            mock_redis_class.return_value = mock_redis_instance
            
            manager = ContextManager()
            
            assert manager.redis_available is False
            assert manager.redis_client is None
    
    def test_get_context_key(self, context_manager):
        """Test context key generation"""
        key = context_manager._get_context_key("user_123")
        assert key == "xoflowers:context:user_123"
    
    @pytest.mark.asyncio
    async def test_get_context_success(self, context_manager, sample_conversation_context):
        """Test successful context retrieval"""
        context_manager.redis_available = True
        context_json = json.dumps({
            'user_id': 'test_user_123',
            'messages': [
                {
                    'user': 'Salut! Vreau trandafiri roșii',
                    'assistant': 'Bună! Am câteva opțiuni frumoase...',
                    'timestamp': '2025-07-16T10:30:00',
                    'intent': 'product_search',
                    'confidence': 0.8
                }
            ],
            'preferences': {'budget_range': [200, 800]},
            'last_updated': '2025-07-16T10:30:00',
            'total_messages': 1
        })
        
        context_manager.redis_client.get.return_value = context_json
        
        result = await context_manager.get_context("test_user_123")
        
        assert result is not None
        assert result.user_id == "test_user_123"
        assert len(result.messages) == 1
        assert result.messages[0].user == "Salut! Vreau trandafiri roșii"
        assert result.preferences == {'budget_range': [200, 800]}
        context_manager.redis_client.get.assert_called_once_with("xoflowers:context:test_user_123")
    
    @pytest.mark.asyncio
    async def test_get_context_not_found(self, context_manager):
        """Test context retrieval when context not found"""
        context_manager.redis_available = True
        context_manager.redis_client.get.return_value = None
        
        result = await context_manager.get_context("test_user_123")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_context_redis_unavailable(self, context_manager):
        """Test context retrieval when Redis is unavailable"""
        context_manager.redis_available = False
        
        result = await context_manager.get_context("test_user_123")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_context_redis_error(self, context_manager):
        """Test context retrieval with Redis error"""
        context_manager.redis_available = True
        context_manager.redis_client.get.side_effect = Exception("Redis error")
        
        result = await context_manager.get_context("test_user_123")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_save_context_success(self, context_manager):
        """Test successful context saving"""
        context_manager.redis_available = True
        
        message = ConversationMessage(
            user="Test",
            assistant="Response",
            timestamp="2025-07-16T10:30:00"
        )
        
        context = ConversationContext(
            user_id="test_user",
            messages=[message],
            preferences={},
            last_updated="2025-07-16T10:30:00",
            total_messages=1
        )
        
        result = await context_manager.save_context(context, ttl_hours=24)
        
        assert result is True
        context_manager.redis_client.setex.assert_called_once()
        
        # Check the call arguments
        call_args = context_manager.redis_client.setex.call_args
        assert call_args[0][0] == "xoflowers:context:test_user"  # key
        assert call_args[0][1] == 24 * 3600  # TTL in seconds
        
        # Check that JSON was properly formatted
        saved_json = call_args[0][2]
        saved_data = json.loads(saved_json)
        assert saved_data['user_id'] == "test_user"
        assert len(saved_data['messages']) == 1
    
    @pytest.mark.asyncio
    async def test_save_context_redis_unavailable(self, context_manager):
        """Test context saving when Redis is unavailable"""
        context_manager.redis_available = False
        
        context = ConversationContext(
            user_id="test_user",
            messages=[],
            preferences={},
            last_updated="2025-07-16T10:30:00",
            total_messages=0
        )
        
        result = await context_manager.save_context(context)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_save_context_redis_error(self, context_manager):
        """Test context saving with Redis error"""
        context_manager.redis_available = True
        context_manager.redis_client.setex.side_effect = Exception("Redis error")
        
        context = ConversationContext(
            user_id="test_user",
            messages=[],
            preferences={},
            last_updated="2025-07-16T10:30:00",
            total_messages=0
        )
        
        result = await context_manager.save_context(context)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_add_message_new_context(self, context_manager):
        """Test adding message to new context"""
        context_manager.redis_available = True
        
        # Mock get_context to return None (new user)
        with patch.object(context_manager, 'get_context') as mock_get, \
             patch.object(context_manager, 'save_context') as mock_save:
            
            mock_get.return_value = None
            mock_save.return_value = True
            
            result = await context_manager.add_message(
                "test_user",
                "Vreau trandafiri",
                "Am găsit câteva opțiuni...",
                "product_search",
                0.8
            )
            
            assert result is True
            mock_save.assert_called_once()
            
            # Check the saved context
            saved_context = mock_save.call_args[0][0]
            assert saved_context.user_id == "test_user"
            assert len(saved_context.messages) == 1
            assert saved_context.messages[0].user == "Vreau trandafiri"
            assert saved_context.messages[0].assistant == "Am găsit câteva opțiuni..."
            assert saved_context.messages[0].intent == "product_search"
            assert saved_context.messages[0].confidence == 0.8
            assert saved_context.total_messages == 1
    
    @pytest.mark.asyncio
    async def test_add_message_existing_context(self, context_manager):
        """Test adding message to existing context"""
        context_manager.redis_available = True
        
        # Create existing context
        existing_message = ConversationMessage(
            user="Salut",
            assistant="Bună ziua!",
            timestamp="2025-07-16T10:00:00"
        )
        
        existing_context = ConversationContext(
            user_id="test_user",
            messages=[existing_message],
            preferences={"budget": 500},
            last_updated="2025-07-16T10:00:00",
            total_messages=1
        )
        
        with patch.object(context_manager, 'get_context') as mock_get, \
             patch.object(context_manager, 'save_context') as mock_save:
            
            mock_get.return_value = existing_context
            mock_save.return_value = True
            
            result = await context_manager.add_message(
                "test_user",
                "Vreau trandafiri",
                "Am găsit câteva opțiuni...",
                "product_search",
                0.8
            )
            
            assert result is True
            
            # Check the saved context
            saved_context = mock_save.call_args[0][0]
            assert len(saved_context.messages) == 2
            assert saved_context.messages[1].user == "Vreau trandafiri"
            assert saved_context.total_messages == 2
            assert saved_context.preferences == {"budget": 500}  # Preserved
    
    def test_compress_context_no_compression_needed(self, context_manager):
        """Test context compression when no compression is needed"""
        messages = [
            ConversationMessage(f"Message {i}", f"Response {i}", "2025-07-16T10:30:00")
            for i in range(5)
        ]
        
        context = ConversationContext(
            user_id="test_user",
            messages=messages,
            preferences={},
            last_updated="2025-07-16T10:30:00",
            total_messages=5
        )
        
        compressed = context_manager._compress_context(context)
        
        assert len(compressed.messages) == 5  # No compression needed
        assert compressed.messages == messages
    
    def test_compress_context_compression_needed(self, context_manager):
        """Test context compression when compression is needed"""
        context_manager.max_messages = 3
        
        messages = [
            ConversationMessage(f"Message {i}", f"Response {i}", "2025-07-16T10:30:00")
            for i in range(5)
        ]
        
        context = ConversationContext(
            user_id="test_user",
            messages=messages,
            preferences={},
            last_updated="2025-07-16T10:30:00",
            total_messages=5
        )
        
        compressed = context_manager._compress_context(context)
        
        assert len(compressed.messages) == 3  # Compressed to max_messages
        assert compressed.messages[0].user == "Message 2"  # Kept last 3 messages
        assert compressed.messages[2].user == "Message 4"
    
    @pytest.mark.asyncio
    async def test_update_preferences_new_context(self, context_manager):
        """Test updating preferences for new user"""
        with patch.object(context_manager, 'get_context') as mock_get, \
             patch.object(context_manager, 'save_context') as mock_save:
            
            mock_get.return_value = None
            mock_save.return_value = True
            
            result = await context_manager.update_preferences(
                "test_user",
                {"budget": 500, "color": "red"}
            )
            
            assert result is True
            
            # Check saved context
            saved_context = mock_save.call_args[0][0]
            assert saved_context.user_id == "test_user"
            assert saved_context.preferences == {"budget": 500, "color": "red"}
            assert len(saved_context.messages) == 0
    
    @pytest.mark.asyncio
    async def test_update_preferences_existing_context(self, context_manager):
        """Test updating preferences for existing user"""
        existing_context = ConversationContext(
            user_id="test_user",
            messages=[],
            preferences={"budget": 300, "occasion": "birthday"},
            last_updated="2025-07-16T10:00:00",
            total_messages=0
        )
        
        with patch.object(context_manager, 'get_context') as mock_get, \
             patch.object(context_manager, 'save_context') as mock_save:
            
            mock_get.return_value = existing_context
            mock_save.return_value = True
            
            result = await context_manager.update_preferences(
                "test_user",
                {"budget": 500, "color": "red"}  # budget will be updated, color added
            )
            
            assert result is True
            
            # Check saved context
            saved_context = mock_save.call_args[0][0]
            expected_preferences = {
                "budget": 500,  # Updated
                "occasion": "birthday",  # Preserved
                "color": "red"  # Added
            }
            assert saved_context.preferences == expected_preferences
    
    @pytest.mark.asyncio
    async def test_get_recent_messages_success(self, context_manager):
        """Test getting recent messages"""
        messages = [
            ConversationMessage(f"Message {i}", f"Response {i}", "2025-07-16T10:30:00")
            for i in range(10)
        ]
        
        context = ConversationContext(
            user_id="test_user",
            messages=messages,
            preferences={},
            last_updated="2025-07-16T10:30:00",
            total_messages=10
        )
        
        with patch.object(context_manager, 'get_context') as mock_get:
            mock_get.return_value = context
            
            result = await context_manager.get_recent_messages("test_user", count=3)
            
            assert len(result) == 3
            assert result[0].user == "Message 7"  # Last 3 messages
            assert result[2].user == "Message 9"
    
    @pytest.mark.asyncio
    async def test_get_recent_messages_no_context(self, context_manager):
        """Test getting recent messages when no context exists"""
        with patch.object(context_manager, 'get_context') as mock_get:
            mock_get.return_value = None
            
            result = await context_manager.get_recent_messages("test_user")
            
            assert result == []
    
    @pytest.mark.asyncio
    async def test_clear_context_success(self, context_manager):
        """Test successful context clearing"""
        context_manager.redis_available = True
        context_manager.redis_client.delete.return_value = 1
        
        result = await context_manager.clear_context("test_user")
        
        assert result is True
        context_manager.redis_client.delete.assert_called_once_with("xoflowers:context:test_user")
    
    @pytest.mark.asyncio
    async def test_clear_context_redis_unavailable(self, context_manager):
        """Test context clearing when Redis is unavailable"""
        context_manager.redis_available = False
        
        result = await context_manager.clear_context("test_user")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup_old_contexts_success(self, context_manager):
        """Test successful cleanup of old contexts"""
        context_manager.redis_available = True
        context_manager.cleanup_interval = 24
        
        # Mock Redis keys and data
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        recent_time = datetime.now().isoformat()
        
        context_manager.redis_client.keys.return_value = [
            "xoflowers:context:user1",
            "xoflowers:context:user2",
            "xoflowers:context:user3"
        ]
        
        # Mock get responses - user1 and user3 are old, user2 is recent
        def mock_get(key):
            if key == "xoflowers:context:user1":
                return json.dumps({"last_updated": old_time})
            elif key == "xoflowers:context:user2":
                return json.dumps({"last_updated": recent_time})
            elif key == "xoflowers:context:user3":
                return json.dumps({"last_updated": old_time})
            return None
        
        context_manager.redis_client.get.side_effect = mock_get
        context_manager.redis_client.delete.return_value = 1
        
        result = await context_manager.cleanup_old_contexts()
        
        assert result == 2  # Should clean up 2 old contexts
        assert context_manager.redis_client.delete.call_count == 2
    
    @pytest.mark.asyncio
    async def test_cleanup_old_contexts_redis_unavailable(self, context_manager):
        """Test cleanup when Redis is unavailable"""
        context_manager.redis_available = False
        
        result = await context_manager.cleanup_old_contexts()
        
        assert result == 0
    
    def test_get_context_summary_with_context(self, context_manager):
        """Test context summary generation with context"""
        messages = [
            ConversationMessage(f"Message {i}", f"Response {i}", "2025-07-16T10:30:00", f"intent_{i}", 0.8)
            for i in range(5)
        ]
        
        context = ConversationContext(
            user_id="test_user",
            messages=messages,
            preferences={"budget": 500},
            last_updated="2025-07-16T10:30:00",
            total_messages=5
        )
        
        summary = context_manager.get_context_summary(context)
        
        assert len(summary['recent_messages']) == 3  # Last 3 messages
        assert summary['preferences'] == {"budget": 500}
        assert summary['total_messages'] == 5
        assert summary['conversation_started'] == "2025-07-16T10:30:00"
        
        # Check recent messages structure
        assert summary['recent_messages'][0]['user'] == "Message 2"
        assert summary['recent_messages'][0]['intent'] == "intent_2"
        assert summary['recent_messages'][2]['user'] == "Message 4"
    
    def test_get_context_summary_empty_context(self, context_manager):
        """Test context summary generation with empty context"""
        summary = context_manager.get_context_summary(None)
        assert summary == {}
        
        empty_context = ConversationContext(
            user_id="test_user",
            messages=[],
            preferences={},
            last_updated="2025-07-16T10:30:00",
            total_messages=0
        )
        
        summary = context_manager.get_context_summary(empty_context)
        assert summary == {}


class TestContextManagerGlobalFunctions:
    """Test global functions and singleton pattern"""
    
    def test_get_context_manager_singleton(self):
        """Test that get_context_manager returns singleton instance"""
        with patch('src.intelligence.context_manager.ContextManager') as mock_manager_class:
            mock_instance = Mock()
            mock_manager_class.return_value = mock_instance
            
            # Clear the global instance
            import src.intelligence.context_manager
            src.intelligence.context_manager._context_manager = None
            
            # First call should create instance
            manager1 = get_context_manager()
            assert manager1 == mock_instance
            mock_manager_class.assert_called_once()
            
            # Second call should return same instance
            manager2 = get_context_manager()
            assert manager2 == mock_instance
            assert manager1 is manager2
    
    @pytest.mark.asyncio
    async def test_get_user_context_function(self):
        """Test global get_user_context function"""
        with patch('src.intelligence.context_manager.get_context_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_context = Mock()
            mock_manager.get_context = AsyncMock(return_value=mock_context)
            mock_get_manager.return_value = mock_manager
            
            result = await get_user_context("test_user")
            
            assert result == mock_context
            mock_manager.get_context.assert_called_once_with("test_user")
    
    @pytest.mark.asyncio
    async def test_add_conversation_message_function(self):
        """Test global add_conversation_message function"""
        with patch('src.intelligence.context_manager.get_context_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.add_message = AsyncMock(return_value=True)
            mock_get_manager.return_value = mock_manager
            
            result = await add_conversation_message(
                "test_user", "message", "response", "intent", 0.8
            )
            
            assert result is True
            mock_manager.add_message.assert_called_once_with(
                "test_user", "message", "response", "intent", 0.8
            )
    
    @pytest.mark.asyncio
    async def test_get_context_for_ai_function(self):
        """Test global get_context_for_ai function"""
        with patch('src.intelligence.context_manager.get_context_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_context = Mock()
            mock_manager.get_context = AsyncMock(return_value=mock_context)
            mock_manager.get_context_summary.return_value = {"summary": "data"}
            mock_get_manager.return_value = mock_manager
            
            result = await get_context_for_ai("test_user")
            
            assert result == {"summary": "data"}
            mock_manager.get_context.assert_called_once_with("test_user")
            mock_manager.get_context_summary.assert_called_once_with(mock_context)
    
    @pytest.mark.asyncio
    async def test_get_context_for_ai_function_no_context(self):
        """Test global get_context_for_ai function with no context"""
        with patch('src.intelligence.context_manager.get_context_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.get_context = AsyncMock(return_value=None)
            mock_manager.get_context_summary.return_value = {}
            mock_get_manager.return_value = mock_manager
            
            result = await get_context_for_ai("test_user")
            
            assert result == {}
    
    @pytest.mark.asyncio
    async def test_update_user_preferences_function(self):
        """Test global update_user_preferences function"""
        with patch('src.intelligence.context_manager.get_context_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.update_preferences = AsyncMock(return_value=True)
            mock_get_manager.return_value = mock_manager
            
            result = await update_user_preferences("test_user", {"budget": 500})
            
            assert result is True
            mock_manager.update_preferences.assert_called_once_with("test_user", {"budget": 500})