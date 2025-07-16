import os
import json
import time
from .redis_manager import RedisManager

class ChromaDBLogger:
    def __init__(self):
        self.redis = RedisManager()

    def log_request(self, query, filters=None, result_count=0, error=None, duration=0):
        log_entry = {
            "timestamp": time.time(),
            "query": query,
            "filters": filters,
            "result_count": result_count,
            "duration": duration,
            "error": error
        }
        redis_key = f"chromadb_log:{int(time.time())}"
        self.redis.redis_client.set(redis_key, json.dumps(log_entry))
        if error:
            print(f"[ChromaDB ERROR] {error} for query '{query}'")
        else:
            print(f"[ChromaDB] Query '{query}' returned {result_count} results in {duration:.3f}s")
