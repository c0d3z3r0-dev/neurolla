class MeanReversion:
    def evaluate(self, df):
        rsi = df["rsi"].iloc[-1]

        if rsi < 30:
            return "BUY"

        if rsi > 70:
            return "SELL"

        return None