from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
from fastapi import Depends, HTTPException
from ..repositories.announcement_repository import AnnouncementRepository, get_announcement_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..core.audit import log_audit
from ..websocket.manager import manager
from ..schemas.announcement_schema import Announcement

class AnnouncementService:
    def __init__(self, ann_repo: AnnouncementRepository, user_repo: UserRepository):
        self.ann_repo = ann_repo
        self.user_repo = user_repo

    async def create_announcement(self, ann_data: Any, user: Dict[str, Any]) -> Dict[str, Any]:
        ann_dict = ann_data.model_dump()
        if ann_dict.get("publish_date") is None:
            ann_dict["publish_date"] = datetime.now(timezone.utc)
        
        if user["role"] in ["hod", "faculty"] and not ann_dict.get("target_departments"):
            if user.get("department_id"):
                ann_dict["target_departments"] = [user["department_id"]]
        
        announcement = Announcement(**ann_dict, created_by=user["id"])
        doc = announcement.model_dump()
        doc["publish_date"] = doc["publish_date"].isoformat()
        doc["created_at"] = doc["created_at"].isoformat()
        
        await self.ann_repo.create(doc)
        await log_audit(user["id"], "create", "announcement", announcement.id, None, doc)
        
        # Background task candidate: notifications
        notify_query = {}
        if announcement.target_roles:
            notify_query["role"] = {"$in": announcement.target_roles}
        if announcement.target_departments:
            notify_query["department_id"] = {"$in": announcement.target_departments}
            
        cursor = self.user_repo.db.users.find(notify_query, {"_id": 0, "id": 1, "role": 1})
        
        notifications = []
        async for target in cursor:
            notifications.append({
                "id": str(uuid.uuid4()),
                "user_id": target["id"],
                "role": target["role"],
                "type": "Announcement",
                "title": announcement.title,
                "message": announcement.content[:100] + ("..." if len(announcement.content) > 100 else ""),
                "is_read": False,
                "priority": "normal",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {"announcement_id": announcement.id}
            })
            
            # Batch insert every 500 notifications
            if len(notifications) >= 500:
                await self.ann_repo.create_notifications(notifications)
                notifications = []
        
        if notifications:
            await self.ann_repo.create_notifications(notifications)
            target_roles = announcement.target_roles or ["student", "faculty", "hod", "admin", "principal"]
            for role in target_roles:
                await manager.broadcast_to_role({
                    "type": "announcement_posted",
                    "data": {"id": announcement.id, "title": announcement.title}
                }, role)
                
        return doc

    async def get_announcements(self, user: Dict[str, Any], skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc).isoformat()
        query = {
            "is_active": True, 
            "is_deleted": {"$ne": True}, 
            "publish_date": {"$lte": now}
        }
        
        visible_roles_by_role = {
            "admin": ["admin", "principal", "hod", "faculty", "student"],
            "principal": ["principal", "hod", "faculty", "student"],
            "hod": ["hod", "faculty", "student"],
            "faculty": ["faculty", "student"],
            "student": ["student"],
        }
        visible_roles = visible_roles_by_role.get(user["role"], [user["role"]])

        role_dept_filter = [
            {"target_roles": []},
            {"target_roles": {"$in": visible_roles}},
        ]
        
        if user.get("department_id"):
            query["$and"] = [
                {"$or": role_dept_filter},
                {"$or": [{"target_departments": []}, {"target_departments": user["department_id"]}]}
            ]
        else:
            query["$or"] = role_dept_filter
            
        announcements = await self.ann_repo.list_announcements(query, skip=skip, limit=limit)
        
        # Optimization: Batch fetch creators
        creator_ids = list({a["created_by"] for a in announcements})
        creators = await self.user_repo.db.users.find({"id": {"$in": creator_ids}}, {"_id": 0, "id": 1, "name": 1, "role": 1}).to_list(None)
        creator_map = {c["id"]: c for c in creators}
        
        for ann in announcements:
            c = creator_map.get(ann["created_by"])
            if c:
                ann["created_by_name"] = c["name"]
                ann["created_by_role"] = c["role"]
                
        return announcements

def get_announcement_service(
    ann_repo: AnnouncementRepository = Depends(get_announcement_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> AnnouncementService:
    return AnnouncementService(ann_repo, user_repo)
