from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.models import BrokerRegistry
from server.broker_validation import DerivValidator
from server.crypto_utils import encrypt_credentials
from server.auth import require_user

router = APIRouter()


@router.post("/broker/register")
def register_broker(
    payload: dict,
    user_id: int = Depends(require_user),
    db: Session = Depends(get_db)
):
    broker_name = payload["broker_name"]
    credentials = payload["credentials"]

    if broker_name == "deriv":
        validator = DerivValidator()

        valid, result = validator.validate(credentials["api_token"])

        if not valid:
            return {
                "status": "invalid token",
                "error": result
            }

    broker = BrokerRegistry(
        user_id=user_id,
        broker_name=broker_name,
        credentials_json=encrypt_credentials(credentials)
    )

    db.add(broker)
    db.commit()

    return {
        "status": "broker registered"
    }
