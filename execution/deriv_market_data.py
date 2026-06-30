import pandas as pd

from execution.deriv_client import DerivClient
from execution.deriv_executor import to_deriv_symbol


def fetch_candles_as_df(api_token, symbol, granularity=300, count=300):
    """
    Connects to Deriv, pulls recent candles for `symbol` (plain
    naming, e.g. "EURUSD" - converted to Deriv's frx-prefixed naming
    internally), and returns a dataframe in the exact shape
    core.features.build_features expects: time, open, high, low,
    close, tick_volume.

    Deriv's candle API has no real traded volume for forex - tick
    count is used as a volume proxy, consistent with how MT5's
    tick_volume field (also a tick count, not real volume) is already
    used everywhere else in this codebase.
    """
    deriv_symbol = to_deriv_symbol(symbol)

    client = DerivClient(api_token)

    try:
        candles = client.get_candles(
            deriv_symbol,
            granularity=granularity,
            count=count
        )
    finally:
        client.close()

    if not candles:
        raise RuntimeError(
            f"Deriv returned no candle data for {deriv_symbol}. "
            f"Check the symbol name and that the market is open."
        )

    df = pd.DataFrame(candles)

    df = df.rename(
        columns={"epoch": "time"}
    )

    df["time"] = pd.to_datetime(
        df["time"],
        unit="s"
    )

    # Deriv's candle API doesn't return tick/volume data, so this is a
    # constant placeholder. tick_volume is one of core.config's 29 raw
    # FEATURE_COLUMNS fed directly into the model (no derived feature
    # transforms it, but the model was trained on real varying MT5
    # tick counts for this column) - a constant value here is a real
    # accuracy gap versus what the model learned on, not a cosmetic
    # one. If volume signal matters to your results, source candles
    # from MT5 instead of Deriv, or retrain with this column dropped.
    df["tick_volume"] = 1

    return df[
        ["time", "open", "high", "low", "close", "tick_volume"]
    ].astype(
        {"open": float, "high": float, "low": float, "close": float}
    )
