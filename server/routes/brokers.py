from fastapi import APIRouter
from server.database import SessionLocal
from server.models import BrokerRegistry
from server.broker_validation import (
    DerivValidator
)

router = APIRouter()


@router.post("/broker/register")
def register_broker(payload: dict):
    db = SessionLocal()

    broker_name = payload[
        "broker_name"
    ]

    credentials = payload[
        "credentials"
    ]

    if broker_name == "deriv":
        validator = DerivValidator()

        valid, result = validator.validate(
            credentials["api_token"]
        )

        if not valid:
            return {
                "status": "invalid token",
                "error": result
            }

    broker = BrokerRegistry(
        user_id=payload["user_id"],
        broker_name=broker_name,
        credentials_json=str(
            credentials
        )
    )

    db.add(broker)
    db.commit()

    return {
        "status": "broker registered"
    }