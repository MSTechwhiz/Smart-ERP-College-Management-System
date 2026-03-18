from typing import List, Optional, Dict, Any
import uuid
import aiohttp
import logging
from datetime import datetime, timezone
from fastapi import HTTPException
from ..repositories.ai_repository import AIRepository
from ..core.config import get_settings

logger = logging.getLogger(__name__)

CHATBOT_SYSTEM_PROMPT = """You are AcademiaOS Assistant, an AI helper for the Smart College ERP System.

You help users with:
1. Navigation - Guide users to different pages and features
2. Feature explanation - Explain what each module does
3. Troubleshooting - Help resolve common issues
4. Role-based guidance - Provide specific help based on user role

Available modules:
- Dashboard: Overview of key metrics
- Students: Student management (Admin/HOD)
- Faculty: Faculty management (Admin)
- Attendance: Mark/view attendance
- Marks: Enter/view marks
- Fees: Fee payment and management
- Documents: Request official documents
- Grievances: Submit and track grievances
- Settings: Theme, password, notifications

Be concise, helpful, and role-aware. If you don't know something, say so."""

class AIService:
    def __init__(self):
        self.repo = AIRepository()
        self.settings = get_settings()

    def get_fallback_response(self, message: str, role: str) -> str:
        message_lower = message.lower()
        if "fee" in message_lower or "payment" in message_lower:
            return "To manage fees, go to the Fees section in your dashboard. Students can view pending fees and make payments. Admins can create fee structures and verify payments."
        elif "attendance" in message_lower:
            return "For attendance, faculty can mark attendance from the Attendance page. Students can view their attendance percentage from their dashboard."
        elif "mark" in message_lower or "grade" in message_lower:
            return "Marks can be entered by faculty under the Marks Entry section. Students can view their marks and calculate CGPA from their dashboard."
        elif "document" in message_lower or "certificate" in message_lower:
            return "To request documents like bonafide or TC, go to Documents section. Your request will be processed by the admin."
        elif "grievance" in message_lower or "complaint" in message_lower:
            return "Submit grievances from the Grievances section. Your complaint will be forwarded through Faculty → HOD → Admin → Principal."
        elif "setting" in message_lower or "theme" in message_lower:
            return "Go to Settings to change theme (Light/Dark), color scheme, password, and notification preferences."
        elif "hello" in message_lower or "hi" in message_lower:
            return f"Hello! I'm AcademiaOS Assistant. As a {role}, how can I help you today?"
        else:
            return f"I can help you navigate the ERP system. As a {role}, you have access to various features. What would you like to know about?"

    async def get_chatbot_knowledge(self, user: Dict[str, Any]) -> str:
        knowledge = []
        if user["role"] == "student":
            data = await self.repo.get_student_knowledge_data(user["id"])
            if data:
                att_pct = (data["attendance_present"] / data["attendance_total"] * 100) if data["attendance_total"] > 0 else 0
                knowledge.append(f"Student Attendance: {att_pct:.2f}% ({data['attendance_present']}/{data['attendance_total']} sessions)")
                knowledge.append(f"Pending Fees: ₹{data['pending_fees']}")
                knowledge.append(f"Current CGPA: {data.get('cgpa', 0.0)}")
                if data.get("dept_name"):
                    knowledge.append(f"Department: {data['dept_name']}")
        elif user["role"] in ["faculty", "hod"]:
            data = await self.repo.get_faculty_knowledge_data(user.get("department_id"))
            if data:
                knowledge.append(f"Your Department: {data['dept_name']}")
                knowledge.append(f"Total students in your department: {data['student_count']}")

        ann_titles = await self.repo.get_recent_announcements(user["role"])
        if ann_titles:
            knowledge.append(f"Recent Announcements: {', '.join(ann_titles)}")
            
        return "\n".join(knowledge)

    async def chat_with_bot(self, message: str, user: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        session = None
        if session_id:
            session = await self.repo.get_chat_session(session_id, user["id"])
        
        if not session:
            session = {
                "id": str(uuid.uuid4()),
                "user_id": user["id"],
                "user_role": user["role"],
                "messages": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            await self.repo.create_chat_session(session)
        
        knowledge = await self.get_chatbot_knowledge(user)
        
        # System Prompt based on role
        role = user.get("role", "student")
        if role == "student":
            system_prompt = f"You are AcademiaOS Assistant, an AI academic helper for students at Sri Balaji Chockalingam Engineering College (ACS Groups, AC Shanmugam, ACS Arun). You provide academic help (explaining concepts like ML, Data Structures, etc.), study guidance, and content generation. STRICT RULES: Refuse hacking, cheating, or ERP security bypass requests. Relevant Student Data: {knowledge}"
        elif role in ["faculty", "hod"]:
            system_prompt = f"You are AcademiaOS Assistant, an AI assistant helping a {role}. You provide academic management help, course planning guidance, and ERP navigation. Relevant Data: {knowledge}"
        else:
            system_prompt = f"You are AcademiaOS Assistant, an AI system navigator for the admin. You help with ERP modules and college information. Relevant Data: {knowledge}"
            
        full_system_prompt = CHATBOT_SYSTEM_PROMPT + "\n\n" + system_prompt
        
        chat_history = []
        for msg in session.get("messages", [])[-10:]:
            chat_history.append({"role": msg["role"], "content": msg["content"]})
        
        messages = [{"role": "system", "content": full_system_prompt}] + chat_history + [{"role": "user", "content": message}]
        
        assistant_response = None
        
        # 1. Try Local Ollama
        if not assistant_response:
            try:
                async with aiohttp.ClientSession() as http_session:
                    # Formatting prompt for /api/generate as requested
                    prompt = f"System: {full_system_prompt}\n"
                    for msg in chat_history:
                        prompt += f"{msg['role'].capitalize()}: {msg['content']}\n"
                    prompt += f"User: {message}\nAssistant:"
                    
                    async with http_session.post(
                        self.settings.ollama_url,
                        json={
                            "model": "llama3",
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            assistant_response = data.get("response")
            except Exception as e:
                logger.warning(f"Ollama failed: {e}")

        # 2. Try Groq API
        if not assistant_response and self.settings.groq_api_key:
            try:
                async with aiohttp.ClientSession() as http_session:
                    async with http_session.post(
                        self.settings.groq_api_url,
                        headers={
                            "Authorization": f"Bearer {self.settings.groq_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama3-8b-8192",
                            "messages": messages,
                            "max_tokens": 500,
                            "temperature": 0.7
                        },
                        timeout=aiohttp.ClientTimeout(total=20)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            assistant_response = data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.warning(f"Groq failed: {e}")

        # 3. Try HuggingFace Inference API
        if not assistant_response and self.settings.hf_api_key:
            try:
                # Simple prompt formatting for instruction models
                hf_prompt = f"System: {full_system_prompt}\nUser: {message}\nAssistant:"
                async with aiohttp.ClientSession() as http_session:
                    async with http_session.post(
                        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                        headers={"Authorization": f"Bearer {self.settings.hf_api_key}"},
                        json={"inputs": hf_prompt, "parameters": {"max_new_tokens": 300}},
                        timeout=aiohttp.ClientTimeout(total=15)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            if isinstance(data, list) and len(data) > 0:
                                assistant_response = data[0].get("generated_text", "").replace(hf_prompt, "").strip()
            except Exception as e:
                logger.warning(f"HuggingFace failed: {e}")

        # 4. Fallback to rule-based
        if not assistant_response:
            logger.info("Using fallback response")
            assistant_response = self.get_fallback_response(message, user["role"])
            
        user_msg = {"role": "user", "content": message, "timestamp": datetime.now(timezone.utc).isoformat()}
        assistant_msg = {"role": "assistant", "content": assistant_response, "timestamp": datetime.now(timezone.utc).isoformat()}
        
        await self.repo.update_chat_session(session["id"], [user_msg, assistant_msg])
        
        return {
            "session_id": session["id"],
            "response": assistant_response,
            "timestamp": assistant_msg["timestamp"]
        }

    async def get_chat_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        return await self.repo.get_user_sessions(user_id)

    async def delete_chat_session(self, session_id: str, user_id: str) -> bool:
        return await self.repo.delete_session(session_id, user_id)

    async def get_student_risk_score(self, student_id: str) -> Dict[str, Any]:
        data = await self.repo.get_student_risk_data(student_id)
        if not data:
            raise HTTPException(status_code=404, detail="Student not found")
            
        # Attendance Risk
        total_classes = len(data["attendance"])
        present_classes = len([a for a in data["attendance"] if a["status"] in ["present", "od"]])
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 100
        attendance_risk = max(0, (75 - attendance_percentage) / 75) * 40
        
        # Marks Risk
        total_marks = []
        for m in data["marks"]:
            for exam_type in ["cia1", "cia2", "cia3", "cia4", "model_exam"]:
                if m.get(exam_type):
                    total_marks.append(m[exam_type])
        avg_marks = sum(total_marks) / len(total_marks) if total_marks else 0
        marks_risk = max(0, (50 - avg_marks) / 50) * 35
        
        # Fee Risk
        fee_pending_count = len(data["pending_fees"])
        fee_risk = min(fee_pending_count * 8, 25)
        
        total_risk = attendance_risk + marks_risk + fee_risk
        risk_level = "high" if total_risk >= 60 else "medium" if total_risk >= 30 else "low"
        
        return {
            "student_id": student_id,
            "risk_score": round(total_risk, 2),
            "risk_level": risk_level,
            "factors": {
                "attendance_percentage": round(attendance_percentage, 2),
                "attendance_risk": round(attendance_risk, 2),
                "average_marks": round(avg_marks, 2),
                "marks_risk": round(marks_risk, 2),
                "pending_fees": fee_pending_count,
                "fee_risk": round(fee_risk, 2)
            },
            "recommendations": [
                "Improve attendance" if attendance_percentage < 75 else None,
                "Focus on academics" if avg_marks < 50 else None,
                "Clear pending fees" if fee_pending_count > 0 else None
            ]
        }

    async def get_department_risk_summary(self, user: Dict[str, Any], department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        target_dept = user["department_id"] if user["role"] == "hod" else department_id
        if not target_dept:
            return []
            
        data = await self.repo.get_department_risk_data(target_dept)
        risk_summary = []
        for s in data:
            attendance_pct = (s["attendance_present"] / s["attendance_total"] * 100) if s["attendance_total"] > 0 else 100
            if attendance_pct < 75:
                risk_summary.append({
                    "student_id": s["id"],
                    "roll_number": s["roll_number"],
                    "name": s["name"] or "Unknown",
                    "attendance_percentage": round(attendance_pct, 2),
                    "risk_level": "high" if attendance_pct < 65 else "medium"
                })
        return risk_summary
