from core.config import TP_MULT, SL_MULT


class MT5Adapter:
    """
    Placeholder adapter for BrokerRouter's generic execute() interface.
    This does NOT place a real MT5 order - it only computes the same
    ATR-based SL/TP every other adapter computes and reports back as
    'simulated'. The real, order-placing MT5 path is live/trader.py,
    which calls mt5.order_send() directly. Route through that instead
    of BrokerRouter("mt5", ...) for actual live execution.
    """

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
