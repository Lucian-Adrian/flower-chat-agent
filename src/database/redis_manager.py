

import json
import time
import redis
from typing import Any, Dict, Optional
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

class RedisManager:
    redis_client: redis.Redis

    def __init__(self) -> None:
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD
        )

    def store_conversation_context(self, user_id: str, context_data: Dict[str, Any]) -> None:
        """Store conversation context in Redis"""
        key = f"context:{user_id}"
        self.redis_client.set(key, json.dumps(context_data))

    def get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get conversation context from Redis"""
        key = f"context:{user_id}"
        data = self.redis_client.get(key)
        if data:
            if not isinstance(data, str):
                data = str(data)
            return json.loads(data)
        return {}

    def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        key = f"profile:{user_id}"
        self.redis_client.set(key, json.dumps(profile_data))

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        key = f"profile:{user_id}"
        data = self.redis_client.get(key)
        if data:
            if not isinstance(data, str):
                data = str(data)
            return json.loads(data)
        return {}

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        key = f"log:{event_type}:{int(time.time())}"
        self.redis_client.set(key, json.dumps(data))
