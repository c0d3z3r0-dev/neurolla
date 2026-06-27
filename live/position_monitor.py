from datetime import datetime, timezone

import MetaTrader5 as mt5

from server.database import SessionLocal
from server.models import Trade


class PositionMonitor:
    """
    Polls MT5 for trades that were OPEN in our database but have since
    closed at the broker, and reconciles them: sets status=CLOSED,
    records realized pnl, and releases the symbol's slot in
    PortfolioManager/ExposureEngine so the same symbol/cluster can be
    traded again.

    Without this, the system can place a trade but has no way to ever
    learn it closed - the cluster stays permanently blocked and the
    Trade row stays OPEN forever, even after MT5 has long since closed
    the position via SL or TP.
    """

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.db = SessionLocal()

    def reconcile(self):
        open_trades = self.db.query(Trade).filter(
            Trade.status == "OPEN"
        ).all()

        for trade in open_trades:
            if not trade.broker_position_id:
                continue

            # For a market order, the resulting position's ticket
            # equals the order ticket recorded at entry, so the same
            # ID identifies both. history_deals_get(position=...)
            # returns every deal (open + close) tied to that position.
            position_id = int(trade.broker_position_id)
            history = mt5.history_deals_get(position=position_id)

            if not history:
                continue

            # A position with only one deal (the opening one) hasn't
            # closed yet at the broker.
            if len(history) < 2:
                continue

            realized_pnl = sum(deal.profit for deal in history)

            trade.pnl = realized_pnl
            trade.status = "CLOSED"
            trade.closed_at = datetime.now(timezone.utc)

            self.portfolio.release_trade(trade.symbol)

            print(f"Reconciled closed trade: {trade.symbol} pnl={realized_pnl:.2f}")

        self.db.commit()

    def close(self):
        self.db.close()
