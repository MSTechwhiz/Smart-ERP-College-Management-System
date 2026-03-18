from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException
from ..repositories.grievance_repository import GrievanceRepository, get_grievance_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..core.audit import log_audit
from ..websocket.manager import manager
from ..schemas.grievance_schema import Grievance

class GrievanceService:
    def __init__(self, grievance_repo: GrievanceRepository, student_repo: StudentRepository, user_repo: UserRepository):
        self.grievance_repo = grievance_repo
        self.student_repo = student_repo
        self.user_repo = user_repo

    async def submit_grievance(self, data: Any, user: Dict[str, Any]) -> Dict[str, Any]:
        student = await self.student_repo.get_by_user_id(user["id"])
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        grievance = Grievance(
            student_id=student["id"],
            department_id=student.get("department_id"),
            current_level=data.target_type,
            status=f"{data.target_type}_review",
            **data.model_dump()
        )
        
        initial_workflow = {
            "level": "student",
            "user_id": user["id"],
            "user_name": user["name"],
            "action": "submitted",
            "remarks": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        grievance.workflow_history = [initial_workflow]
        
        doc = grievance.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        doc["updated_at"] = doc["updated_at"].isoformat()
        
        await self.grievance_repo.create(doc)
        await manager.broadcast_to_role({
            "type": "new_grievance",
            "data": {"ticket_id": grievance.ticket_id, "category": data.category}
        }, "faculty")
        
        await log_audit(user["id"], "create", "grievance", grievance.id, None, doc)
        return doc

    async def get_grievances(self, user: Dict[str, Any], status: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        if user["role"] == "student":
            student = await self.student_repo.get_by_user_id(user["id"])
            if student: query["student_id"] = student["id"]
        elif user["role"] == "faculty":
            if user.get("department_id"): query["department_id"] = user["department_id"]
            query["current_level"] = "faculty"
            query["target_type"] = "faculty"
        elif user["role"] == "hod":
            dept_id = user.get("department_id")
            if not dept_id:
                raise HTTPException(status_code=400, detail="HOD department not configured")
            query["department_id"] = dept_id
            
            if status == "hod_review":
                query["status"] = "hod_review"
            elif status == "escalated":
                # For escalated view, show all in department with escalated status
                query["status"] = "escalated"
            else:
                # Default HOD review view
                query["current_level"] = "hod"
                query["target_type"] = "faculty"
        elif user["role"] == "admin":
            query["current_level"] = "admin"
            query["target_type"] = "admin"
        elif user["role"] == "principal":
            query["current_level"] = "principal"
            query["target_type"] = "admin"
            
        if status: query["status"] = status
        if category: query["category"] = category
            
        grievances = await self.grievance_repo.list_grievances(query)
        
        # Batch enrich student names
        student_ids = list({g["student_id"] for g in grievances})
        students = await self.student_repo.db.students.find({"id": {"$in": student_ids}}, {"id": 1, "roll_number": 1, "user_id": 1}).to_list(None)
        student_map = {s["id"]: s for s in students}
        
        user_ids = [s["user_id"] for s in students]
        users = await self.user_repo.db.users.find({"id": {"$in": user_ids}}, {"id": 1, "name": 1}).to_list(None)
        user_map = {u["id"]: u for u in users}
        
        for g in grievances:
            s_id = g.get("student_id")
            if s_id:
                s = student_map.get(s_id)
                if s:
                    g["roll_number"] = s.get("roll_number", "N/A")
                    u_id = s.get("user_id")
                    if u_id:
                        u = user_map.get(u_id)
                        if u: g["student_name"] = u.get("name", "Unknown Student")
                
        return grievances

    async def forward_grievance(self, grievance_id: str, to_level: str, remarks: Optional[str], user: Dict[str, Any]) -> Dict[str, Any]:
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance: raise HTTPException(status_code=404, detail="Grievance not found")
        
        workflow_entry = {
            "level": grievance["current_level"],
            "user_id": user["id"],
            "user_name": user["name"],
            "action": f"forwarded_to_{to_level}",
            "remarks": remarks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        update_data = {
            "current_level": to_level,
            "status": f"{to_level}_review",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if to_level == "hod" and remarks:
            update_data["faculty_remarks_for_hod"] = remarks
        
        await self.grievance_repo.update_workflow(grievance_id, update_data, workflow_entry)
        await manager.broadcast_to_role({
            "type": "grievance_forwarded",
            "data": {"ticket_id": grievance["ticket_id"], "grievance_id": grievance_id}
        }, to_level)
        
        return {"message": f"Grievance forwarded to {to_level}"}

    async def get_grievance_detail(self, grievance_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance:
            raise HTTPException(status_code=404, detail="Grievance not found")
        
        if user["role"] == "student":
            student = await self.student_repo.get_by_user_id(user["id"])
            if not student or student["id"] != grievance["student_id"]:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Enrich
        student = await self.student_repo.get_by_id(grievance["student_id"])
        if student:
            u = await self.user_repo.get_by_id(student["user_id"])
            if u:
                grievance["student_name"] = u["name"]
                grievance["student_email"] = u["email"]
            grievance["roll_number"] = student["roll_number"]
            
            dept = await self.user_repo.db.departments.find_one({"id": student["department_id"]}, {"_id": 0, "name": 1, "code": 1})
            if dept: grievance["department"] = dept
            
        grievance["comments"] = await self.grievance_repo.get_comments(grievance_id)
        return grievance

    async def get_all_grievances(self, user: Dict[str, Any], status: Optional[str], category: Optional[str]) -> List[Dict[str, Any]]:
        query = {}
        if user["role"] == "hod":
            dept_students = await self.student_repo.list_by_department(user["department_id"])
            query["student_id"] = {"$in": [s["id"] for s in dept_students]}
        
        if status: query["status"] = status
        if category: query["category"] = category
        
        grievances = await self.grievance_repo.list_grievances(query)
        # Batch enrich (similar to get_grievances)
        # ... (Implementation similar to get_grievances)
        return grievances

    async def assign_grievance(self, grievance_id: str, assigned_to: str) -> Dict[str, Any]:
        await self.grievance_repo.update(grievance_id, {"assigned_to": assigned_to, "status": "in_progress"})
        return {"message": "Grievance assigned"}

    async def escalate_grievance(self, grievance_id: str) -> Dict[str, Any]:
        await self.grievance_repo.update(grievance_id, {"status": "escalated"})
        return {"message": "Grievance escalated"}

    async def add_comment(self, grievance_id: str, comment: str, user: Dict[str, Any]) -> Dict[str, Any]:
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance: raise HTTPException(status_code=404, detail="Grievance not found")
        
        comment_doc = {
            "id": str(uuid.uuid4()),
            "grievance_id": grievance_id,
            "user_id": user["id"],
            "user_name": user["name"],
            "user_role": user["role"],
            "comment": comment,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await self.grievance_repo.add_comment(comment_doc)
        return {"message": "Comment added", "comment": comment_doc}

    async def resolve_grievance(self, grievance_id: str, resolution: str, user: Dict[str, Any]) -> Dict[str, Any]:
        grievance = await self.grievance_repo.get_by_id(grievance_id)
        if not grievance: raise HTTPException(status_code=404, detail="Grievance not found")
        
        workflow_entry = {
            "level": grievance["current_level"],
            "user_id": user["id"],
            "user_name": user["name"],
            "action": "resolved",
            "remarks": resolution,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        update_data = {
            "status": "resolved",
            "resolution": resolution,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolved_by": user["id"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.grievance_repo.update_workflow(grievance_id, update_data, workflow_entry)
        
        # Notify student
        student = await self.student_repo.get_by_id(grievance["student_id"])
        if student:
            await manager.send_personal_message({
                "type": "grievance_resolved",
                "data": {"ticket_id": grievance["ticket_id"], "resolution": resolution}
            }, student["user_id"])
            
        await log_audit(user["id"], "resolve", "grievance", grievance_id, None, update_data)
        return {"message": "Grievance resolved"}

def get_grievance_service(
    grievance_repo: GrievanceRepository = Depends(get_grievance_repository),
    student_repo: StudentRepository = Depends(get_student_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> GrievanceService:
    return GrievanceService(grievance_repo, student_repo, user_repo)
