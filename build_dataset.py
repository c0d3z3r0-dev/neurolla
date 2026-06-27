import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_market_data(rows=50000):
    np.random.seed(42)

    base_price = 1.1000
    current_price = base_price

    data = []
    start_time = datetime(2024, 1, 1)

    for i in range(rows):
        timestamp = start_time + timedelta(minutes=5 * i)

        drift = np.random.normal(0, 0.0004)

        open_price = current_price
        close_price = open_price + drift

        high_price = max(open_price, close_price) + abs(
            np.random.normal(0, 0.0002)
        )

        low_price = min(open_price, close_price) - abs(
            np.random.normal(0, 0.0002)
        )

        volume = np.random.randint(100, 3000)

        data.append([
            timestamp,
            round(open_price, 5),
            round(high_price, 5),
            round(low_price, 5),
            round(close_price, 5),
            volume
        ])

        current_price = close_price

    df = pd.DataFrame(
        data,
        columns=[
            "time",
            "open",
            "high",
            "low",
            "close",
            "tick_volume"
        ]
    )

    return df


def main():
    df = generate_market_data()

    df.to_csv(
        "data/raw/market.csv",
        index=False
    )

    print("Placeholder dataset created successfully.")


if __name__ == "__main__":
    main()