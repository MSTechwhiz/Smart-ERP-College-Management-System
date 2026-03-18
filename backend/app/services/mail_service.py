from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from ..repositories.mail_repository import MailRepository, get_mail_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..websocket.manager import manager
from ..schemas.mail_schema import Mail

class MailService:
    def __init__(self, mail_repo: MailRepository, user_repo: UserRepository):
        self.mail_repo = mail_repo
        self.user_repo = user_repo

    async def send_mail(self, data: Any, user: Dict[str, Any]) -> Dict[str, Any]:
        mail = Mail(
            from_user_id=user["id"],
            **data.model_dump()
        )
        doc = mail.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        await self.mail_repo.create(doc)
        
        if not data.is_draft:
            try:
                await manager.send_personal_message({
                    "type": "mail_received",
                    "data": {"mail_id": mail.id, "subject": data.subject, "from": user.get("name", "Unknown")}
                }, data.to_user_id)
            except Exception as e:
                # Log error but don't fail the mail send
                print(f"Failed to send websocket notification for mail: {e}")
            
        return doc

    async def get_inbox(self, user_id: str) -> List[Dict[str, Any]]:
        query = {"to_user_id": user_id, "is_draft": False, "is_archived": False}
        mails = await self.mail_repo.list_mails(query)
        
        # Batch enrich sender info
        sender_ids = list({m["from_user_id"] for m in mails})
        senders = await self.user_repo.db.users.find({"id": {"$in": sender_ids}}, {"id": 1, "name": 1, "email": 1, "role": 1}).to_list(None)
        sender_map = {s["id"]: s for s in senders}
        
        for m in mails:
            s = sender_map.get(m["from_user_id"])
            if s:
                m["from_name"] = s["name"]
                m["from_email"] = s["email"]
                m["from_role"] = s["role"]
        return mails

    async def get_sent_mails(self, user_id: str) -> List[Dict[str, Any]]:
        query = {"from_user_id": user_id, "is_draft": False}
        mails = await self.mail_repo.list_mails(query)
        
        # Batch enrich recipient info
        recipient_ids = list({m["to_user_id"] for m in mails})
        recipients = await self.user_repo.db.users.find({"id": {"$in": recipient_ids}}, {"id": 1, "name": 1, "email": 1}).to_list(None)
        recipient_map = {r["id"]: r for r in recipients}
        
        for m in mails:
            r = recipient_map.get(m["to_user_id"])
            if r:
                m["to_name"] = r["name"]
                m["to_email"] = r["email"]
        return mails

    async def mark_read(self, mail_id: str, user_id: str) -> bool:
        mail = await self.mail_repo.get_by_id(mail_id, user_id)
        if not mail: raise HTTPException(status_code=404, detail="Mail not found")
        return await self.mail_repo.update(mail_id, {"is_read": True})

    async def archive_mail(self, mail_id: str, user_id: str) -> bool:
        mail = await self.mail_repo.get_by_id(mail_id, user_id)
        if not mail: raise HTTPException(status_code=404, detail="Mail not found")
        return await self.mail_repo.update(mail_id, {"is_archived": True})

def get_mail_service(
    mail_repo: MailRepository = Depends(get_mail_repository),
    user_repo: UserRepository = Depends(get_user_repository)
) -> MailService:
    return MailService(mail_repo, user_repo)
