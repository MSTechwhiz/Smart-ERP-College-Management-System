from __future__ import annotations

import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from ..utils.cache import cache


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for static files and health/metrics
        path = request.url.path
        if path.startswith("/static") or path in ["/health", "/metrics", "/"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = int(time.time())
        
        # Use Redis sorted set for sliding window rate limiting
        key = f"rate_limit:{client_ip}:{path}"
        
        try:
            # Add current request to the window
            pipe = cache.redis.pipeline()
            # Remove timestamps older than the window
            pipe.zremrangebyscore(key, 0, now - self.window)
            # Add current timestamp
            pipe.zadd(key, {str(now): now})
            # Count requests in window
            pipe.zcard(key)
            # Set expiry for the key
            pipe.expire(key, self.window)
            
            results = await pipe.execute()
            request_count = results[2]
            
            if request_count > self.limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "RateLimitExceeded",
                        "message": "Too many requests. Please try again later.",
                        "retry_after": self.window
                    }
                )
        except Exception:
            # Fallback for Redis failure: allow request
            pass

        response = await call_next(request)
        return response
