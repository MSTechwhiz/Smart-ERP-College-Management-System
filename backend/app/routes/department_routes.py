from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from ..core.security import get_current_user, require_roles
from ..schemas.department_schema import DepartmentCreate
from ..services.department_service import DepartmentService, get_department_service

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.post("", response_model=dict)
async def create_department(
    dept_data: DepartmentCreate, 
    user: dict = Depends(require_roles(["principal", "admin"])),
    dept_service: DepartmentService = Depends(get_department_service)
):
    doc = await dept_service.create_department(dept_data, user["id"])
    return {"message": "Department created", "department": doc}


@router.get("", response_model=List[dict])
async def get_departments(
    user: dict = Depends(get_current_user),
    dept_service: DepartmentService = Depends(get_department_service)
):
    return await dept_service.get_departments()


@router.get("/{dept_id}", response_model=dict)
async def get_department(
    dept_id: str, 
    user: dict = Depends(get_current_user),
    dept_service: DepartmentService = Depends(get_department_service)
):
    dept = await dept_service.get_department(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@router.get("/{dept_id}/analytics", response_model=dict)
async def get_department_analytics(
    dept_id: str,
    user: dict = Depends(get_current_user),
    dept_service: DepartmentService = Depends(get_department_service)
):
    """Get full analytics for a department including year-wise student distribution."""
    return await dept_service.get_department_analytics(dept_id)


@router.put("/{dept_id}", response_model=dict)
async def update_department(
    dept_id: str,
    name: Optional[str] = None,
    code: Optional[str] = None,
    hod_id: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "admin"])),
    dept_service: DepartmentService = Depends(get_department_service)
):
    """Update department"""
    update_data = {}
    if name:
        update_data["name"] = name
    if code:
        update_data["code"] = code
    if hod_id is not None:
        update_data["hod_id"] = hod_id

    updated = await dept_service.update_department(dept_id, update_data, user["id"])
    return {"message": "Department updated", "department": updated}


@router.delete("/{dept_id}", response_model=dict)
async def delete_department(
    dept_id: str, 
    user: dict = Depends(require_roles(["principal", "admin"])),
    dept_service: DepartmentService = Depends(get_department_service)
):
    """Delete department (only if no students/faculty)"""
    await dept_service.delete_department(dept_id, user["id"])
    return {"message": "Department deleted"}

