import pandas as pd

from core.analytics import NeuroLLaAnalytics
from core.regime import MarketRegime
from train import main as train_model


class AdaptiveTrainer:
    def __init__(self):
        self.analytics = NeuroLLaAnalytics()

    def should_retrain(self):
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

            train_model()

        else:
            print(
                "No retraining needed."
            )


if __name__ == "__main__":
    trainer = AdaptiveTrainer()

    trainer.run()