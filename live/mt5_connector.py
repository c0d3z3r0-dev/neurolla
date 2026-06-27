import os
import MetaTrader5 as mt5
import pandas as pd


class MT5Connector:
    def __init__(self):
        # MT5_TERMINAL_PATH is optional - if unset, mt5.initialize()
        # auto-detects an already-running terminal, which works fine
        # on any machine (and matches what live/trader.py already
        # does). Only set it if you need to launch a specific
        # installation explicitly.
        terminal_path = os.environ.get("MT5_TERMINAL_PATH")

        initialized = (
            mt5.initialize(path=terminal_path)
            if terminal_path
            else mt5.initialize()
        )

        if not initialized:
            raise Exception(
                f"Failed to connect to MetaTrader5: {mt5.last_error()}"
            )

    def fetch_data(
        self,
        symbol="EURUSD",
        timeframe=mt5.TIMEFRAME_M5,
        bars=50000
    ):
        rates = mt5.copy_rates_from_pos(
            symbol,
            timeframe,
            0,
            bars
        )

        if rates is None:
            raise Exception(
                f"No market data retrieved: {mt5.last_error()}"
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

    def save_csv(self, df, path):
        df.to_csv(path, index=False)
        print(f"Saved dataset to {path}")

    def shutdown(self):
        mt5.shutdown()