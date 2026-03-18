from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException
from ..repositories.admission_repository import AdmissionRepository, get_admission_repository
from ..repositories.department_repository import DepartmentRepository, get_department_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..core.audit import log_audit
from ..core.security import hash_password
from ..schemas.auth_schema import User as UserSchema
from ..schemas.student_schema import Student as StudentSchema

class AdmissionService:
    def __init__(
        self, 
        admission_repo: AdmissionRepository,
        department_repo: DepartmentRepository,
        student_repo: StudentRepository,
        user_repo: UserRepository
    ):
        self.admission_repo = admission_repo
        self.department_repo = department_repo
        self.student_repo = student_repo
        self.user_repo = user_repo

    async def create_application(self, data: Any, admin_user_id: str) -> Dict[str, Any]:
        app_id = str(uuid.uuid4())
        doc = {
            "id": app_id,
            **data.model_dump(),
            "status": "Pending",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "verified_at": None, "verified_by": None,
            "approved_at": None, "approved_by": None,
            "rejected_at": None, "rejected_by": None,
            "rejection_reason": None, "created_student_id": None
        }
        await self.admission_repo.create(doc)
        await log_audit(admin_user_id, "create", "admission", app_id, after_value=doc)
        return doc

    async def get_applications(
        self, 
        user: Dict[str, Any], 
        status: Optional[str] = None, 
        department_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        query = {}
        if user["role"] == "admin":
            query["status"] = status if status else {"$in": ["Pending", "office_verified"]}
        elif user["role"] == "hod":
            query["status"] = "office_verified"
            query["department_id"] = user.get("department_id")
        elif user["role"] == "principal":
            query["status"] = "hod_approved"
            
        if department_id and user["role"] in ["principal", "admin"]:
            query["department_id"] = department_id
            
        applications = await self.admission_repo.list_applications(query, skip=skip, limit=limit)
        
        # Batch enrich departments
        dept_ids = list({a["department_id"] for a in applications})
        depts = await self.department_repo.db.departments.find({"id": {"$in": dept_ids}}, {"id": 1, "name": 1, "code": 1}).to_list(None)
        dept_map = {d["id"]: d for d in depts}
        
        for app in applications:
            d = dept_map.get(app["department_id"])
            if d:
                app["department_name"] = d["name"]
                app["department_code"] = d["code"]
        return applications

    async def verify_application(self, app_id: str, user_id: str) -> bool:
        app = await self.admission_repo.get_by_id(app_id)
        if not app: raise HTTPException(status_code=404, detail="Application not found")
        if app["status"] != "Pending": raise HTTPException(status_code=400, detail="Not in Pending status")
        
        return await self.admission_repo.update(app_id, {
            "status": "office_verified",
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "verified_by": user_id
        })

    async def hod_review(self, app_id: str, approved: bool, rejection_reason: str, user_id: str) -> bool:
        app = await self.admission_repo.get_by_id(app_id)
        if not app: raise HTTPException(status_code=404, detail="Application not found")
        if app["status"] != "office_verified": raise HTTPException(status_code=400, detail="Not verified by office")
        
        update_data = {
            "status": "hod_approved" if approved else "Rejected",
            "rejection_reason": rejection_reason if not approved else None,
            "hod_reviewed_at": datetime.now(timezone.utc).isoformat(),
            "hod_reviewed_by": user_id
        }
        return await self.admission_repo.update(app_id, update_data)

    async def principal_approve(self, app_id: str, approved: bool, rejection_reason: str, user_id: str) -> Dict[str, Any]:
        app = await self.admission_repo.get_by_id(app_id)
        if not app: raise HTTPException(status_code=404, detail="Application not found")
        if app["status"] != "hod_approved": raise HTTPException(status_code=400, detail="Not approved by HOD")
        
        if not approved:
            await self.admission_repo.update(app_id, {
                "status": "Rejected",
                "rejection_reason": rejection_reason,
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "rejected_by": user_id
            })
            return {"message": "Rejected"}

        # Full approval and creation
        dept = await self.department_repo.get_by_id(app["department_id"])
        dept_code = dept["code"] if dept else "UNK"
        
        year_short = datetime.now().year % 100
        batch_year = str(datetime.now().year)
        count = await self.admission_repo.count_students_in_batch(app["department_id"], batch_year)
        roll_number = f"{year_short}{dept_code}{str(count + 1).zfill(3)}"
        
        # Create user
        user_id_new = str(uuid.uuid4())
        user_doc = {
            "id": user_id_new,
            "email": app["applicant_email"],
            "name": app["applicant_name"],
            "role": "student",
            "department_id": app["department_id"],
            "password": await hash_password("student@123"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "permissions": [], "sub_roles": []
        }
        await self.user_repo.create(user_doc)
        
        # Create student
        student_id = str(uuid.uuid4())
        student_doc = {
            "id": student_id,
            "user_id": user_id_new,
            "roll_number": roll_number,
            "department_id": app["department_id"],
            "batch": f"{datetime.now().year}-{datetime.now().year + 4}",
            "semester": 1,
            "regulation": "R2023",
            "admission_date": datetime.now(timezone.utc).isoformat(),
            "is_active": True, "cgpa": 0.0
        }
        await self.student_repo.create(student_doc)
        
        # Update app
        await self.admission_repo.update(app_id, {
            "status": "Approved",
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "approved_by": user_id,
            "created_student_id": student_id
        })
        
        await log_audit(user_id, "approve_admission", "admission", app_id, after_value={"student_id": student_id, "roll_number": roll_number})
        
        return {
            "message": "Admission approved and student created",
            "student_id": student_id,
            "roll_number": roll_number,
            "default_password": "student@123"
        }

def get_admission_service(
    admission_repo: AdmissionRepository = Depends(get_admission_repository),
    department_repo: DepartmentRepository = Depends(get_department_repository),
    student_repo: StudentRepository = Depends(get_student_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AdmissionService:
    return AdmissionService(admission_repo, department_repo, student_repo, user_repo)
