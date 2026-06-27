class RegimeDetector:
    """Lightweight single-label regime classifier used by live/scanner.py
    to pick which strategy class evaluates the current bar."""

    def detect(self, df):
        volatility = df[
            "volatility"
        ].iloc[-1]

        if volatility > 0.005:
            return "VOLATILE"

        if volatility < 0.001:
            return "RANGE"

        return "TREND"


class MarketRegime:
    """Richer regime report used by adaptive_train.py to decide whether
    market conditions have shifted enough to justify retraining."""

    def __init__(self, df):
        self.df = df

    def volatility_regime(self):
        returns = self.df["close"].pct_change()
        volatility = returns.rolling(20).std().iloc[-1]

        if volatility > 0.005:
            return "VOLATILE"

        if volatility < 0.001:
            return "RANGE"

        return "NORMAL"

    def trend_regime(self):
        close = self.df["close"]
        ema20 = close.ewm(span=20, adjust=False).mean()
        ema50 = close.ewm(span=50, adjust=False).mean()

        if ema20.iloc[-1] > ema50.iloc[-1]:
            return "UPTREND"

        if ema20.iloc[-1] < ema50.iloc[-1]:
            return "DOWNTREND"

        return "FLAT"
