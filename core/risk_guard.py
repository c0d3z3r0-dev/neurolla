from server.database import SessionLocal
from server.models import (
    RiskControl,
    Trade
)
from notifications.notifier import (
    NeuroLLaNotifier
)


class RiskGuard:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = SessionLocal()
        self.notifier = NeuroLLaNotifier(
            telegram_config={
                 "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
                 "chat_id": "YOUR_CHAT_ID"
            }
        )

    def get_controls(self):
        return self.db.query(
            RiskControl
        ).filter(
            RiskControl.user_id == self.user_id
        ).first()

    def today_pnl(self):
        trades = self.db.query(
            Trade
        ).filter(
            Trade.user_id == self.user_id
        ).all()

        return sum(
            t.pnl for t in trades
        )

    def trade_count(self):
        trades = self.db.query(
            Trade
        ).filter(
            Trade.user_id == self.user_id
        ).all()

        return len(trades)

    def can_trade(self):
        controls = self.get_controls()

        if not controls:
            return True

        if controls.emergency_stop:
            return False

        if abs(
            self.today_pnl()
        ) >= controls.daily_loss_limit:
            return False

        if self.trade_count() >= (
            controls.max_trades_per_day
        ):

        self.notifier.alert(
             "RiskGuard blocked trading."
        )
            return False

        return True