from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import User
from server.auth import require_user

router = APIRouter()


@router.get("/users/me")
def get_me(
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    # Returns only the caller's own record - never the full user table,
    # which would leak every other user's email and google_uid.
    user = db.query(User).filter(User.id == user_id).first()
    return user
