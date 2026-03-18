import json
import logging
import time
from typing import Any, Dict, Optional
import redis.asyncio as redis
from ..core.config import get_settings

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, default_ttl: int = 300):
        settings = get_settings()
        self.redis_url = settings.redis_url
        self.default_ttl = default_ttl
        self.redis: Optional[redis.Redis] = None
        self._local_cache: Dict[str, Dict[str, Any]] = {}

        if self.redis_url:
            try:
                self.redis = redis.from_url(self.redis_url, decode_responses=True)
                logger.info(f"Connected to Redis at {self.redis_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}. Falling back to in-memory cache.")
        else:
            logger.warning("REDIS_URL not set. Using in-memory cache (not distributed).")

    async def get(self, key: str) -> Optional[Any]:
        if self.redis:
            try:
                data = await self.redis.get(key)
                return json.loads(data) if data else None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return None
        
        # Fallback to local cache
        if key in self._local_cache:
            item = self._local_cache[key]
            if time.time() < item["expiry"]:
                return item["value"]
            else:
                del self._local_cache[key]
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        timeout = ttl if ttl is not None else self.default_ttl
        if self.redis:
            try:
                await self.redis.set(key, json.dumps(value), ex=timeout)
                return
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        # Fallback to local cache
        expiry = time.time() + timeout
        self._local_cache[key] = {"value": value, "expiry": expiry}

    async def delete(self, key: str) -> None:
        if self.redis:
            try:
                await self.redis.delete(key)
                return
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        if key in self._local_cache:
            del self._local_cache[key]

    async def incr(self, key: str, expiry: int = 900) -> int:
        if self.redis:
            try:
                # Use a pipeline for atomic increment and expire
                pipe = self.redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, expiry)
                results = await pipe.execute()
                return results[0]
            except Exception as e:
                logger.error(f"Redis incr error: {e}")
        
        # Fallback to local cache
        item = self._local_cache.get(key)
        now = time.time()
        
        if item and now < item["expiry"]:
            new_value = int(item["value"]) + 1
            item["value"] = new_value
            return new_value
        else:
            new_value = 1
            self._local_cache[key] = {"value": new_value, "expiry": now + expiry}
            return new_value

    async def clear(self) -> None:
        if self.redis:
            try:
                await self.redis.flushdb()
                return
            except Exception as e:
                logger.error(f"Redis flushdb error: {e}")
        
        self._local_cache = {}

# Global instance
cache = RedisCache()
