from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException
from ..repositories.settings_repository import SettingsRepository
from ..schemas.settings_schema import UserSettings, UserSettingsUpdate, PasswordChange
from ..core.security import verify_password, hash_password
from ..core.audit import log_audit

class SettingsService:
    def __init__(self):
        self.repo = SettingsRepository()

    async def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        settings = await self.repo.get_settings(user_id)
        if not settings:
            default_settings = UserSettings(user_id=user_id)
            doc = default_settings.model_dump()
            doc["updated_at"] = doc["updated_at"].isoformat()
            await self.repo.create_settings(doc)
            return doc
        return settings

    async def update_user_settings(self, user_id: str, settings_data: UserSettingsUpdate) -> Dict[str, Any]:
        update_data = {k: v for k, v in settings_data.model_dump().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.repo.update_settings(user_id, update_data)
        return {"message": "Settings updated successfully"}

    async def change_password(self, user_id: str, password_data: PasswordChange) -> Dict[str, Any]:
        db_user = await self.repo.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not await verify_password(password_data.current_password, db_user["password"]):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        new_hashed = await hash_password(password_data.new_password)
        await self.repo.update_password(user_id, new_hashed)
        await log_audit(user_id, "change_password", "user", user_id)
        return {"message": "Password changed successfully"}

    async def get_user_profile(self, user: Dict[str, Any]) -> Dict[str, Any]:
        profile = await self.repo.get_user_by_id(user["id"])
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile.pop("password", None)
        
        if user["role"] == "student":
            student = await self.repo.get_student_by_user_id(user["id"])
            if student:
                profile["student_details"] = student
                dept = await self.repo.get_department_by_id(student["department_id"])
                if dept:
                    profile["department"] = dept
        elif user["role"] == "faculty":
            faculty = await self.repo.get_faculty_by_user_id(user["id"])
            if faculty:
                profile["faculty_details"] = faculty
                dept = await self.repo.get_department_by_id(faculty["department_id"])
                if dept:
                    profile["department"] = dept
        elif user["role"] == "hod":
            dept = await self.repo.get_department_by_hod(user["id"])
            if dept:
                profile["department"] = dept
        
        return profile
