from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import Depends
from ..repositories.analytics_repository import AnalyticsRepository, get_analytics_repository
from ..utils.cache import cache

class AnalyticsService:
    def __init__(self, analytics_repo: AnalyticsRepository):
        self.analytics_repo = analytics_repo

    async def get_dashboard_analytics(self) -> Dict[str, Any]:
        cache_key = "dashboard_stats"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        counts = await self.analytics_repo.get_dashboard_counts()
        fee_summary = await self.analytics_repo.get_fee_summary()
        workflows = await self.analytics_repo.get_workflow_counts()
        dept_stats = await self.analytics_repo.get_department_stats()
        cgpa_dist = await self.analytics_repo.get_cgpa_distribution()

        result = {
            **counts,
            **fee_summary,
            **workflows,
            "department_wise_students": dept_stats,
            "cgpa_distribution": cgpa_dist
        }
        
        await cache.set(cache_key, result, ttl=300)
        return result

    async def get_fee_analytics(self, department_id: Optional[str]) -> Dict[str, Any]:
        cache_key = f"fee_analytics_{department_id or 'all'}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data
            
        fee_summary = await self.analytics_repo.get_fee_summary()
        total_collected = fee_summary["total_fee_collected"]
        
        fee_structures = await self.analytics_repo.get_active_fee_structures()
        total_expected_per_student = sum(f["amount"] for f in fee_structures)
        
        dept_collection = []
        departments = await self.analytics_repo.get_all_departments()
        
        # This could be further optimized with a single aggregation, but for now let's use the repo
        for dept in departments:
            # We already have detailed logic in get_detailed_department_stats, but for the overview:
            pipeline = [
                {"$lookup": {
                    "from": "students",
                    "localField": "student_id",
                    "foreignField": "id",
                    "as": "student"
                }},
                {"$unwind": "$student"},
                {"$match": {"student.department_id": dept["id"], "status": "completed"}},
                {"$group": {"_id": None, "collected": {"$sum": "$amount"}, "student_count": {"$addToSet": "$student_id"}}}
            ]
            results = await self.analytics_repo.db.fee_payments.aggregate(pipeline).to_list(1)
            data = results[0] if results else {"collected": 0, "student_count": []}
            
            # Get actual student count for expected calculation
            student_count = await self.analytics_repo.db.students.count_documents({"department_id": dept["id"]})
            
            dept_collection.append({
                "department": dept["name"],
                "code": dept["code"],
                "collected": data["collected"],
                "student_count": student_count
            })
        
        # Monthly trend - also better as aggregation
        trend_pipeline = [
            {"$match": {"status": "completed"}},
            {"$project": {
                "amount": 1,
                "month": {"$dateToString": {"format": "%b %Y", "date": {"$dateFromString": {"dateString": "$payment_date"}}}}
            }},
            {"$group": {"_id": "$month", "amount": {"$sum": "$amount"}}},
            {"$sort": {"_id": 1}},
            {"$limit": 6}
        ]
        trend_results = await self.analytics_repo.db.fee_payments.aggregate(trend_pipeline).to_list(None)
        monthly_trend = [{"month": r["_id"], "amount": r["amount"]} for r in trend_results]
        
        total_students = await self.analytics_repo.get_total_students_count()
        total_expected = total_expected_per_student * total_students if total_students else 0
        
        result = {
            "total_collected": total_collected,
            "total_expected": total_expected,
            "collection_percentage": round(total_collected / total_expected * 100, 2) if total_expected > 0 else 0,
            "department_wise": dept_collection,
            "monthly_trend": monthly_trend
        }
        
        await cache.set(cache_key, result, ttl=600)
        return result

    async def get_attendance_analytics(self, department_id: Optional[str], user_role: str, user_dept_id: Optional[str]) -> Dict[str, Any]:
        match_query = {}
        if user_role == "hod":
            match_query["student.department_id"] = user_dept_id
        elif department_id:
            match_query["student.department_id"] = department_id
        
        cache_key = f"att_analytics_{department_id or 'all'}_{user_role}_{user_dept_id or ''}"
        cached = await cache.get(cache_key)
        if cached: return cached
        
        pipeline = [
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$match": match_query},
            {"$group": {
                "_id": None,
                "total": {"$sum": 1},
                "present": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}},
                "absent": {"$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}},
                "od": {"$sum": {"$cond": [{"$eq": ["$status", "od"]}, 1, 0]}}
            }}
        ]
        
        results = await self.analytics_repo.db.attendance.aggregate(pipeline).to_list(1)
        stats = results[0] if results else {"total": 0, "present": 0, "absent": 0, "od": 0}
        
        # Subject wise
        subj_pipeline = [
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "id",
                "as": "student"
            }},
            {"$unwind": "$student"},
            {"$match": match_query},
            {"$group": {
                "_id": "$subject_id",
                "total": {"$sum": 1},
                "present": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}},
                "absent": {"$sum": {"$cond": [{"$eq": ["$status", "absent"]}, 1, 0]}},
                "od": {"$sum": {"$cond": [{"$eq": ["$status", "od"]}, 1, 0]}}
            }},
            {"$lookup": {
                "from": "subjects",
                "localField": "_id",
                "foreignField": "id",
                "as": "subject_info"
            }},
            {"$unwind": "$subject_info"},
            {"$project": {
                "_id": 0,
                "subject_id": "$_id",
                "subject_name": "$subject_info.name",
                "subject_code": "$subject_info.code",
                "total": 1,
                "present": 1,
                "absent": 1,
                "od": 1,
                "percentage": {
                    "$cond": [
                        {"$gt": ["$total", 0]},
                        {"$round": [{"$multiply": [{"$divide": [{"$add": ["$present", "$od"]}, "$total"]}, 100]}, 2]},
                        0
                    ]
                }
            }}
        ]
        subject_list = await self.analytics_repo.db.attendance.aggregate(subj_pipeline).to_list(None)
        
        res = {
            "total_records": stats["total"],
            "present": stats["present"],
            "absent": stats["absent"],
            "od": stats["od"],
            "attendance_percentage": round((stats["present"] + stats["od"]) / stats["total"] * 100, 2) if stats["total"] > 0 else 0,
            "subject_wise": subject_list
        }
        await cache.set(cache_key, res, ttl=300)
        return res

    async def get_risk_analytics(self, department_id: Optional[str], user_role: str, user_dept_id: Optional[str]) -> List[Dict[str, Any]]:
        match_query = {}
        if user_role == "hod":
            match_query["department_id"] = user_dept_id
        elif department_id:
            match_query["department_id"] = department_id
            
        # Comprehensive aggregation for risk analysis
        pipeline = [
            {"$match": match_query},
            {"$lookup": {
                "from": "attendance",
                "localField": "id",
                "foreignField": "student_id",
                "as": "attendance"
            }},
            {"$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "id",
                "as": "user"
            }},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "student_id": "$id",
                "roll_number": "$roll_number",
                "name": {"$ifNull": ["$user.name", "Unknown"]},
                "email": {"$ifNull": ["$user.email", ""]},
                "cgpa": {"$ifNull": ["$cgpa", 0]},
                "total_att": {"$size": "$attendance"},
                "present_att": {
                    "$size": {
                        "$filter": {
                            "input": "$attendance",
                            "as": "a",
                            "cond": {"$in": ["$$a.status", ["present", "od"]]}
                        }
                    }
                }
            }},
            {"$project": {
                "student_id": 1, "roll_number": 1, "name": 1, "email": 1, "cgpa": 1,
                "attendance_percentage": {
                    "$cond": [
                        {"$gt": ["$total_att", 0]},
                        {"$multiply": [{"$divide": ["$present_att", "$total_att"]}, 100]},
                        100
                    ]
                }
            }},
            # Add risk scoring logic in projection
            {"$addFields": {
                "risk_score": {
                    "$add": [
                        {"$cond": [{"$lt": ["$attendance_percentage", 75]}, 40, {"$cond": [{"$lt": ["$attendance_percentage", 85]}, 20, 0]}]},
                        {"$cond": [{"$lt": ["$cgpa", 5]}, 40, {"$cond": [{"$lt": ["$cgpa", 6]}, 20, 0]}]}
                    ]
                }
            }},
            {"$match": {"risk_score": {"$gt": 20}}},
            {"$addFields": {
                "risk_level": {
                    "$cond": [{"$gte": ["$risk_score", 60]}, "high", {"$cond": [{"$gte": ["$risk_score", 40]}, "medium", "low"]}]
                },
                "risk_factors": {
                    # This part is tricky with purely aggregation if we want specific strings, but let's approximate
                    "$setUnion": [
                        {"$cond": [{"$lt": ["$attendance_percentage", 75]}, ["Low attendance"], {"$cond": [{"$lt": ["$attendance_percentage", 85]}, ["Moderate attendance"], []]}]},
                        {"$cond": [{"$lt": ["$cgpa", 5]}, ["Low CGPA"], {"$cond": [{"$lt": ["$cgpa", 6]}, ["Moderate CGPA"], []]}]}
                    ]
                }
            }},
            {"$sort": {"risk_score": -1}},
            {"$project": {
                "_id": 0, "student_id": 1, "roll_number": 1, "name": 1, "email": 1, 
                "attendance_percentage": {"$round": ["$attendance_percentage", 2]},
                "cgpa": 1, "risk_score": 1, "risk_level": 1, "risk_factors": 1
            }}
        ]

        
        results = await self.analytics_repo.db.students.aggregate(pipeline).to_list(None)
        return results

    async def get_department_analytics(self, department_id: str) -> Dict[str, Any]:
        data = await self.analytics_repo.get_detailed_department_stats(department_id)
        if not data:
            return {"error": "Department not found"}
        return data

def get_analytics_service(
    analytics_repo: AnalyticsRepository = Depends(get_analytics_repository)
) -> AnalyticsService:
    return AnalyticsService(analytics_repo)
