from typing import List, Optional, Dict, Any
from ..core.database import get_db
from datetime import datetime, timezone

class SettingsRepository:
    def __init__(self):
        self.db = get_db()

    async def get_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.user_settings.find_one({"user_id": user_id}, {"_id": 0})

    async def create_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        await self.db.user_settings.insert_one(settings_data)
        settings_data.pop("_id", None)
        return settings_data

    async def update_settings(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        result = await self.db.user_settings.update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.users.find_one({"id": user_id}, {"_id": 0})

    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": {"password": hashed_password}}
        )
        if result.modified_count > 0:
            from ..utils.cache import cache
            await cache.delete(f"user_profile:{user_id}")
        return result.modified_count > 0

    async def get_student_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.students.find_one({"user_id": user_id}, {"_id": 0})

    async def get_faculty_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.faculty.find_one({"user_id": user_id}, {"_id": 0})

    async def get_department_by_id(self, dept_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.departments.find_one({"id": dept_id}, {"_id": 0, "name": 1, "code": 1})

    async def get_department_by_hod(self, hod_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.departments.find_one({"hod_id": hod_id}, {"_id": 0})
