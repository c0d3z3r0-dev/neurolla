import torch
import torch.nn.functional as F
import pandas as pd

from networks.hybrid_model import NeuroLLaCore
from core.features import build_features
from core.evaluator import build_sequences
from core.risk import fractional_kelly


class SignalEngine:
    def __init__(self):
        self.model = NeuroLLaCore()

        self.model.load_state_dict(
            torch.load(
                "models/trained/neurolla.pth"
            )
        )

        self.model.eval()

    def generate(self, market_df):
        df = build_features(market_df)

        dummy_labels = [1] * len(df)

        X, _ = build_sequences(
            df,
            dummy_labels
        )

        latest = torch.tensor(
            X[-1:],
            dtype=torch.float32
        )

        with torch.no_grad():
            logits = self.model(latest)
            probs = F.softmax(
                logits,
                dim=1
            )

        pred = torch.argmax(
            probs,
            dim=1
        ).item()

        confidence = torch.max(
            probs
        ).item()

        price = df["close"].iloc[-1]

        if pred == 2:
            signal = "BUY"
            sl = price - 0.0010
            tp = price + 0.0020

        elif pred == 0:
            signal = "SELL"
            sl = price + 0.0010
            tp = price - 0.0020

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