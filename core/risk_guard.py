import os
from datetime import datetime, timezone

from server.database import SessionLocal
from server.models import RiskControl, Trade
from notifications.notifier import NeuroLLaNotifier


class RiskGuard:
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = SessionLocal()

        # Telegram credentials come from the environment, never hardcoded,
        # so this class works the same in dev and in production.
        self.notifier = NeuroLLaNotifier(
            telegram_config={
                "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
                "chat_id": os.environ.get("TELEGRAM_CHAT_ID", "")
            }
        )

    def _todays_trades(self):
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        return self.db.query(Trade).filter(
            Trade.user_id == self.user_id,
            Trade.opened_at >= today_start
        ).all()

    def today_pnl(self):
        # Only CLOSED trades have a realized pnl; open trades contribute 0
        # until they close, which is the correct behavior for a daily
        # drawdown check (we don't want to double count unrealized moves
        # the broker hasn't confirmed yet).
        trades = self._todays_trades()
        return sum(t.pnl for t in trades if t.status == "CLOSED")

    def trade_count(self):
        return len(self._todays_trades())

    def can_trade(self):
        controls = self.db.query(RiskControl).filter(
            RiskControl.user_id == self.user_id
        ).first()

        if not controls:
            return True

        if controls.emergency_stop:
            return False

        if abs(self.today_pnl()) >= controls.daily_loss_limit:
            self.notifier.alert("RiskGuard blocked trading: daily loss limit reached.")
            return False

        if self.trade_count() >= controls.max_trades_per_day:
            self.notifier.alert("RiskGuard blocked trading: max trades per day reached.")
            return False

        return True

    def close(self):
        self.db.close()
