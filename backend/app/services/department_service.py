from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException

from ..repositories.department_repository import DepartmentRepository, get_department_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..core.audit import log_audit


class DepartmentService:
    def __init__(self, dept_repo: DepartmentRepository, user_repo: UserRepository):
        self.dept_repo = dept_repo
        self.user_repo = user_repo

    async def create_department(self, dept_data: Any, admin_user_id: str) -> Dict[str, Any]:
        from ..schemas.department_schema import Department
        dept = Department(**dept_data.model_dump())
        doc = dept.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        await self.dept_repo.create(doc)
        await log_audit(admin_user_id, "create", "department", dept.id, after_value=doc)
        return doc

    async def get_departments(self) -> List[Dict[str, Any]]:
        return await self.dept_repo.list_all()

    async def get_department(self, dept_id: str) -> Optional[Dict[str, Any]]:
        return await self.dept_repo.get_by_id(dept_id)

    async def get_department_analytics(self, dept_id: str) -> Dict[str, Any]:
        """Return analytics for a department — safe defaults when no data exists."""
        db = self.dept_repo.db

        dept = await db.departments.find_one({"id": dept_id}, {"_id": 0})
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")

        # --- Student counts ---
        students = await db.students.find({"department_id": dept_id}, {"_id": 0, "id": 1, "year": 1, "cgpa": 1}).to_list(length=None)
        student_ids = [s["id"] for s in students]
        student_count = len(students)

        # Year-wise breakdown
        year_map = {1: 0, 2: 0, 3: 0, 4: 0}
        cgpa_values = []
        for s in students:
            yr = int(s.get("year") or 0)
            if yr in year_map:
                year_map[yr] += 1
            cgpa = s.get("cgpa")
            if cgpa and cgpa > 0:
                cgpa_values.append(float(cgpa))
        
        avg_cgpa = round(sum(cgpa_values) / len(cgpa_values), 2) if cgpa_values else 0.0

        # --- Faculty count ---
        faculty_count = await db.faculty.count_documents({"department_id": dept_id})

        # --- Attendance ---
        attendance_percentage = 0.0
        if student_ids:
            att_records = await db.attendance.find({"student_id": {"$in": student_ids}}, {"_id": 0, "present": 1, "total": 1}).to_list(length=None)
            if att_records:
                total_p = sum(r.get("present", 0) for r in att_records)
                total_t = sum(r.get("total", 0) for r in att_records)
                attendance_percentage = round((total_p / total_t * 100) if total_t > 0 else 0.0, 1)

        # --- Fee stats ---
        fee_pipeline = [
            {"$match": {"student_id": {"$in": student_ids}}},
            {"$group": {
                "_id": None,
                "expected": {"$sum": "$amount"},
                "collected": {"$sum": {"$cond": [{"$eq": ["$status", "paid"]}, "$amount", 0]}},
                "pending": {"$sum": {"$cond": [{"$ne": ["$status", "paid"]}, "$amount", 0]}}
            }}
        ]
        fees = {"expected": 0, "collected": 0, "pending": 0, "percentage": 0}
        if student_ids:
            fee_agg = await db.fees.aggregate(fee_pipeline).to_list(length=None)
            if fee_agg:
                r = fee_agg[0]
                collected = r.get("collected", 0)
                expected = r.get("expected", 0)
                fees = {
                    "expected": expected,
                    "collected": collected,
                    "pending": r.get("pending", 0),
                    "percentage": round((collected / expected * 100) if expected > 0 else 0, 1)
                }

        # --- Subject performance trend ---
        marks_pipeline = [
            {"$match": {"student_id": {"$in": student_ids}, "total": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$subject_name", "average": {"$avg": "$total"}}},
            {"$sort": {"average": -1}},
            {"$limit": 5}
        ]
        performance_trend = []
        if student_ids:
            marks_agg = await db.marks.aggregate(marks_pipeline).to_list(length=None)
            performance_trend = [
                {"subject": r["_id"], "average": round(r["average"], 1)}
                for r in marks_agg if r["_id"]
            ]

        return {
            "department": dept,
            "stats": {
                "student_count": student_count,
                "faculty_count": faculty_count,
                "attendance_percentage": attendance_percentage,
                "average_cgpa": avg_cgpa,
                "fees": fees,
                "year_distribution": {
                    "year_1": year_map[1],
                    "year_2": year_map[2],
                    "year_3": year_map[3],
                    "year_4": year_map[4],
                }
            },
            "performance_trend": performance_trend
        }

    async def update_department(self, dept_id: str, update_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        dept = await self.dept_repo.get_by_id(dept_id)
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")

        if "hod_id" in update_data:
            hod_id = update_data["hod_id"]
            if hod_id:
                # Update the user role to HOD
                await self.user_repo.db.users.update_one(
                    {"id": hod_id}, 
                    {"$set": {"role": "hod", "department_id": dept_id}}
                )
                from ..utils.cache import cache
                await cache.delete(f"user_profile:{hod_id}")

        if update_data:
            await self.dept_repo.update(dept_id, update_data)
            updated = await self.dept_repo.get_by_id(dept_id)
            await log_audit(admin_user_id, "update", "department", dept_id, before_value=dept, after_value=updated)
            return updated
        return dept

    async def delete_department(self, dept_id: str, admin_user_id: str) -> bool:
        dept = await self.dept_repo.get_by_id(dept_id)
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")

        # Check for associated records
        student_count = await self.user_repo.db.students.count_documents({"department_id": dept_id})
        faculty_count = await self.user_repo.db.faculty.count_documents({"department_id": dept_id})
        subject_count = await self.user_repo.db.subjects.count_documents({"department_id": dept_id})
        
        if student_count > 0 or faculty_count > 0 or subject_count > 0:
            raise HTTPException(
                status_code=400, 
                detail="Department cannot be deleted because it has associated records"
            )

        await self.dept_repo.delete(dept_id)
        await log_audit(admin_user_id, "delete", "department", dept_id, before_value=dept)
        return True


def get_department_service(
    dept_repo: DepartmentRepository = Depends(get_department_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> DepartmentService:
    return DepartmentService(dept_repo, user_repo)
