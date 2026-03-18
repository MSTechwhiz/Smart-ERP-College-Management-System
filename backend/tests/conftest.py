import asyncio
import pytest
import os
from httpx import AsyncClient
from app.main import app
from app.core.database import get_db
from app.core.security import create_token
from app.utils.cache import cache
from mongomock_motor import AsyncMongoMockClient
from unittest.mock import AsyncMock

# Mock database
@pytest.fixture(scope="function")
def mock_db():
    client = AsyncMongoMockClient()
    return client["test_db"]

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def mock_redis():
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=None)
    cache.delete = AsyncMock(return_value=None)
    
    # Mock Redis for RateLimitMiddleware
    mock_pipeline = AsyncMock()
    mock_pipeline.zremrangebyscore = AsyncMock()
    mock_pipeline.zadd = AsyncMock()
    mock_pipeline.zcard = AsyncMock()
    mock_pipeline.expire = AsyncMock()
    mock_pipeline.execute = AsyncMock(return_value=[None, None, 1, None]) # request_count = 1
    
    mock_redis_obj = AsyncMock()
    mock_redis_obj.pipeline = lambda: mock_pipeline
    cache.redis = mock_redis_obj
    
    return cache

@pytest.fixture(scope="function")
async def admin_user(mock_db):
    user = {
        "id": "admin-123",
        "email": "admin@test.com",
        "name": "Admin User",
        "role": "admin",
        "is_active": True,
        "permissions": [],
        "sub_roles": []
    }
    await mock_db.users.insert_one(user)
    return user

@pytest.fixture(scope="function")
def admin_token(admin_user):
    return create_token(admin_user)

@pytest.fixture(scope="function")
async def client(mock_db, mock_redis):
    # Pass mock_db to closure
    def get_mock_db():
        return mock_db
        
    # Override get_db to return our mock_db instance
    app.dependency_overrides[get_db] = get_mock_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
