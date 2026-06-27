import os
import json
from cryptography.fernet import Fernet

# A single Fernet key, read from the environment, encrypts every broker
# credential blob at rest. Without this, broker API tokens were being
# stored as plain str(dict) in the database - readable by anyone with
# DB access or a backup file.
_ENCRYPTION_KEY = os.environ.get("NEUROLLA_ENCRYPTION_KEY")

_fernet = None


def _get_fernet():
    global _fernet

    if _fernet is None:
        if not _ENCRYPTION_KEY:
            raise RuntimeError(
                "NEUROLLA_ENCRYPTION_KEY is not set. Refusing to store "
                "broker credentials unencrypted. Generate one with: "
                "python -c \"from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())\""
            )
        _fernet = Fernet(_ENCRYPTION_KEY.encode())

    return _fernet


def encrypt_credentials(credentials: dict) -> str:
    raw = json.dumps(credentials).encode()
    return _get_fernet().encrypt(raw).decode()


def decrypt_credentials(token: str) -> dict:
    raw = _get_fernet().decrypt(token.encode())
    return json.loads(raw.decode())
