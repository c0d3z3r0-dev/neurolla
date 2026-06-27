from server.database import SessionLocal
from server.models import Trade
from datetime import datetime, timezone


class TradeJournal:
    def __init__(self):
        self.db = SessionLocal()

    def log_trade(
        self,
        user_id,
        signal_packet
    ):
        trade = Trade(
            user_id=user_id,
            symbol=signal_packet["symbol"],
            direction=signal_packet["signal"],
            entry=signal_packet.get(
                "entry",
                0
            ),
            tp=signal_packet.get(
                "tp",
                0
            ),
            sl=signal_packet.get(
                "sl",
                0
            ),
            confidence=signal_packet[
                "confidence"
            ],
            volume=signal_packet.get(
                "volume",
                0.0
            )
        )

        self.db.add(trade)
        self.db.commit()

    def close_trade(
        self,
        trade_id,
        pnl
    ):
        trade = self.db.query(
            Trade
        ).filter(
            Trade.id == trade_id
        ).first()

        if trade:
            trade.pnl = pnl
            trade.status = "CLOSED"
            trade.closed_at = datetime.now(timezone.utc)

            self.db.commit()

    def close(self):
        self.db.close()