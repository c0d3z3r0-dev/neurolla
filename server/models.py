from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean
)

from server.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String,
        unique=True
    )

    name = Column(
        String
    )

    google_uid = Column(
        String,
        unique=True
    )


class BrokerRegistry(Base):
    __tablename__ = "broker_registry"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer
    )

    broker_name = Column(
        String
    )

    credentials_json = Column(
        String
    )

    active = Column(
        Boolean,
        default=True
    )


class BotConfig(Base):
    __tablename__ = "bot_configs"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer
    )

    capital = Column(
        Float
    )

    risk_level = Column(
        String
    )

    confidence_threshold = Column(
        Float
    )

    auto_trade = Column(
        Boolean
    )

class Trade(Base):
    __tablename__ = "trades"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer
    )

    symbol = Column(
        String
    )

    direction = Column(
        String
    )

    entry = Column(
        Float
    )

    tp = Column(
        Float
    )

    sl = Column(
        Float
    )

    confidence = Column(
        Float
    )

    pnl = Column(
        Float,
        default=0
    )

    status = Column(
        String,
        default="OPEN"
    )

class RiskControl(Base):
    __tablename__ = "risk_controls"

    id = Column(
        Integer,
        primary_key=True
    )

    user_id = Column(
        Integer
    )

    daily_loss_limit = Column(
        Float
    )

    max_trades_per_day = Column(
        Integer
    )

    max_drawdown = Column(
        Float
    )

    emergency_stop = Column(
        Boolean,
        default=False
    )