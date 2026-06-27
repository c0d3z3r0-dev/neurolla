import os
import jwt
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException

# All secrets come from the environment, never hardcoded, so the same
# code runs unchanged across dev/staging/production.
JWT_SECRET = os.environ.get("NEUROLLA_JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
FIREBASE_CREDENTIALS_PATH = os.environ.get(
    "FIREBASE_CREDENTIALS_PATH", "firebase-admin.json"
)

_firebase_app = None


def _get_firebase_app():
    # Firebase is only initialized the first time it's actually needed
    # (during a Google login), not at import time. This means importing
    # server.auth - which every other route module does transitively -
    # no longer crashes in environments without firebase-admin.json,
    # such as this offline editing/testing environment.
    global _firebase_app

    if _firebase_app is None:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)

    return _firebase_app


def verify_google_token(id_token):
    _get_firebase_app()
    decoded_token = auth.verify_id_token(id_token)
    return decoded_token


def issue_session_token(user_id):
    if not JWT_SECRET:
        raise RuntimeError(
            "NEUROLLA_JWT_SECRET is not set. Refusing to issue an "
            "unsigned session token."
        )

    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def require_user(authorization: str = Header(default=None)):
    """
    FastAPI dependency: every protected route declares
    `user_id: int = Depends(require_user)` and gets back the verified
    caller's user_id, instead of trusting a user_id passed in the
    request body or path (which any caller could spoof).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()

    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="Server auth is not configured")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token")

    return payload["user_id"]
