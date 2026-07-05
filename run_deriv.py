from core.db_init import init_db  # must be first - creates tables before any query

# Initialise all DB tables before importing anything that opens a session
init_db()
import os
import pandas as pd

from execution.signal_engine import SignalEngine
from execution.deriv_executor import DerivExecutor


def main():
    df = pd.read_csv(
        "data/raw/market.csv"
    )
    df["time"] = pd.to_datetime(df["time"])

    engine = SignalEngine()

    signal_packet = engine.generate(df)

    print("Signal:", signal_packet)

    api_token = os.environ.get("DERIV_API_TOKEN")

    if not api_token:
        print("DERIV_API_TOKEN environment variable is not set.")
        return

    executor = DerivExecutor(
        api_token=api_token
    )

    executor.execute(
        signal_packet
    )


if __name__ == "__main__":
    main()

