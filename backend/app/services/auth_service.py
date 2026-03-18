from __future__ import annotations

from typing import Any, Dict, Optional
from datetime import datetime, timezone
import bcrypt
import jwt
from fastapi import HTTPException, status, Depends

from ..core.config import get_settings
from ..repositories.user_repository import UserRepository, get_user_repository


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.settings = get_settings()

    async def register_user(self, user_data: Any) -> Dict[str, Any]:
        existing = await self.user_repo.get_by_email(user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_dict = user_data.model_dump()
        from ..core.security import hash_password
        user_dict["password"] = await hash_password(user_data.password)
        user_dict["created_at"] = user_dict["created_at"].isoformat()

        await self.user_repo.create(user_dict)
        del user_dict["password"]
        user_dict.pop("_id", None)
        return user_dict

    async def login(self, login_data: Any) -> Dict[str, Any]:
        from ..utils.cache import cache
        lockout_key = f"lockout:{login_data.email}"
        attempts_key = f"attempts:{login_data.email}"
        
        # Check lockout
        if await cache.get(lockout_key):
            raise HTTPException(status_code=423, detail="Account temporarily locked due to multiple failed attempts. Try again in 15 minutes.")

        email = str(login_data.email).strip().lower()
        user = await self.user_repo.get_by_email(email)
        
        from ..core.security import verify_password, create_access_token, create_refresh_token
        
        if not user or not await verify_password(login_data.password, user["password"]):
            # Increment attempts
            attempts = await cache.incr(attempts_key, expiry=900)
            
            if attempts >= 5:
                await cache.set(lockout_key, True, ttl=900) # 15 min lockout
                await cache.delete(attempts_key)
                raise HTTPException(status_code=423, detail="Account locked due to 5 failed attempts.")
            
            raise HTTPException(status_code=401, detail=f"Invalid credentials. {5 - attempts} attempts remaining.")

        if user["role"] != login_data.role:
            raise HTTPException(status_code=401, detail="Invalid role for this user")

        # Success - Reset attempts
        await cache.delete(attempts_key)

        access_token = create_access_token(user)
        refresh_token = create_refresh_token(user)
        
        user_response = {k: v for k, v in user.items() if k not in ["password", "_id"]}

        if user.get("department_id"):
            db = self.user_repo.db
            dept = await db.departments.find_one({"id": user["department_id"]}, {"_id": 0, "code": 1})
            if dept:
                user_response["department_code"] = dept["code"].lower()

        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "user": user_response
        }

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        from ..core.security import create_access_token, create_refresh_token
        import jwt
        
        try:
            payload = jwt.decode(refresh_token, self.settings.jwt_refresh_secret, algorithms=[self.settings.jwt_algorithm])
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
            user_id = payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="User not found or inactive")

        return {
            "access_token": create_access_token(user),
            "refresh_token": create_refresh_token(user)
        }

    async def get_me(self, user: dict) -> Dict[str, Any]:
        user_response = {k: v for k, v in user.items() if k not in ["password", "_id"]}
        if user.get("department_id"):
            db = self.user_repo.db
            dept = await db.departments.find_one({"id": user["department_id"]}, {"_id": 0, "code": 1})
            if dept:
                user_response["department_code"] = dept["code"].lower()
        return user_response


def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)
