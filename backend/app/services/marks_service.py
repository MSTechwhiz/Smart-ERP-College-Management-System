from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from ..repositories.marks_repository import MarksRepository, get_marks_repository
from ..repositories.student_repository import StudentRepository, get_student_repository
from ..websocket.manager import manager
from ..schemas.marks_schema import Marks, MarksCreate, BulkMarksCreate
from ..utils.grading import calculate_grade, calculate_cgpa
from ..core.audit import log_audit

class MarksService:
    def __init__(
        self, 
        marks_repo: MarksRepository, 
        student_repo: StudentRepository
    ):
        self.marks_repo = marks_repo
        self.student_repo = student_repo

    async def enter_marks(self, marks_data: MarksCreate, user_id: str, user_name: str, user_role: str) -> Dict[str, Any]:
        existing = await self.marks_repo.get_marks_by_criteria({
            "student_id": marks_data.student_id,
            "subject_id": marks_data.subject_id,
            "academic_year": marks_data.academic_year,
            "semester": marks_data.semester
        })
        
        if existing:
            if existing.get("is_locked"):
                raise HTTPException(status_code=400, detail="Marks are locked and cannot be modified")
            
            update_data = {
                marks_data.exam_type: marks_data.marks,
                "updated_by": user_id,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await self.marks_repo.update_marks(existing["id"], update_data)
            after_value = await self.marks_repo.get_marks_by_criteria({"id": existing["id"]})
            await log_audit(user_id, "update", "marks", existing["id"], existing, after_value)
            return after_value
        else:
            marks = Marks(
                student_id=marks_data.student_id,
                subject_id=marks_data.subject_id,
                academic_year=marks_data.academic_year,
                semester=marks_data.semester,
                updated_by=user_id
            )
            marks_dict = marks.model_dump()
            marks_dict[marks_data.exam_type] = marks_data.marks
            marks_dict["updated_at"] = marks_dict["updated_at"].isoformat()
            
            await self.marks_repo.create_marks(marks_dict)
            await log_audit(user_id, "create", "marks", marks.id, after_value=marks_dict)
            return marks_dict

    async def enter_bulk_marks(self, bulk_data: BulkMarksCreate, user_id: str) -> Dict[str, Any]:
        records_to_upsert = []
        for record in bulk_data.records:
            marks = Marks(
                student_id=record["student_id"],
                subject_id=bulk_data.subject_id,
                academic_year=bulk_data.academic_year,
                semester=bulk_data.semester,
                updated_by=user_id
            )
            doc = marks.model_dump()
            doc[bulk_data.exam_type] = record["marks"]
            doc["updated_at"] = doc["updated_at"].isoformat()
            records_to_upsert.append(doc)
            
        success_count = await self.marks_repo.bulk_upsert_marks(records_to_upsert)
        return {"message": f"Bulk marks entered: {success_count} success", "success_count": success_count}

    async def get_marks(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.marks_repo.get_marks_with_subjects(query, skip=skip, limit=limit)

    async def lock_marks(self, marks_id: str, user_id: str, user_name: str, user_role: str) -> Dict[str, Any]:
        marks = await self.marks_repo.get_marks_by_criteria({"id": marks_id})
        if not marks:
            raise HTTPException(status_code=404, detail="Marks not found")
        
        # Calculate total and grade
        total = 0
        weights = {"cia1": 0.15, "cia2": 0.15, "cia3": 0.1, "cia4": 0.1, "model_exam": 0.1, "assignment": 0.1, "semester_exam": 0.3}
        for exam_type, weight in weights.items():
            if marks.get(exam_type) is not None:
                total += marks[exam_type] * weight
        
        grade, grade_point = calculate_grade(total)
        
        update_data = {
            "is_locked": True,
            "total": round(total, 2),
            "grade": grade,
            "grade_point": grade_point,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.marks_repo.update_marks(marks_id, update_data)
        after_value = await self.marks_repo.get_marks_by_criteria({"id": marks_id})
        await log_audit(user_id, "lock", "marks", marks_id, marks, after_value)
        
        # Update student CGPA
        cgpa = await calculate_cgpa(marks["student_id"])
        await self.student_repo.update(marks["student_id"], {"cgpa": cgpa})
        
        # Notification
        student = await self.student_repo.get_by_id(marks["student_id"])
        if student:
            await manager.send_personal_message({
                "type": "marks_published",
                "data": {"subject_id": marks["subject_id"], "grade": grade}
            }, student["user_id"])
            
        return after_value

    async def get_cgpa_data(self, student_id: str) -> Dict[str, Any]:
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
            
        semester_gpa = await self.marks_repo.get_semester_gpa(student_id)
        return {
            "student_id": student_id,
            "cgpa": student.get("cgpa", 0),
            "semester_gpa": semester_gpa
        }

def get_marks_service(
    marks_repo: MarksRepository = Depends(get_marks_repository),
    student_repo: StudentRepository = Depends(get_student_repository)
) -> MarksService:
    return MarksService(marks_repo, student_repo)
