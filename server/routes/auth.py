from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.auth import verify_google_token, issue_session_token
from server.database import get_db
from server.models import User

router = APIRouter()


@router.post("/auth/google")
def google_auth(payload: dict, db: Session = Depends(get_db)):
    decoded = verify_google_token(payload["id_token"])

    email = decoded["email"]
    name = decoded.get("name", "Unknown")
    uid = decoded["uid"]

    existing = db.query(User).filter(
        User.google_uid == uid
    ).first()

    if existing:
        token = issue_session_token(existing.id)
        return {
            "status": "login successful",
            "user_id": existing.id,
            "session_token": token
        }

    user = User(
        email=email,
        name=name,
        google_uid=uid
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = issue_session_token(user.id)

    return {
        "status": "account created",
        "user_id": user.id,
        "session_token": token
    }
