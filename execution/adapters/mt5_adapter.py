class MT5Adapter:
    def __init__(
        self,
        credentials
    ):
        self.credentials = credentials

    def execute(
        self,
        signal_packet
    ):
        price = signal_packet["entry"]
        atr = signal_packet["atr"]

        if signal_packet["signal"] == "BUY":
            sl = price - (atr * 1.5)
            tp = price + (atr * 3.0)

        else:
            sl = price + (atr * 1.5)
            tp = price - (atr * 3.0)

        return {
            "status": "executed",
            "entry": price,
            "sl": sl,
            "tp": tp
        }