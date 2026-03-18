from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..core.security import get_current_user, require_roles
from ..schemas.auth_schema import TokenResponse, UserCreate, UserLogin
from ..services.auth_service import AuthService, get_auth_service


router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/register", response_model=dict)
async def register_user(
    user_data: UserCreate,
    user: dict = Depends(require_roles(["principal", "admin"])),
    auth_service: AuthService = Depends(get_auth_service)
):
    user_dict = await auth_service.register_user(user_data)
    return {"message": "User registered successfully", "user": user_dict}


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    result = await auth_service.login(login_data)
    return TokenResponse(
        access_token=result["access_token"], 
        refresh_token=result["refresh_token"],
        user=result["user"]
    )


@router.post("/auth/refresh", response_model=dict)
async def refresh(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.refresh_token(refresh_token)


@router.get("/auth/me", response_model=dict)
async def get_me(
    user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    user_response = await auth_service.get_me(user)
    return user_response

