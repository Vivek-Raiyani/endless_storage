"""
Token encryption/decryption utility.
Google Drive refresh tokens are encrypted at rest using Fernet symmetric encryption.
The key is stored in the environment as TOKEN_ENCRYPTION_KEY.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_fernet():
    """Lazy-load Fernet only if the key is configured."""
    if not settings.TOKEN_ENCRYPTION_KEY:
        return None
    try:
        from cryptography.fernet import Fernet
        return Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())
    except Exception as e:
        logger.error(f"Failed to initialize Fernet: {e}")
        return None


def encrypt_token(plaintext: str) -> str:
    """
    Encrypt a refresh token for storage in the DB.
    Falls back to plaintext if TOKEN_ENCRYPTION_KEY is not set (dev-only).
    """
    f = _get_fernet()
    if f is None:
        logger.warning("TOKEN_ENCRYPTION_KEY not set — storing token as plaintext (dev mode only)")
        return plaintext
    return f.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> Optional[str]:
    """
    Decrypt a stored refresh token.
    Returns None on failure.
    """
    f = _get_fernet()
    if f is None:
        return ciphertext  # dev fallback
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except Exception as e:
        logger.error(f"Failed to decrypt token: {e}")
        return None
