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

DEFAULT_WATCHLIST = [
    "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"
]


class MultiPairScanner:
    """
    Picks a rule-based direction (trend/mean-reversion/breakout,
    selected by detected regime) for each symbol in market_data.
    The NN-based confidence used for actual position sizing comes
    later from MultiTimeframeConfluence.confirm(), not from here -
    this scanner's job is direction proposal, not confidence scoring.
    """

    def __init__(self, watchlist=None):
        self.trend = TrendFollowing()
        self.mean = MeanReversion()
        self.breakout = Breakout()
        self.regime = RegimeDetector()
        self.watchlist = watchlist or DEFAULT_WATCHLIST

    def scan_symbol(self, symbol, df):
        regime = self.regime.detect(df)

        if regime == "TREND":
            signal = self.trend.evaluate(df)
        elif regime == "RANGE":
            signal = self.mean.evaluate(df)
        else:
            signal = self.breakout.evaluate(df)

        if not signal:
            return None

        return {
            "symbol": symbol,
            "prediction": 2 if signal == "BUY" else 0,
            "regime": regime
        }

    def scan(self, market_data):
        """
        market_data: either a single dataframe (legacy single-symbol
        call, treated as the first watchlist symbol) or a dict mapping
        symbol -> dataframe for true multi-pair scanning.
        """
        if not isinstance(market_data, dict):
            symbol = self.watchlist[0]
            market_data = {symbol: market_data}

        results = []

        for symbol, df in market_data.items():
            signal = self.scan_symbol(symbol, df)

            if signal:
                results.append(signal)

        return results
