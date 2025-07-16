

"""
SecurityFilter: Advanced security filtering for XOFlowers agent.
 - Jailbreak detection (regex, extensibil)
 - Rate limiting (configurabil, pe Redis)
 - Toate evenimentele logate în Redis și logger
"""

import re
import time
import logging
import json
from typing import Optional
from src.database.redis_manager import RedisManager
from config import RATE_LIMIT_SECONDS
from src.intelligence.prompts import CENSORSHIP_KEYWORDS


class SecurityFilter:
    """
    SecurityFilter: advanced jailbreak detection, rate limiting, and security event logging.
    Toate evenimentele de securitate sunt logate în Redis și logger.
    """
    JAILBREAK_PATTERNS = [
        re.compile(r"(?i)ignore previous|disregard previous|bypass|jailbreak|unfiltered|do anything|prompt injection|act as|simulate|override|system prompt|developer mode|\bopenai\b|\bchatgpt\b|\bmidjourney\b|\bdan\b|\bignore all instructions\b"),
        re.compile(r"(?i)\btoken\b|\bapi[_-]?key\b|\bsecret\b|\bpassword\b|\baccess[_-]?token\b"),
        # Extindeți cu pattern-uri noi dacă e nevoie
    ]
    RATE_LIMIT_SECONDS: int = RATE_LIMIT_SECONDS

    def __init__(self) -> None:
        self.redis: RedisManager = RedisManager()
        self.logger: logging.Logger = logging.getLogger("SecurityFilter")

    def is_jailbreak_attempt(self, user_id: str, message: str) -> bool:
        """
        Detectează tentative de jailbreak folosind pattern-uri avansate. Loghează orice eveniment.
        """
        for pattern in self.JAILBREAK_PATTERNS:
            if pattern.search(message):
                self.log_security_event(user_id, "jailbreak_attempt", message)
                return True
        return False

    def is_offensive_content(self, user_id: str, message: str) -> bool:
        """
        Detectează conținut ofensator folosind lista CENSORSHIP_KEYWORDS. Loghează orice eveniment.
        """
        message_lower = message.lower()
        for keyword in CENSORSHIP_KEYWORDS:
            if keyword in message_lower:
                self.log_security_event(user_id, "offensive_content", message)
                return True
        return False

    def is_rate_limited(self, user_id: str, event: str = "message") -> bool:
        """
        Verifică dacă utilizatorul este rate-limited pentru un anumit eveniment.
        Loghează orice depășire de limită.
        """
        key = f"rate_limit:{user_id}:{event}"
        now = int(time.time())
        last_time = self.redis.redis_client.get(key)
        last_time_int = 0
        if last_time:
            try:
                if isinstance(last_time, bytes):
                    last_time_int = int(last_time.decode())
                elif isinstance(last_time, str):
                    last_time_int = int(last_time)
                else:
                    last_time_int = int(str(last_time))
            except Exception as e:
                self.logger.error(f"Rate limit parse error: {e}")
                last_time_int = 0
            if now - last_time_int < self.RATE_LIMIT_SECONDS:
                self.log_security_event(user_id, "rate_limited", f"{event} blocked")
                return True
        self.redis.redis_client.set(key, now)
        return False

    def log_security_event(self, user_id: str, event_type: str, details: str) -> None:
        """
        Loghează orice eveniment de securitate în Redis și logger.
        """
        log_entry = {
            "timestamp": time.time(),
            "user_id": user_id,
            "event_type": event_type,
            "details": details
        }
        self.redis.log_event("security", log_entry)
        self.logger.warning(f"SECURITY [{event_type}] user={user_id} details={details}")

    def get_recent_security_events(self, limit: int = 20):
        """
        Returnează ultimele evenimente de securitate din Redis (audit trail).
        """
        # Caută chei log:security:*
        raw_keys = self.redis.redis_client.keys("log:security:*")
        keys = []
        for k in raw_keys:
            if isinstance(k, (bytes, str)):
                keys.append(k.decode() if isinstance(k, bytes) else k)
        keys = sorted(keys, reverse=True)[:limit]
        events = []
        for key in keys:
            data = self.redis.redis_client.get(key)
            if isinstance(data, bytes):
                try:
                    data = data.decode()
                    events.append(json.loads(data))
                except Exception:
                    continue
            elif isinstance(data, str):
                try:
                    events.append(json.loads(data))
                except Exception:
                    continue
        return events
