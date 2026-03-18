from typing import List, Optional
from fastapi import APIRouter, Depends
from ..core.security import get_current_user
from ..schemas.settings_schema import UserSettingsUpdate, PasswordChange
from ..services.settings_service import SettingsService

router = APIRouter(prefix="/api", tags=["Settings"])
service = SettingsService()

@router.get("/settings", response_model=dict)
async def get_user_settings(user: dict = Depends(get_current_user)):
    return await service.get_user_settings(user["id"])

@router.put("/settings", response_model=dict)
async def update_user_settings(
    settings_data: UserSettingsUpdate,
    user: dict = Depends(get_current_user)
):
    return await service.update_user_settings(user["id"], settings_data)

@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    user: dict = Depends(get_current_user)
):
    return await service.change_password(user["id"], password_data)

@router.get("/profile", response_model=dict)
async def get_user_profile(user: dict = Depends(get_current_user)):
    return await service.get_user_profile(user)
