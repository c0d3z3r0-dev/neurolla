class TradeQuality:
    def score(self, df):
        score = 0

        if df["rsi"].iloc[-1] > 50:
            score += 20

        if (
            df["ema20"].iloc[-1] >
            df["ema50"].iloc[-1]
        ):
            score += 20

        if df["volatility"].iloc[-1] > 0.001:
            score += 20

        if df["atr"].iloc[-1] > 0:
            score += 20

        return score