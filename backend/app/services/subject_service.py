from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import Depends, HTTPException
from ..repositories.subject_repository import SubjectRepository, get_subject_repository
from ..core.audit import log_audit
from ..schemas.subject_schema import Subject, SubjectFacultyMapping

class SubjectService:
    def __init__(self, subject_repo: SubjectRepository):
        self.subject_repo = subject_repo

    async def create_subject(self, data: Any, user_id: str) -> Dict[str, Any]:
        # Check if subject code already exists
        existing = await self.subject_repo.list_subjects({"code": data.code})
        if existing:
            raise HTTPException(status_code=400, detail=f"Subject with code '{data.code}' already exists")
            
        subject = Subject(**data.model_dump())
        doc = subject.model_dump()
        await self.subject_repo.create(doc)
        await log_audit(user_id, "create", "subject", subject.id, after_value=doc)
        return doc

    async def get_subjects(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        return await self.subject_repo.list_subjects(query, skip=skip, limit=limit)

    async def create_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Check for period conflict (same section/semester/day/period/academic_year)
        # We need to find the department_id from the subject to be thorough, 
        # but mappings are already scoped by subject_id.
        
        # Check if this slot is already taken for the section
        existing_slot = await self.subject_repo.list_mappings({
            "academic_year": data["academic_year"],
            "semester": data["semester"],
            "section": data["section"],
            "day": data["day"],
            "period": data["period"]
        })
        if existing_slot:
            raise HTTPException(status_code=400, detail=f"Slot already occupied for Section {data['section']}")

        # 2. Check for faculty double-booking
        existing_faculty_slot = await self.subject_repo.list_mappings({
            "academic_year": data["academic_year"],
            "faculty_id": data["faculty_id"],
            "day": data["day"],
            "period": data["period"]
        })
        if existing_faculty_slot:
            raise HTTPException(status_code=400, detail="Faculty already assigned to another subject in this period")

        mapping = SubjectFacultyMapping(**data)
        doc = mapping.model_dump()
        await self.subject_repo.create_mapping(doc)
        return doc

    async def get_student_timetable(self, student: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Normalize inputs for strict matching
        semester = int(student.get("semester", 1))
        section = str(student.get("section", "A")).upper()
        department_id = student.get("department_id")
        
        # Fetch mappings for the student's context
        query = {
            "semester": semester,
            "section": section
        }
        
        # Debug logging to verify matching
        print(f"--- DEBUG: Timetable Fetch ---")
        print(f"Student: {student.get('name')} (Dept: {student.get('department_name')})")
        print(f"Context: Semester={semester}, Section='{section}', DeptID={department_id}")
        
        # We fetch mappings and then map them to the format requested by the frontend
        raw_mappings = await self.get_mappings(query, department_id=department_id)
        
        print(f"Result: Found {len(raw_mappings)} mapped slots")
        print(f"-------------------------------")
        
        formatted_timetable = []
        for m in raw_mappings:
            formatted_timetable.append({
                "day": m.get("day"),
                "period": m.get("period"),
                "subject": m.get("subject_name", "Unknown Subject"),
                "faculty": m.get("faculty_name", "Unknown Faculty"),
                "subject_code": m.get("subject_code"),
                "subject_type": m.get("subject_type"),
                "start_time": m.get("start_time"),
                "end_time": m.get("end_time")
            })
            
        return formatted_timetable

    async def get_mappings(self, query: Dict[str, Any], department_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        if department_id:
            # First find all subjects belonging to this department
            subjects = await self.subject_repo.list_subjects({"department_id": department_id})
            subject_ids = [s["id"] for s in subjects]
            if not subject_ids:
                return []
            query["subject_id"] = {"$in": subject_ids}

        mappings = await self.subject_repo.list_mappings(query, skip=skip, limit=limit)
        # Optimization: Batch fetch subject info
        subject_ids = list({m["subject_id"] for m in mappings})
        subjects = await self.subject_repo.list_subjects({"id": {"$in": subject_ids}})
        subject_map = {s["id"]: s for s in subjects}
        
        for m in mappings:
            s = subject_map.get(m["subject_id"])
            if s:
                m["subject_name"] = s.get("name", "Unknown Subject")
                m["subject_code"] = s.get("code", "N/A")
                m["subject_type"] = s.get("subject_type", "theory")
        
        # Optimization: Batch fetch faculty names
        faculty_ids = list({m["faculty_id"] for m in mappings})
        # Use faculty profile collection directly to get names
        from ..core.database import get_db
        db = get_db()
        faculty_profiles = await db.faculty.find({"id": {"$in": faculty_ids}}, {"id": 1, "name": 1, "_id": 0}).to_list(None)
        faculty_map = {f.get("id"): f.get("name") for f in faculty_profiles if f.get("id")}
        
        for m in mappings:
            m["faculty_name"] = faculty_map.get(m.get("faculty_id"), "Unknown Faculty")
            
        return mappings

    async def update_subject(self, subject_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject: raise HTTPException(status_code=404, detail="Subject not found")
        await self.subject_repo.update(subject_id, update_data)
        return await self.subject_repo.get_by_id(subject_id)

    async def delete_subject(self, subject_id: str) -> bool:
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject: raise HTTPException(status_code=404, detail="Subject not found")
        
        # Check for dependencies (simplified)
        marks_count = await self.subject_repo.db.marks.count_documents({"subject_id": subject_id})
        if marks_count > 0:
            raise HTTPException(status_code=400, detail=f"Cannot delete subject with {marks_count} marks records")
            
        return await self.subject_repo.delete(subject_id)

def get_subject_service(
    subject_repo: SubjectRepository = Depends(get_subject_repository)
) -> SubjectService:
    return SubjectService(subject_repo)
