class TrendFollowing:
    def evaluate(self, df):
        if (
            df["ema20"].iloc[-1] >
            df["ema50"].iloc[-1]
        ):
            return "BUY"

        if (
            df["ema20"].iloc[-1] <
            df["ema50"].iloc[-1]
        ):
            return "SELL"

        return None