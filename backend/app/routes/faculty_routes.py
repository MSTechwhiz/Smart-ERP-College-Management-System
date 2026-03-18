from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from ..core.audit import log_audit
from ..core.database import get_db
from ..core.security import get_current_user, hash_password, require_roles
from ..schemas.auth_schema import User
from ..schemas.faculty_schema import Faculty, FacultyCreate
from ..services.faculty_service import FacultyService, get_faculty_service


router = APIRouter(prefix="/api/faculty", tags=["faculty"])


@router.post("", response_model=dict)
async def create_faculty(
    faculty_data: FacultyCreate, 
    user: dict = Depends(require_roles(["principal", "admin"])),
    faculty_service: FacultyService = Depends(get_faculty_service)
):
    faculty_dict = await faculty_service.create_faculty(faculty_data, user["id"])
    return {"message": "Faculty created", "faculty": faculty_dict}


@router.get("", response_model=List[dict])
async def get_faculty_list(
    department_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user: dict = Depends(get_current_user),
    faculty_service: FacultyService = Depends(get_faculty_service)
):
    query = {}
    if user["role"] == "hod":
        query["department_id"] = user["department_id"]
    elif department_id and user["role"] in ["principal", "admin"]:
        query["department_id"] = department_id

    faculty_list = await faculty_service.get_faculty_list(query, skip=skip, limit=limit)
    return faculty_list


@router.get("/me/profile", response_model=dict)
async def get_my_faculty_profile(
    user: dict = Depends(require_roles(["faculty", "hod", "principal", "admin"])),
    faculty_service: FacultyService = Depends(get_faculty_service)
):
    faculty = await faculty_service.faculty_repo.get_by_user_id(user["id"])
    if not faculty:
        if user["role"] in ["principal", "admin", "hod"]:
            return {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "designation": user["role"].capitalize(),
                "employee_id": "ADMIN",
            }
        raise HTTPException(status_code=404, detail="Faculty profile not found")

    faculty["name"] = user["name"]
    faculty["email"] = user["email"]
    faculty["role"] = user["role"]
    return faculty


@router.put("/{faculty_id}/class-incharge", response_model=dict)
async def assign_class_incharge(
    faculty_id: str,
    incharge_class: str,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    faculty_service: FacultyService = Depends(get_faculty_service)
):
    faculty = await faculty_service.faculty_repo.get_by_id(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    if user["role"] == "hod" and faculty["department_id"] != user["department_id"]:
        raise HTTPException(status_code=403, detail="Cannot assign faculty outside your department")

    updated = await faculty_service.assign_class_incharge(faculty_id, incharge_class, user["id"])
    return {"message": "Class incharge assigned", "faculty": updated}


@router.put("/{faculty_id}", response_model=dict)
async def update_faculty(
    faculty_id: str,
    designation: Optional[str] = None,
    specialization: Optional[str] = None,
    is_class_incharge: Optional[bool] = None,
    incharge_class: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "admin", "hod"])),
    faculty_service: FacultyService = Depends(get_faculty_service)
):
    """Update faculty details"""
    faculty = await faculty_service.faculty_repo.get_by_id(faculty_id)
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty not found")

    if user["role"] == "hod" and faculty["department_id"] != user.get("department_id"):
        raise HTTPException(status_code=403, detail="Cannot update faculty from other department")

    update_data = {}
    if designation:
        update_data["designation"] = designation
    if specialization:
        update_data["specialization"] = specialization
    if is_class_incharge is not None:
        update_data["is_class_incharge"] = is_class_incharge
    if incharge_class:
        update_data["incharge_class"] = incharge_class

    updated = await faculty_service.update_faculty(faculty_id, update_data, user["id"])
    return {"message": "Faculty updated", "faculty": updated}


@router.delete("/{faculty_id}", response_model=dict)
async def delete_faculty(
    faculty_id: str, 
    user: dict = Depends(require_roles(["principal", "admin"])),
    faculty_service: FacultyService = Depends(get_faculty_service)
):
    """Delete faculty and user account"""
    await faculty_service.delete_faculty(faculty_id, user["id"])
    return {"message": "Faculty deleted"}

