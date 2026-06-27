import MetaTrader5 as mt5
import torch
import torch.nn.functional as F
import pandas as pd

from networks.hybrid_model import NeuroLLaCore
from core.features import build_features
from core.evaluator import build_sequences


class MultiTimeframeConfluence:
    def __init__(self):
        self.model = NeuroLLaCore()

        self.model.load_state_dict(
            torch.load(
                "models/trained/neurolla.pth"
            )
        )

        self.model.eval()

    def fetch_tf(
        self,
        symbol,
        timeframe,
        bars=300
    ):
        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            bars
        )

        df = pd.DataFrame(rates)

        df["time"] = pd.to_datetime(
            df["time"],
            unit="s"
        )

        df = df[
            [
                "time",
                "open",
                "high",
                "low",
                "close",
                "tick_volume"
            ]
        ]

        return df

    def infer(self, symbol, timeframe):
        df = self.fetch_tf(
            symbol,
            timeframe
        )

        df = build_features(df)

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

        prediction = torch.argmax(
            probs,
            dim=1
        ).item()

        confidence = torch.max(
            probs
        ).item()

        return prediction, confidence

    def confirm(self, symbol):
        tf_map = {
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "H1": mt5.TIMEFRAME_H1
        }

        results = {}

        for tf_name, tf in tf_map.items():
            pred, conf = self.infer(
                symbol,
                tf
            )

            results[tf_name] = {
                "prediction": pred,
                "confidence": conf
            }

        preds = [
            x["prediction"]
            for x in results.values()
        ]

        aligned = len(set(preds)) == 1

        return aligned, results