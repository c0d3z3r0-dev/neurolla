from core.config import TP_MULT, SL_MULT


class BinanceAdapter:
    """
    Placeholder adapter. Binance execution is not yet implemented against
    a real Binance API connection - see the note in ctrader_adapter.py;
    the same caveat applies here.
    """

    def __init__(self, credentials):
        self.api_key = credentials.get("api_key")
        self.api_secret = credentials.get("api_secret")

    def execute(self, signal_packet):
        price = signal_packet["entry"]
        atr = signal_packet["atr"]

        if signal_packet["signal"] == "BUY":
            sl = price - (atr * SL_MULT)
            tp = price + (atr * TP_MULT)
        else:
            sl = price + (atr * SL_MULT)
            tp = price - (atr * TP_MULT)

        return {
            "status": "simulated",
            "entry": price,
            "sl": sl,
            "tp": tp
        }
