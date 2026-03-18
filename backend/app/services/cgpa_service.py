from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException

from ..repositories.cgpa_repository import CGPARepository, get_cgpa_repository
from ..core.config import get_settings

class CGPAService:
    def __init__(self, cgpa_repo: CGPARepository):
        self.cgpa_repo = cgpa_repo
        self.settings = get_settings()

    async def calculate_enhanced(self, entries: List[dict], semester: Optional[int], save: bool, user: dict) -> Dict[str, Any]:
        if not entries:
            raise HTTPException(status_code=400, detail="No entries provided")
        
        total_credits = 0
        weighted_sum = 0
        
        for entry in entries:
            grade = entry.get("grade", "U").upper()
            credits = entry.get("credits", 0)
            grade_point = self.settings.ANNA_UNIVERSITY_GRADES.get(grade, 0)
            weighted_sum += grade_point * credits
            total_credits += credits
        
        if total_credits == 0:
            return {"sgpa": 0.0, "total_credits": 0, "entries": entries}
        
        sgpa = round(weighted_sum / total_credits, 2)
        
        result = {
            "sgpa": sgpa,
            "total_credits": total_credits,
            "weighted_sum": weighted_sum,
            "entries": entries
        }
        
        if save and user["role"] == "student":
            student = await self.cgpa_repo.get_student_by_user_id(user["id"])
            if student:
                calc_record = {
                    "id": str(uuid.uuid4()),
                    "student_id": student["id"],
                    "semester": semester,
                    "entries": entries,
                    "sgpa": sgpa,
                    "total_credits": total_credits,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await self.cgpa_repo.save_calculation(calc_record)
                result["saved"] = True
                result["calculation_id"] = calc_record["id"]
        
        return result

    async def get_history(self, user: dict) -> List[Dict[str, Any]]:
        if user["role"] != "student":
            raise HTTPException(status_code=403, detail="Only students can view CGPA history")
        
        student = await self.cgpa_repo.get_student_by_user_id(user["id"])
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        return await self.cgpa_repo.get_history(student["id"])

    async def get_overall_cgpa(self, user: dict) -> Dict[str, Any]:
        if user["role"] != "student":
            raise HTTPException(status_code=403, detail="Only students can view CGPA")
        
        student = await self.cgpa_repo.get_student_by_user_id(user["id"])
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        calculations = await self.cgpa_repo.get_all_calculations(student["id"])
        
        if not calculations:
            return {"cgpa": 0.0, "total_credits": 0, "semesters": 0}
        
        total_credits = 0
        weighted_sum = 0
        
        for calc in calculations:
            total_credits += calc.get("total_credits", 0)
            weighted_sum += calc.get("sgpa", 0) * calc.get("total_credits", 0)
        
        cgpa = round(weighted_sum / total_credits, 2) if total_credits > 0 else 0.0
        
        return {
            "cgpa": cgpa,
            "total_credits": total_credits,
            "semesters": len(calculations),
            "semester_details": calculations
        }

    def calculate_manual(self, grades: List[dict]) -> Dict[str, Any]:
        grade_points = {
            "O": 10.0, "A+": 9.0, "A": 8.0, "B+": 7.0,
            "B": 6.0, "C": 5.0, "P": 4.0, "F": 0.0
        }
        
        total_credits = 0
        total_points = 0
        
        for item in grades:
            credits = item.get("credits", 0)
            grade = item.get("grade", "F")
            gp = grade_points.get(grade, 0)
            total_credits += credits
            total_points += credits * gp
        
        cgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0
        
        return {
            "total_credits": total_credits,
            "total_points": round(total_points, 2),
            "cgpa": cgpa
        }

    async def recalculate_student_cgpa(self, student_id: str) -> Dict[str, Any]:
        from ..utils.grading import calculate_cgpa
        student = await self.cgpa_repo.get_student_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        cgpa = await calculate_cgpa(student_id)
        await self.cgpa_repo.update_student_cgpa(student_id, cgpa)
        
        return {"message": "CGPA recalculated", "student_id": student_id, "new_cgpa": cgpa}

def get_cgpa_service(cgpa_repo: CGPARepository = Depends(get_cgpa_repository)) -> CGPAService:
    return CGPAService(cgpa_repo)
