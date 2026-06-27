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
            sl = price - (atr * 1.5)
            tp = price + (atr * 3.0)
        else:
            sl = price + (atr * 1.5)
            tp = price - (atr * 3.0)

        return {
            "status": "simulated",
            "entry": price,
            "sl": sl,
            "tp": tp
        }
