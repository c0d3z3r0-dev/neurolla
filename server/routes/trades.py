from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import Trade
from server.auth import require_user

router = APIRouter()


@router.get("/trades")
def get_trades(
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    return db.query(Trade).filter(
        Trade.user_id == user_id
    ).all()


@router.get("/trades/open")
def open_trades(
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    return db.query(Trade).filter(
        Trade.user_id == user_id,
        Trade.status == "OPEN"
    ).all()


@router.get("/trades/closed")
def closed_trades(
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    return db.query(Trade).filter(
        Trade.user_id == user_id,
        Trade.status == "CLOSED"
    ).all()
