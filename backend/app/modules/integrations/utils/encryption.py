"""Master token encryption utilities using Fernet symmetric encryption.

Deliberately self-contained (not shared with app.modules.ai.utils.encryption):
a Keep master token is a full Google account credential, broader in scope than
an OpenRouter API key, so it uses its own encryption key (KEEP_TOKEN_ENCRYPTION_KEY)
to keep rotation/blast-radius independent from the AI module's key.
"""

import base64

from cryptography.fernet import Fernet

from app.core.config import settings
from app.modules.integrations.exceptions import KeepEncryptionError


def get_keep_cipher() -> Fernet:
    """Get Fernet cipher from settings.

    Returns:
        Fernet cipher instance

    Raises:
        KeepEncryptionError: If encryption key is not configured
    """
    key = settings.keep.token_encryption_key
    if not key:
        raise KeepEncryptionError("KEEP_TOKEN_ENCRYPTION_KEY not configured in settings")

    try:
        return Fernet(key)
    except Exception as e:
        raise KeepEncryptionError(f"Invalid encryption key: {e}") from e


def encrypt_master_token(token: str) -> str:
    """Encrypt a Keep master token using Fernet.

    Args:
        token: Plain text master token

    Returns:
        Base64-encoded encrypted token

    Raises:
        KeepEncryptionError: If encryption fails
    """
    try:
        cipher = get_keep_cipher()
        encrypted_bytes = cipher.encrypt(token.encode())
        return base64.b64encode(encrypted_bytes).decode()
    except Exception as e:
        raise KeepEncryptionError(f"Master token encryption failed: {e}") from e


def decrypt_master_token(encrypted_token: str) -> str:
    """Decrypt an encrypted Keep master token.

    Args:
        encrypted_token: Base64-encoded encrypted token

    Returns:
        Plain text master token

    Raises:
        KeepEncryptionError: If decryption fails
    """
    try:
        cipher = get_keep_cipher()
        encrypted_bytes = base64.b64decode(encrypted_token)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    except Exception as e:
        raise KeepEncryptionError(f"Master token decryption failed: {e}") from e
