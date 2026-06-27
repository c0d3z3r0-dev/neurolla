from core.config import TP_MULT, SL_MULT


class DerivAdapter:
    def __init__(self, credentials):
        self.api_token = credentials.get("api_token")

    def execute(self, signal_packet):
        # This print-only adapter is a placeholder for routing through
        # BrokerRouter. The fully-implemented Deriv path (real websocket
        # order placement) lives in execution/deriv_executor.py and
        # execution/deriv_client.py - wire BrokerRouter to call that
        # implementation instead of this one before going live.
        print("Sending signal to Deriv (placeholder adapter):", signal_packet)

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
