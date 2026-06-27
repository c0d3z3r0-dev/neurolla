import MetaTrader5 as mt5
import pandas as pd

from core.features import build_features
from core.inference import ModelInference


class MultiTimeframeConfluence:
    """
    Runs the same model across M5/M15/H1 and checks whether they all
    agree on direction, as a confirmation gate before commander.py
    acts on the primary (rule-based) strategy signal.
    """

    def __init__(self):
        self.inference = ModelInference()

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
        df = self.fetch_tf(symbol, timeframe)
        df = build_features(df)

        label_index, label_name, confidence = self.inference.predict(df)

        return label_index, confidence

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
