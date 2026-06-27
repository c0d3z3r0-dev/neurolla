class Breakout:
    def evaluate(self, df):
        high = df["high"].rolling(20).max().iloc[-1]
        low = df["low"].rolling(20).min().iloc[-1]
        close = df["close"].iloc[-1]

        if close >= high:
            return "BUY"

        if close <= low:
            return "SELL"

        return None