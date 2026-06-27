from fastapi import APIRouter
from server.database import SessionLocal
from server.models import User

router = APIRouter()


@router.post("/users/create")
def create_user(payload: dict):
    db = SessionLocal()

    user = User(
        email=payload["email"],
        name=payload["name"],
        google_uid=payload["google_uid"]
    )

    db.add(user)
    db.commit()

    return {
        "status": "user created"
    }


@router.get("/users")
def get_users():
    db = SessionLocal()

    users = db.query(User).all()

    return users