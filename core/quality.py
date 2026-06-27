class TradeQuality:
    """
    Scores 0-100. Each of the four checks below contributes 25 points,
    so a trade that passes every check scores exactly 100.
    """

    def score(self, df):
        score = 0

        if df["rsi"].iloc[-1] > 50:
            score += 25

        if (
            df["ema20"].iloc[-1] >
            df["ema50"].iloc[-1]
        ):
            score += 25

        if df["volatility"].iloc[-1] > 0.001:
            score += 25

        if df["atr"].iloc[-1] > 0:
            score += 25

        return score