from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]  # backend/

# Load backend/.env (same behavior as legacy server.py)
load_dotenv(ROOT_DIR / ".env")


# Anna University Grading System
ANNA_UNIVERSITY_GRADES: dict = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "P": 4,
    "F": 0,
    "U": 0,
    "AB": 0,
    "WH": 0
}

@dataclass(frozen=True)
class Settings:
    mongo_url: str
    db_name: str
    # Security
    jwt_secret: str = "your-secret-key-change-it"
    jwt_refresh_secret: str = "your-refresh-secret-key-change-it"
    encryption_key: str = "production_ready_secret_key_fixed_length_32"
    jwt_algorithm: str = "HS256"
    jwt_access_expiration_minutes: int = 30
    jwt_refresh_expiration_days: int = 7

    redis_url: str = ""
    frontend_url: str = "http://localhost:3000"

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    groq_api_key: str = ""
    groq_api_url: str = "https://api.groq.com/openai/v1/chat/completions"
    ollama_url: str = "http://localhost:11434/api/generate"
    hf_api_key: str = ""

    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_from: str = ""

    uploads_dir: Path = ROOT_DIR / "uploads"
    log_file: Path = ROOT_DIR / "app.log"
    
    @property
    def razorpay_client(self):
        if self.razorpay_key_id and self.razorpay_key_secret:
            import razorpay
            return razorpay.Client(auth=(self.razorpay_key_id, self.razorpay_key_secret))
        return None


def get_settings() -> Settings:
    # Keep the same env var names/expectations as legacy server.py
    return Settings(
        mongo_url=os.environ["MONGO_URL"],
        db_name=os.environ["DB_NAME"],
        jwt_secret=os.environ.get("JWT_SECRET", "academia-erp-secret-key-2024"),
        jwt_refresh_secret=os.environ.get("JWT_REFRESH_SECRET", "academia-erp-refresh-secret-key-2024"),
        jwt_algorithm=os.environ.get("JWT_ALGORITHM", "HS256"),
        jwt_access_expiration_minutes=int(os.environ.get("JWT_ACCESS_EXPIRATION_MINUTES", "30")),
        jwt_refresh_expiration_days=int(os.environ.get("JWT_REFRESH_EXPIRATION_DAYS", "7")),
        redis_url=os.environ.get("REDIS_URL", ""),
        frontend_url=os.environ.get("FRONTEND_URL", "http://localhost:3000,http://localhost:5173"),
        razorpay_key_id=os.environ.get("RAZORPAY_KEY_ID", ""),
        razorpay_key_secret=os.environ.get("RAZORPAY_KEY_SECRET", ""),
        groq_api_key=os.environ.get("GROQ_API_KEY", ""),
        ollama_url=os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
        hf_api_key=os.environ.get("HF_API_KEY", ""),
        email_host=os.environ.get("EMAIL_HOST", "smtp.gmail.com"),
        email_port=int(os.environ.get("EMAIL_PORT", "587")),
        email_user=os.environ.get("EMAIL_USER", ""),
        email_password=os.environ.get("EMAIL_PASSWORD", ""),
        email_from=os.environ.get("EMAIL_FROM", os.environ.get("EMAIL_USER", "")),
    )

