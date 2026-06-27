from core.features import build_features
from core.inference import ModelInference
from core.risk import fractional_kelly
from core.config import TP_MULT, SL_MULT


class SignalEngine:
    """
    Produces a complete signal_packet (signal, confidence, entry,
    sl, tp, risk) from raw market data - used by execution/deriv_executor.py
    which expects signal_packet["risk"] to size the trade.
    """

    def __init__(self):
        self.inference = ModelInference()

    def generate(self, market_df):
        df = build_features(market_df)

        label_index, label_name, confidence = self.inference.predict(df)

        price = df["close"].iloc[-1]
        atr = df["atr"].iloc[-1]

        if label_index == 2:
            signal = "BUY"
            sl = price - (atr * SL_MULT)
            tp = price + (atr * TP_MULT)

        elif label_index == 0:
            signal = "SELL"
            sl = price + (atr * SL_MULT)
            tp = price - (atr * TP_MULT)

        else:
            signal = "HOLD"
            sl = None
            tp = None

        risk = fractional_kelly(
            confidence
        )

        return {
            "signal": signal,
            "confidence": confidence,
            "entry": price,
            "sl": sl,
            "tp": tp,
            "risk": risk
        }
