from server.database import SessionLocal
from server.models import Trade
import numpy as np


class NeuroLLaAnalytics:
    """
    All queries are scoped to a single user_id so one user's analytics
    never include another user's trades. Pass user_id=None only for
    operator/admin-level aggregate reporting across all users.
    """

    def __init__(self, user_id=None):
        self.user_id = user_id
        self.db = SessionLocal()

    def all_trades(self):
        query = self.db.query(Trade)

        if self.user_id is not None:
            query = query.filter(Trade.user_id == self.user_id)

        return query.all()

    def open_trades(self):
        return [t for t in self.all_trades() if t.status == "OPEN"]

    def total_trades(self):
        return len(
            self.all_trades()
        )

    def closed_trades(self):
        return [
            t for t in self.all_trades()
            if t.status == "CLOSED"
        ]

    def win_rate(self):
        trades = self.closed_trades()

        if not trades:
            return 0

        wins = [
            t for t in trades
            if t.pnl > 0
        ]

        return len(wins) / len(trades)

    def total_pnl(self):
        trades = self.closed_trades()

        return sum(
            t.pnl for t in trades
        )

    def profit_factor(self):
        trades = self.closed_trades()

        profits = sum(
            t.pnl for t in trades
            if t.pnl > 0
        )

        losses = abs(
            sum(
                t.pnl for t in trades
                if t.pnl < 0
            )
        )

        if losses == 0:
            return profits

        return profits / losses

    def sharpe_ratio(self):
        trades = self.closed_trades()

        returns = [
            t.pnl for t in trades
        ]

        if len(returns) < 2:
            return 0

        mean_return = np.mean(
            returns
        )

        std_return = np.std(
            returns
        )

        if std_return == 0:
            return 0

        return mean_return / std_return

    def max_drawdown(self):
        trades = self.closed_trades()

        equity = []

        running = 0

        for t in trades:
            running += t.pnl
            equity.append(running)

        if not equity:
            return 0

        peak = equity[0]
        max_dd = 0

        for value in equity:
            if value > peak:
                peak = value

            dd = peak - value

            if dd > max_dd:
                max_dd = dd

        return max_dd

    def pair_breakdown(self):
        """Per-symbol trade counts and win rate, for spotting which
        pairs the strategy actually performs well on."""
        trades = self.closed_trades()

        breakdown = {}

        for t in trades:
            entry = breakdown.setdefault(
                t.symbol,
                {"trades": 0, "wins": 0, "pnl": 0.0}
            )

            entry["trades"] += 1
            entry["pnl"] += t.pnl

            if t.pnl > 0:
                entry["wins"] += 1

        for symbol, entry in breakdown.items():
            entry["win_rate"] = (
                entry["wins"] / entry["trades"]
                if entry["trades"] > 0 else 0
            )

        return breakdown

    def confidence_stats(self):
        """Distribution of model confidence at entry, split by whether
        the trade ended up a winner or loser - useful for tuning the
        MIN_CONFIDENCE threshold in core/config.py."""
        trades = self.closed_trades()

        if not trades:
            return {"winning_avg_confidence": 0, "losing_avg_confidence": 0}

        winners = [t.confidence for t in trades if t.pnl > 0]
        losers = [t.confidence for t in trades if t.pnl <= 0]

        return {
            "winning_avg_confidence": float(np.mean(winners)) if winners else 0,
            "losing_avg_confidence": float(np.mean(losers)) if losers else 0
        }

    def close(self):
        self.db.close()
