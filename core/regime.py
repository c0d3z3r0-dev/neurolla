class RegimeDetector:
    def detect(self, df):
        volatility = df[
            "volatility"
        ].iloc[-1]

        if volatility > 0.005:
            return "VOLATILE"

        if volatility < 0.001:
            return "RANGE"

        return "TREND"