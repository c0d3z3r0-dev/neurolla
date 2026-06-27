from fastapi import APIRouter
from server.database import SessionLocal
from server.models import BotConfig

router = APIRouter()


@router.post("/config/save")
def save_config(payload: dict):
    db = SessionLocal()

    config = BotConfig(
        user_id=payload["user_id"],
        capital=payload["capital"],
        risk_level=payload["risk_level"],
        confidence_threshold=payload[
            "confidence_threshold"
        ],
        auto_trade=payload["auto_trade"]
    )

    db.add(config)
    db.commit()

    return {
        "status": "config saved"
    }