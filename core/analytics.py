from server.database import SessionLocal
from server.models import Trade
import numpy as np


class NeuroLLaAnalytics:
    def __init__(self):
        self.db = SessionLocal()

    def all_trades(self):
        return self.db.query(
            Trade
        ).all()

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