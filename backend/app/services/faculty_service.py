from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
import bcrypt
from fastapi import Depends, HTTPException

from ..repositories.faculty_repository import FacultyRepository, get_faculty_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..core.security import hash_password
from ..core.audit import log_audit


class FacultyService:
    def __init__(self, faculty_repo: FacultyRepository, user_repo: UserRepository):
        self.faculty_repo = faculty_repo
        self.user_repo = user_repo

    async def create_faculty(self, faculty_create_data: Any, admin_user_id: str) -> Dict[str, Any]:
        existing = await self.user_repo.get_by_email(faculty_create_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": faculty_create_data.email,
            "name": faculty_create_data.name,
            "role": "faculty",
            "department_id": faculty_create_data.department_id,
            "password": await hash_password(faculty_create_data.password),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "permissions": [],
            "sub_roles": []
        }
        await self.user_repo.create(user_doc)

        faculty_id = str(uuid.uuid4())
        faculty_doc = {
            "id": faculty_id,
            "user_id": user_id,
            "employee_id": faculty_create_data.employee_id,
            "department_id": faculty_create_data.department_id,
            "designation": faculty_create_data.designation,
            "specialization": faculty_create_data.specialization,
            "joining_date": datetime.now(timezone.utc).isoformat(),
            "is_class_incharge": False,
            "incharge_class": None
        }
        await self.faculty_repo.create(faculty_doc)

        await log_audit(admin_user_id, "create", "faculty", faculty_id, after_value=faculty_doc)
        return faculty_doc

    async def get_faculty_list(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.faculty_repo.get_faculty_with_users(query, skip=skip, limit=limit)

    async def update_faculty(self, faculty_id: str, update_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        faculty = await self.faculty_repo.get_by_id(faculty_id)
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")

        if update_data:
            await self.faculty_repo.update(faculty_id, update_data)
            updated = await self.faculty_repo.get_by_id(faculty_id)
            await log_audit(admin_user_id, "update", "faculty", faculty_id, before_value=faculty, after_value=updated)
            return updated
        return faculty

    async def delete_faculty(self, faculty_id: str, admin_user_id: str) -> bool:
        faculty = await self.faculty_repo.get_by_id(faculty_id)
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")

        await self.user_repo.delete(faculty["user_id"])
        await self.faculty_repo.delete(faculty_id)
        await log_audit(admin_user_id, "delete", "faculty", faculty_id, before_value=faculty)
        return True

    async def assign_class_incharge(self, faculty_id: str, incharge_class: str, admin_user_id: str) -> Dict[str, Any]:
        faculty = await self.faculty_repo.get_by_id(faculty_id)
        if not faculty:
            raise HTTPException(status_code=404, detail="Faculty not found")

        before_value = dict(faculty)
        await self.faculty_repo.update(faculty_id, {"is_class_incharge": True, "incharge_class": incharge_class})
        await self.user_repo.db.users.update_one({"id": faculty["user_id"]}, {"$addToSet": {"sub_roles": "class_incharge"}})
        
        from ..utils.cache import cache
        await cache.delete(f"user_profile:{faculty['user_id']}")

        after_value = await self.faculty_repo.get_by_id(faculty_id)
        await log_audit(admin_user_id, "assign_class_incharge", "faculty", faculty_id, before_value, after_value)
        return after_value


def get_faculty_service(
    faculty_repo: FacultyRepository = Depends(get_faculty_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> FacultyService:
    return FacultyService(faculty_repo, user_repo)
