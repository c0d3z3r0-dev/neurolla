import random
import numpy as np


class MonteCarloEngine:
    """
    Shuffles the order of a fixed set of trade results to see how much
    the *path* could have differed by luck, holding the win/loss
    distribution itself fixed.

    Note: final cumulative equity (sum of all trade results) is the
    same regardless of order, so reporting mean/worst/best of the final
    equity value would always collapse to one identical number - it
    carries no information. What genuinely varies by shuffle order is
    path-dependent: how deep the worst drawdown gets, and how long the
    worst losing streak runs. Those are what this engine reports.
    """

    def simulate(
        self,
        trade_results,
        runs=1000
    ):
        final_equity = float(np.sum(trade_results))

        max_drawdowns = []
        max_losing_streaks = []

        for _ in range(runs):
            shuffled = trade_results[:]
            random.shuffle(shuffled)

            equity = np.cumsum(shuffled)

            running_peak = np.maximum.accumulate(equity)
            drawdown = running_peak - equity
            max_drawdowns.append(drawdown.max())

            streak = 0
            worst_streak = 0
            for result in shuffled:
                if result < 0:
                    streak += 1
                    worst_streak = max(worst_streak, streak)
                else:
                    streak = 0
            max_losing_streaks.append(worst_streak)

        return {
            "final_equity": final_equity,
            "mean_max_drawdown": float(np.mean(max_drawdowns)),
            "worst_max_drawdown": float(np.max(max_drawdowns)),
            "mean_max_losing_streak": float(np.mean(max_losing_streaks)),
            "worst_max_losing_streak": int(np.max(max_losing_streaks))
        }
