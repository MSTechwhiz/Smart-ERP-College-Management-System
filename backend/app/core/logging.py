from __future__ import annotations

import logging
import sys
import time
import uuid
from typing import Any, Dict
from logging.handlers import RotatingFileHandler

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


import contextvars

request_id_var = contextvars.ContextVar("request_id", default="N/A")

import os
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "N/A")
        }
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure structured logging
def setup_logging():
    env = os.environ.get("ENV", "development")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    console_handler = logging.StreamHandler(sys.stdout)
    
    if env == "production":
        formatter = JSONFormatter()
    else:
        # Use default value for request_id if not present
        formatter = logging.Formatter('%(asctime)s - [RID:%(request_id)s] - %(name)s - %(levelname)s - %(message)s', defaults={"request_id": "N/A"})
        
    console_handler.setFormatter(formatter)
    
    # File handler with rotation (50MB, 5 backups)
    file_handler = RotatingFileHandler(
        "app.log", 
        maxBytes=50 * 1024 * 1024, 
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    # Filter is already adding rid, but defaults in Formatter is safer for all loggers
    logger.addFilter(RequestIdFilter())

# Filter to add request_id to log records
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = request_id_var.get()
        return True

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        token = request_id_var.set(req_id)
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            user_info = ""
            if hasattr(request.state, "user") and request.state.user:
                user = request.state.user
                user_info = f" User: {user.get('id')} ({user.get('email')})"
            
            logging.info(
                f"Method: {request.method} Path: {request.url.path} "
                f"Status: {response.status_code} ProcessTime: {process_time:.4f}s{user_info}"
            )
            
            # Add request-id header to response
            response.headers["X-Request-ID"] = req_id
            return response
        except Exception as e:
            process_time = time.time() - start_time
            user_info = ""
            if hasattr(request.state, "user") and request.state.user:
                user = request.state.user
                user_info = f" User: {user.get('id')} ({user.get('email')})"

            logging.error(
                f"Method: {request.method} Path: {request.url.path} "
                f"Status: 500 ProcessTime: {process_time:.4f}s{user_info} Error: {str(e)}",
                exc_info=True
            )
            raise
        finally:
            request_id_var.reset(token)
