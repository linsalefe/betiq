import redis
import json
import os
from typing import Any, Optional

class RedisCache:
    """Cliente Redis para cache"""
    
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        
        try:
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=0,
                decode_responses=True,
                socket_connect_timeout=2
            )
            self.client.ping()
            self.enabled = True
        except:
            self.enabled = False
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except:
            return None
    
    def set(self, key: str, value: Any, expire_seconds: int = 3600):
        if not self.enabled:
            return
        
        try:
            self.client.setex(key, expire_seconds, json.dumps(value))
        except:
            pass
