from core.config import TP_MULT, SL_MULT


class CTraderAdapter:
    """
    Placeholder adapter. cTrader execution is not yet implemented against
    a real cTrader Open API connection - this only computes the same
    ATR-based SL/TP every other adapter computes and reports back as
    'simulated' so BrokerRouter never crashes when 'ctrader' is selected.
    Replace execute() with real cTrader Open API order calls before
    routing real capital through this adapter.
    """

    def __init__(self, credentials):
        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")

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
