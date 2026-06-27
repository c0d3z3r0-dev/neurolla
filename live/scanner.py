from strategies.trend_following import (
    TrendFollowing
)

from strategies.mean_reversion import (
    MeanReversion
)

from strategies.breakout import (
    Breakout
)

from core.regime import (
    RegimeDetector
)


class MultiPairScanner:
    def __init__(self):
        self.trend = TrendFollowing()
        self.mean = MeanReversion()
        self.breakout = Breakout()
        self.regime = RegimeDetector()

    def scan(self, df):
        regime = self.regime.detect(df)

        signal = None

        if regime == "TREND":
            signal = self.trend.evaluate(df)

        elif regime == "RANGE":
            signal = self.mean.evaluate(df)

        else:
            signal = self.breakout.evaluate(df)

        if signal:
            return [
                {
                    "symbol": "EURUSD",
                    "prediction": (
                        2 if signal == "BUY"
                        else 0
                    ),
                    "confidence": 0.85
                }
            ]

        return []