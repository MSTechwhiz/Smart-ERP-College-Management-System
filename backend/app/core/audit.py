from __future__ import annotations

from typing import Optional

from fastapi import Request

from .database import get_db
from ..schemas.audit_schema import AuditLog
from ..websocket.manager import manager
from ..utils.mongo_utils import clean_mongo_doc


async def log_audit(
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    before_value: dict = None,
    after_value: dict = None,
    ip_address: str = None,
    module: str = None,
    request: Request = None,
    user_name: str = None,
    user_role: str = None,
):
    """Legacy-compatible audit logging copied from backend/server.py"""
    db = get_db()
    
    # Clean nested ObjectIds
    if before_value:
        before_value = clean_mongo_doc(before_value)
    if after_value:
        after_value = clean_mongo_doc(after_value)

    if not user_name or not user_role:
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "name": 1, "role": 1})
        user_name = user_name or (user.get("name") if user else None)
        user_role = user_role or (user.get("role") if user else None)

    user_agent: Optional[str] = None
    if request:
        ip_address = request.client.host if request.client else ip_address
        user_agent = request.headers.get("user-agent")

    audit = AuditLog(
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        module=module or entity_type,
        before_value=before_value,
        after_value=after_value,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    doc = audit.model_dump()
    doc["timestamp"] = doc["timestamp"].isoformat()
    doc["role"] = user_role
    await db.audit_logs_enhanced.insert_one(doc)

    await manager.broadcast_to_role(
        {
            "type": "audit_log",
            "data": {
                "id": audit.id,
                "user_name": user_name,
                "action": action,
                "entity_type": entity_type,
                "timestamp": doc["timestamp"],
            },
        },
        "principal",
    )

