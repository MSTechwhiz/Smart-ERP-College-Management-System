from __future__ import annotations
from typing import Tuple
from ..core.database import get_db

def calculate_grade(total: float) -> Tuple[str, float]:
    """Calculate grade and grade point based on total marks"""
    if total >= 90:
        return "O", 10.0
    elif total >= 80:
        return "A+", 9.0
    elif total >= 70:
        return "A", 8.0
    elif total >= 60:
        return "B+", 7.0
    elif total >= 55:
        return "B", 6.0
    elif total >= 50:
        return "C", 5.0
    elif total >= 40:
        return "P", 4.0
    else:
        return "F", 0.0

async def calculate_cgpa(student_id: str) -> float:
    """Calculate CGPA for a student"""
    db = get_db()
    marks_list = await db.marks.find(
        {"student_id": student_id, "is_locked": True, "grade_point": {"$ne": None}},
        {"_id": 0}
    ).to_list(None)
    
    if not marks_list:
        return 0.0
    
    total_credits = 0
    total_grade_points = 0
    
    for mark in marks_list:
        subject = await db.subjects.find_one({"id": mark["subject_id"]}, {"_id": 0, "credits": 1})
        if subject:
            credits = subject.get("credits", 0)
            total_credits += credits
            total_grade_points += mark.get("grade_point", 0.0) * credits
    
    return round(total_grade_points / total_credits, 2) if total_credits > 0 else 0.0
