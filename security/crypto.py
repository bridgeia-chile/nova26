"""
Security Crypto Layer
Encrypted storage utilities for soul db secrets.
"""
from cryptography.fernet import Fernet
import os
import base64

class CryptoManager:
    def __init__(self):
        # We derive a deterministic key from owner_id or a fixed salt for portability 
        # in the SOUL_DB. In production, this needs a safer master password prompt.
        master_secret = os.getenv("OWNER_TELEGRAM_ID", "nova_default_secret_key_1234")
        padded_secret = master_secret.ljust(32, 'a')[:32].encode('utf-8')
        self.key = base64.urlsafe_b64encode(padded_secret)
        self.cipher = Fernet(self.key)

    def encrypt_sensitive(self, data: str) -> str:
        """Encrypts data for DB storage."""
        if not data: return data
        return self.cipher.encrypt(data.encode('utf-8')).decode('utf-8')

    def decrypt_sensitive(self, encrypted_data: str) -> str:
        """Decrypts data from DB storage."""
        if not encrypted_data: return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
        except Exception:
            return encrypted_data # Return as-is if decrypt fails (e.g. unencrypted legacy)
