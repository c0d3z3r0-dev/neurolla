from fastapi import APIRouter
from server.auth import verify_google_token
from server.database import SessionLocal
from server.models import User

router = APIRouter()


@router.post("/auth/google")
def google_auth(payload: dict):
    db = SessionLocal()

    decoded = verify_google_token(
        payload["id_token"]
    )

    email = decoded["email"]
    name = decoded.get(
        "name",
        "Unknown"
    )
    uid = decoded["uid"]

    existing = db.query(User).filter(
        User.google_uid == uid
    ).first()

    if existing:
        return {
            "status": "login successful",
            "user_id": existing.id
        }

    user = User(
        email=email,
        name=name,
        google_uid=uid
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "status": "account created",
        "user_id": user.id
    }