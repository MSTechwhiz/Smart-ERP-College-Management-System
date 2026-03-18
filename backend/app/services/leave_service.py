from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from ..repositories.leave_repository import LeaveRepository, get_leave_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..schemas.leave_schema import LeaveRequest

class LeaveService:
    def __init__(self, leave_repo: LeaveRepository, student_repo: StudentRepository):
        self.leave_repo = leave_repo
        self.student_repo = student_repo

    async def submit_leave_request(self, data: Any, user_id: str) -> Dict[str, Any]:
        student = await self.student_repo.get_by_user_id(user_id)
        if not student: raise HTTPException(status_code=404, detail="Student not found")
        
        leave = LeaveRequest(
            student_id=student["id"],
            status="Pending",
            **data.model_dump()
        )
        doc = leave.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        await self.leave_repo.create(doc)
        return doc

    async def get_leave_requests(self, user: Dict[str, Any], status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        if user["role"] == "student":
            student = await self.student_repo.get_by_user_id(user["id"])
            if student: query["student_id"] = student["id"]
        elif user["role"] == "hod":
            dept_id = user.get("department_id")
            if not dept_id:
                raise HTTPException(status_code=400, detail="HOD department not configured")
            dept_students = await self.student_repo.list_by_department(dept_id)
            query["student_id"] = {"$in": [s["id"] for s in dept_students]}
        
        if status: query["status"] = status
        requests = await self.leave_repo.list_requests(query)
        
        # Enrich with student details
        enriched_requests = []
        for req in requests:
            student = await self.student_repo.get_by_id(req.get("student_id"))
            if student:
                req["student_name"] = student.get("name", "Unknown Student")
                req["roll_number"] = student.get("roll_number", "N/A")
                req["department_name"] = student.get("department_name", "N/A")
            enriched_requests.append(req)
            
        return enriched_requests

    async def approve_leave_request(self, request_id: str, approved: bool, user_id: str) -> Dict[str, Any]:
        leave = await self.leave_repo.get_by_id(request_id)
        if not leave: raise HTTPException(status_code=404, detail="Leave request not found")
        
        status = "approved" if approved else "rejected"
        await self.leave_repo.update(request_id, {"status": status, "approved_by": user_id})
        return {"message": f"Leave request {status}"}

def get_leave_service(
    leave_repo: LeaveRepository = Depends(get_leave_repository),
    student_repo: StudentRepository = Depends(get_student_repository)
) -> LeaveService:
    return LeaveService(leave_repo, student_repo)
