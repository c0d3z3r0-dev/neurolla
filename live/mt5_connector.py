import MetaTrader5 as mt5
import pandas as pd


class MT5Connector:
    def __init__(self):
        if not mt5.initialize(
            path=r"C:\Program Files\MetaTrader 5\terminal64.exe"
        ):
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