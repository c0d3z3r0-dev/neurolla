from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import BotConfig
from server.auth import require_user

router = APIRouter()


@router.post("/config/save")
def save_config(
    payload: dict,
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    config = BotConfig(
        user_id=user_id,
        capital=payload["capital"],
        risk_level=payload["risk_level"],
        confidence_threshold=payload["confidence_threshold"],
        auto_trade=payload["auto_trade"]
    )

    db.add(config)
    db.commit()

    return {
        "status": "config saved"
    }
