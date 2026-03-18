from typing import List, Optional, Dict, Any
import csv
import io
from datetime import datetime
from fastapi.responses import StreamingResponse
from ..repositories.audit_repository import AuditRepository

class AuditService:
    def __init__(self):
        self.repo = AuditRepository()

    def _build_query(
        self, 
        module: Optional[str] = None, 
        action: Optional[str] = None, 
        role: Optional[str] = None, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        query = {}
        if module:
            query["module"] = module
        if action:
            query["action"] = action
        if role:
            query["role"] = role
        if start_date:
            query["timestamp"] = {"$gte": start_date}
        if end_date:
            if "timestamp" in query:
                query["timestamp"]["$lte"] = end_date
            else:
                query["timestamp"] = {"$lte": end_date}
        return query

    async def get_audit_logs(
        self, 
        module: Optional[str] = None, 
        action: Optional[str] = None, 
        role: Optional[str] = None, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        query = self._build_query(module, action, role, start_date, end_date)
        total = await self.repo.count_logs(query)
        logs = await self.repo.get_logs(query, skip, limit)
        return {"total": total, "logs": logs}

    async def export_audit_logs(
        self, 
        module: Optional[str] = None, 
        action: Optional[str] = None, 
        role: Optional[str] = None, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> StreamingResponse:
        query = self._build_query(module, action, role, start_date, end_date)
        logs = await self.repo.get_all_logs(query)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Timestamp", "User", "Role", "Module", "Action", "Entity Type", "Entity ID", "Details"])
        
        for log in logs:
            writer.writerow([
                log.get("timestamp"),
                log.get("user_name"),
                log.get("role") or log.get("user_role"),
                log.get("module"),
                log.get("action"),
                log.get("entity_type"),
                log.get("entity_id"),
                log.get("details") or ""
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
