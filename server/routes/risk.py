from fastapi import APIRouter
from server.database import SessionLocal
from server.models import RiskControl

router = APIRouter()


@router.post("/risk/save")
def save_risk(payload: dict):
    db = SessionLocal()

    risk = RiskControl(
        user_id=payload["user_id"],
        daily_loss_limit=payload[
            "daily_loss_limit"
        ],
        max_trades_per_day=payload[
            "max_trades_per_day"
        ],
        max_drawdown=payload[
            "max_drawdown"
        ],
        emergency_stop=False
    )

    db.add(risk)
    db.commit()

    return {
        "status": "risk saved"
    }


@router.post("/risk/emergency-stop")
def emergency_stop(payload: dict):
    db = SessionLocal()

    risk = db.query(
        RiskControl
    ).filter(
        RiskControl.user_id ==
        payload["user_id"]
    ).first()

    if risk:
        risk.emergency_stop = True
        db.commit()

    return {
        "status": "bot halted"
    }