from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import RiskControl
from server.auth import require_user

router = APIRouter()


@router.post("/risk/save")
def save_risk(
    payload: dict,
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    risk = RiskControl(
        user_id=user_id,
        daily_loss_limit=payload["daily_loss_limit"],
        max_trades_per_day=payload["max_trades_per_day"],
        max_drawdown=payload["max_drawdown"],
        emergency_stop=False
    )

    db.add(risk)
    db.commit()

    return {
        "status": "risk saved"
    }


@router.post("/risk/emergency-stop")
def emergency_stop(
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    risk = db.query(RiskControl).filter(
        RiskControl.user_id == user_id
    ).first()

    if risk:
        risk.emergency_stop = True
        db.commit()

    return {
        "status": "bot halted"
    }
