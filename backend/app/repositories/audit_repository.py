from typing import List, Optional, Dict, Any
from ..core.database import get_db

from ..utils.mongo_utils import clean_mongo_doc

class AuditRepository:
    def __init__(self):
        self.db = get_db()

    async def get_logs(self, query: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        logs = await self.db.audit_logs_enhanced.find(query, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(None)
        return clean_mongo_doc(logs)

    async def count_logs(self, query: Dict[str, Any]) -> int:
        return await self.db.audit_logs_enhanced.count_documents(query)

    async def get_all_logs(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        logs = await self.db.audit_logs_enhanced.find(query, {"_id": 0}).sort("timestamp", -1).to_list(None)
        return clean_mongo_doc(logs)
