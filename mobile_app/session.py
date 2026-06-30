import threading
from datetime import datetime, timezone

from core.config import (
    SEQUENCE_LENGTH,
    MIN_CONFIDENCE,
    TP_MULT,
    SL_MULT
)
from core.features import build_features
from core.inference import ModelInference
from core.risk import fractional_kelly
from execution.deriv_market_data import fetch_candles_as_df
from execution.deriv_executor import DerivExecutor

DEFAULT_SYMBOL = "EURUSD"
DEFAULT_STAKE_BASE = 10.0  # USD, used as the base for risk-scaled stake sizing


class DerivSession:
    """
    Holds one connected Deriv session's state: the API token, the
    loaded model, the most recent prediction, the live executor, and a
    session-local log of trades placed through this app (only this
    app and only this run - there is no database, so this is not a
    substitute for Deriv's own statement/history).

    This is the model layer for the mobile_app UI - it has no NiceGUI
    imports, so it can be tested or reused independently of the UI.
    """

    def __init__(self):
        self.api_token = None
        self.executor = None
        self.inference = None
        self.lock = threading.Lock()

        self.last_prediction = None
        self.last_confidence = None
        self.last_signal_packet = None
        self.last_error = None

        # Most-recent-first list of {symbol, signal, confidence, entry,
        # sl, tp, result, placed_at} dicts - cleared on disconnect.
        self.trade_log = []

    @property
    def is_connected(self):
        return self.executor is not None

    def load_model(self):
        # Loading NeuroLLaCore + the scaler is done once, lazily - not
        # in __init__ - so the UI can show a clear "model not found"
        # error instead of the whole app crashing if train.py hasn't
        # been run yet on this machine.
        if self.inference is None:
            self.inference = ModelInference()

    def connect(self, api_token):
        """
        Authorizes against Deriv with the given token. Raises
        ConnectionError (bad network/host) or PermissionError (bad
        token) - the UI is responsible for catching these and showing
        a clear message rather than a stack trace.
        """
        executor = DerivExecutor(api_token)

        self.api_token = api_token
        self.executor = executor

    def disconnect(self):
        if self.executor:
            self.executor.close()

        self.executor = None
        self.api_token = None
        self.last_prediction = None
        self.last_confidence = None
        self.last_signal_packet = None
        self.trade_log = []

    def get_signal(self, symbol=DEFAULT_SYMBOL):
        """
        Fetches recent candles from Deriv, runs the model, and stores
        the result on self.last_* for the UI to read. Returns the
        signal_packet dict on success.
        """
        self.load_model()

        df = fetch_candles_as_df(
            self.api_token,
            symbol,
            count=max(SEQUENCE_LENGTH + 50, 300)
        )

        df = build_features(df)

        if len(df) < SEQUENCE_LENGTH:
            raise RuntimeError(
                f"Not enough candle history after warm-up "
                f"({len(df)} rows, need {SEQUENCE_LENGTH}). "
                f"Try again in a few minutes once more bars exist."
            )

        label_index, label_name, confidence = self.inference.predict(df)

        price = df["close"].iloc[-1]
        atr = df["atr"].iloc[-1]

        if label_index == 2:
            sl = price - (atr * SL_MULT)
            tp = price + (atr * TP_MULT)
        elif label_index == 0:
            sl = price + (atr * SL_MULT)
            tp = price - (atr * TP_MULT)
        else:
            sl = None
            tp = None

        risk_fraction = fractional_kelly(confidence)

        signal_packet = {
            "symbol": symbol,
            "signal": label_name,
            "confidence": confidence,
            "entry": float(price),
            "atr": float(atr),
            "sl": sl,
            "tp": tp,
            "risk": risk_fraction
        }

        self.last_prediction = label_name
        self.last_confidence = confidence
        self.last_signal_packet = signal_packet

        return signal_packet

    def can_trade(self):
        return (
            self.last_signal_packet is not None
            and self.last_signal_packet["signal"] != "HOLD"
            and self.last_confidence is not None
            and self.last_confidence >= MIN_CONFIDENCE
        )

    def place_trade(self):
        """
        Sends the last computed signal to Deriv via DerivExecutor.
        Deliberately requires get_signal() to have been called first
        and can_trade() to be true - this app never places a trade
        the user hasn't first seen the prediction and confidence for.
        """
        if not self.can_trade():
            raise RuntimeError(
                "No tradeable signal available. Get a fresh signal first."
            )

        result = self.executor.execute(self.last_signal_packet)

        self.trade_log.insert(0, {
            **self.last_signal_packet,
            "result": result,
            "placed_at": datetime.now(timezone.utc)
        })

        return result
