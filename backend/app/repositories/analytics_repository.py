from __future__ import annotations

from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..core.database import get_db
from fastapi import Depends

class AnalyticsRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def get_dashboard_counts(self) -> Dict[str, int]:
        total_students = await self.db.students.count_documents({})
        total_faculty = await self.db.faculty.count_documents({})
        total_departments = await self.db.departments.count_documents({})
        return {
            "total_students": total_students,
            "total_faculty": total_faculty,
            "total_departments": total_departments
        }

    async def get_fee_summary(self) -> Dict[str, Any]:
        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = await self.db.fee_payments.aggregate(pipeline).to_list(1)
        total_fee_collected = result[0]["total"] if result else 0
        
        pending_verifications = await self.db.fee_payments.count_documents({"status": "screenshot_uploaded"})
        return {
            "total_fee_collected": total_fee_collected,
            "pending_verifications": pending_verifications
        }

    async def get_workflow_counts(self) -> Dict[str, int]:
        open_grievances = await self.db.grievances.count_documents({"status": {"$ne": "resolved"}})
        pending_documents = await self.db.document_requests.count_documents({"status": {"$nin": ["generated", "collected", "rejected"]}})
        return {
            "open_grievances": open_grievances,
            "pending_documents": pending_documents
        }

    async def get_department_stats(self) -> List[Dict[str, Any]]:
        pipeline = [
            {"$lookup": {
                "from": "students",
                "localField": "id",
                "foreignField": "department_id",
                "as": "student_info"
            }},
            {"$lookup": {
                "from": "faculty",
                "localField": "id",
                "foreignField": "department_id",
                "as": "faculty_info"
            }},
            {"$project": {
                "department": "$name",
                "code": "$code",
                "count": {"$size": "$student_info"},
                "faculty_count": {"$size": "$faculty_info"},
                "_id": 0
            }}
        ]
        return await self.db.departments.aggregate(pipeline).to_list(None)

    async def get_cgpa_distribution(self) -> Dict[str, int]:
        pipeline = [
            {"$project": {
                "grade": {
                    "$switch": {
                        "branches": [
                            {"case": {"$gte": ["$cgpa", 9]}, "then": "O"},
                            {"case": {"$gte": ["$cgpa", 8]}, "then": "A+"},
                            {"case": {"$gte": ["$cgpa", 7]}, "then": "A"},
                            {"case": {"$gte": ["$cgpa", 6]}, "then": "B+"},
                            {"case": {"$gte": ["$cgpa", 5.5]}, "then": "B"},
                            {"case": {"$gte": ["$cgpa", 5]}, "then": "C"},
                            {"case": {"$gte": ["$cgpa", 4]}, "then": "P"}
                        ],
                        "default": "F"
                    }
                }
            }},
            {"$group": {"_id": "$grade", "count": {"$sum": 1}}}
        ]
        results = await self.db.students.aggregate(pipeline).to_list(None)
        distribution = {"O": 0, "A+": 0, "A": 0, "B+": 0, "B": 0, "C": 0, "P": 0, "F": 0}
        for r in results:
            distribution[r["_id"]] = r["count"]
        return distribution

    async def get_all_completed_payments(self) -> List[Dict[str, Any]]:
        return await self.db.fee_payments.find({"status": "completed"}, {"_id": 0, "amount": 1, "payment_date": 1}).to_list(None)

    async def get_active_fee_structures(self) -> List[Dict[str, Any]]:
        return await self.db.fee_structures.find({"is_active": True}, {"_id": 0}).to_list(None)

    async def get_all_departments(self) -> List[Dict[str, Any]]:
        return await self.db.departments.find({}, {"_id": 0}).to_list(None)

    async def get_students_by_query(self, query: dict, projection: dict = {"_id": 0}) -> List[Dict[str, Any]]:
        return await self.db.students.find(query, projection).to_list(None)

    async def get_total_students_count(self) -> int:
        return await self.db.students.count_documents({})

    async def get_attendance_for_students(self, student_ids: List[str], projection: dict = {"_id": 0}) -> List[Dict[str, Any]]:
        return await self.db.attendance.find({"student_id": {"$in": student_ids}}, projection).to_list(None)

    async def get_subject_lite(self, subj_id: str) -> Optional[Dict[str, Any]]:
        return await self.db.subjects.find_one({"id": subj_id}, {"_id": 0, "name": 1, "code": 1})

    async def get_detailed_department_stats(self, dept_id: str) -> Optional[Dict[str, Any]]:
        dept = await self.db.departments.find_one({"id": dept_id}, {"_id": 0})
        if not dept:
            return None

        # Perform complex aggregation to get student count, faculty count, avg cgpa, and attendance in one/two calls
        student_stats_pipeline = [
            {"$match": {"department_id": dept_id}},
            {"$group": {
                "_id": None,
                "student_count": {"$sum": 1},
                "avg_cgpa": {"$avg": "$cgpa"}
            }}
        ]
        student_results = await self.db.students.aggregate(student_stats_pipeline).to_list(1)
        student_stats = student_results[0] if student_results else {"student_count": 0, "avg_cgpa": 0}

        faculty_count = await self.db.faculty.count_documents({"department_id": dept_id})

        # Attendance Aggregation
        attendance_pipeline = [
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$match": {"student.department_id": dept_id}},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "present": {"$sum": {"$cond": [{"$in": ["$status", ["present", "od"]]}, 1, 0]}}
            }}
        ]
        attendance_results = await self.db.attendance.aggregate(attendance_pipeline).to_list(1)
        att_data = attendance_results[0] if attendance_results else {"total": 0, "present": 0}
        attendance_percentage = (att_data["present"] / att_data["total"] * 100) if att_data["total"] > 0 else 100

        # Fees Aggregation
        fee_pipeline = [
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$match": {"student.department_id": dept_id, "status": "completed"}},
            {"$group": {
                "_id": None,
                "collected": {"$sum": "$amount"}
            }}
        ]
        fee_results = await self.db.fee_payments.aggregate(fee_pipeline).to_list(1)
        total_collected = fee_results[0]["collected"] if fee_results else 0

        # Expected fees - assuming all active structures apply
        fee_structures = await self.db.fee_structures.find({"is_active": True}, {"_id": 0, "amount": 1}).to_list(None)
        expected_per_student = sum(f["amount"] for f in fee_structures)
        total_expected = expected_per_student * student_stats["student_count"]

        # Performance Trend (Top 5 subjects in dept)
        perf_pipeline = [
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$match": {"student.department_id": dept_id}},
            {"$group": {
                "_id": "$subject_id",
                "average": {"$avg": "$marks"}
            }},
            {"$sort": {"average": -1}},
            {"$limit": 5},
            {"$lookup": {
                "from": "subjects",
                "localField": "_id",
                "foreignField": "id",
                "as": "subject_info"
            }},
            {"$unwind": "$subject_info"},
            {"$project": {
                "_id": 0,
                "subject": "$subject_info.name",
                "average": {"$round": ["$average", 1]}
            }}
        ]
        performance_trend = await self.db.marks.aggregate(perf_pipeline).to_list(None)

        return {
            "department": dept,
            "stats": {
                "student_count": student_stats["student_count"],
                "faculty_count": faculty_count,
                "attendance_percentage": round(attendance_percentage, 1),
                "average_cgpa": round(student_stats["avg_cgpa"], 2),
                "fees": {
                    "expected": total_expected,
                    "collected": total_collected,
                    "pending": max(0, total_expected - total_collected),
                    "percentage": round(total_collected / total_expected * 100, 1) if total_expected > 0 else 0
                }
            },
            "performance_trend": performance_trend
        }

def get_analytics_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(db)
