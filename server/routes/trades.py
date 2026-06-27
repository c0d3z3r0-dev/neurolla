from fastapi import APIRouter
from server.database import SessionLocal
from server.models import Trade

router = APIRouter()


@router.get("/trades/{user_id}")
def get_trades(user_id: int):
    db = SessionLocal()

    trades = db.query(
        Trade
    ).filter(
        Trade.user_id == user_id
    ).all()

    return trades


@router.get("/trades/open/{user_id}")
def open_trades(user_id: int):
    db = SessionLocal()

    trades = db.query(
        Trade
    ).filter(
        Trade.user_id == user_id,
        Trade.status == "OPEN"
    ).all()

    return trades


@router.get("/trades/closed/{user_id}")
def closed_trades(user_id: int):
    db = SessionLocal()

    trades = db.query(
        Trade
    ).filter(
        Trade.user_id == user_id,
        Trade.status == "CLOSED"
    ).all()

    return trades