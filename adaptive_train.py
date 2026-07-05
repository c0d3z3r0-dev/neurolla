from core.db_init import init_db  # must be first - creates tables before any query

# Initialise all DB tables before importing anything that opens a session
init_db()
import pandas as pd

from core.analytics import NeuroLLaAnalytics
from core.regime import MarketRegime
from train import main as train_model


class AdaptiveTrainer:
    """
    Decides whether the shared NeuroLLaCore model needs retraining,
    based on recent win rate. user_id=None evaluates win rate across
    every user (appropriate for a single shared model, since all
    users' commander.py instances trade off the same checkpoint).
    Pass a specific user_id only if you want one account's recent
    performance to drive the decision instead.
    """

    def __init__(self, user_id=None):
        self.analytics = NeuroLLaAnalytics(user_id=user_id)

    def should_retrain(self):
        closed_trades = self.analytics.closed_trades()

        # With no closed trades yet, win_rate() returns 0, which would
        # otherwise look identical to "model is actually losing" and
        # trigger a pointless retrain on a freshly deployed system.
        if len(closed_trades) < 30:
            return False

        win_rate = self.analytics.win_rate()

        if win_rate < 0.45:
            return True

        return False

    def evaluate_regime(self):
        df = pd.read_csv(
            "data/raw/market.csv"
        )

        regime = MarketRegime(df)

        print(
            "Volatility:",
            regime.volatility_regime()
        )

        print(
            "Trend:",
            regime.trend_regime()
        )

    def run(self):
        self.evaluate_regime()

        if self.should_retrain():
            print(
                "Retraining triggered..."
            )

            # NOTE: this call blocks until training finishes (could be
            # minutes to hours). Calling AdaptiveTrainer.run() from
            # inside a live trading loop (commander.adapt()) will
            # freeze that loop for the duration. For production, run
            # this on a separate schedule/worker process instead of
            # inline in the same loop that places trades.
            train_model()

        else:
            print(
                "No retraining needed."
            )


if __name__ == "__main__":
    trainer = AdaptiveTrainer()

    trainer.run()
