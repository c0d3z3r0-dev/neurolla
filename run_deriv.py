import pandas as pd

from execution.signal_engine import SignalEngine
from execution.deriv_executor import DerivExecutor


def main():
    df = pd.read_csv(
        "data/raw/market.csv"
    )

    engine = SignalEngine()

    signal_packet = engine.generate(df)

    print("Signal:", signal_packet)

    executor = DerivExecutor(
        api_token="YOUR_DERIV_API_TOKEN"
    )

    executor.execute(
        signal_packet
    )


if __name__ == "__main__":
    main()