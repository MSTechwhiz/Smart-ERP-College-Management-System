from typing import List, Optional
from fastapi import APIRouter, Depends
from ..core.security import get_current_user, require_roles
from ..services.ai_service import AIService

router = APIRouter(prefix="/api", tags=["AI Chatbot"])
service = AIService()

@router.post("/chatbot/message", response_model=dict)
async def chat_with_bot(
    message: str,
    session_id: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    return await service.chat_with_bot(message, user, session_id)

@router.get("/chatbot/sessions", response_model=List[dict])
async def get_chat_sessions(user: dict = Depends(get_current_user)):
    return await service.get_chat_sessions(user["id"])

@router.delete("/chatbot/session/{session_id}", response_model=dict)
async def delete_chat_session(session_id: str, user: dict = Depends(get_current_user)):
    await service.delete_chat_session(session_id, user["id"])
    return {"message": "Session deleted"}

@router.get("/ai/risk-score/{student_id}", response_model=dict)
async def get_student_risk_score(
    student_id: str,
    user: dict = Depends(require_roles(["principal", "hod"]))
):
    return await service.get_student_risk_score(student_id)

@router.get("/analytics/risks", response_model=List[dict])
async def get_department_risk_summary(
    department_id: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "hod"]))
):
    return await service.get_department_risk_summary(user, department_id)

