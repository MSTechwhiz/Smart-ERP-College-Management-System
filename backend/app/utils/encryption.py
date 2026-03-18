import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ..core.config import get_settings

settings = get_settings()

class Encryption:
    _fernet = None

    @classmethod
    def get_fernet(cls):
        if cls._fernet is None:
            key = getattr(settings, "encryption_key", None)
            if not key or key == "changeme":
                # Fallback or development key - in production this must be set
                key = "production_ready_secret_key_fixed_length_32"
            
            # Ensure key is 32 bytes and base64 encoded for Fernet
            key_bytes = key.encode()
            if len(key_bytes) < 32:
                key_bytes = key_bytes.ljust(32, b"0")
            elif len(key_bytes) > 32:
                key_bytes = key_bytes[:32]
                
            cls._fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
        return cls._fernet

    @classmethod
    def encrypt(cls, data: str) -> str:
        if not data:
            return data
        f = cls.get_fernet()
        return f.encrypt(data.encode()).decode()

    @classmethod
    def decrypt(cls, token: str) -> str:
        if not token:
            return token
        try:
            f = cls.get_fernet()
            return f.decrypt(token.encode()).decode()
        except Exception:
            # If decryption fails (e.g. data was already plain text or key changed), return as is
            return token
