import pandas as pd
import numpy as np


def ema(series, period):
    return series.ewm(
        span=period,
        adjust=False
    ).mean()


def rsi(series, period=14):
    delta = series.diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(period)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(period)
        .mean()
    )

    rs = gain / loss

    return 100 - (
        100 / (1 + rs)
    )


def atr(df, period=14):
    high_low = df["high"] - df["low"]

    high_close = np.abs(
        df["high"] - df["close"].shift()
    )

    low_close = np.abs(
        df["low"] - df["close"].shift()
    )

    tr = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    return tr.rolling(period).mean()


def build_features(df):
    df["ema20"] = ema(
        df["close"], 20
    )

    df["ema50"] = ema(
        df["close"], 50
    )

    df["rsi"] = rsi(
        df["close"]
    )

    df["atr"] = atr(df)

    df["returns"] = (
        df["close"].pct_change()
    )

    df["volatility"] = (
        df["returns"]
        .rolling(20)
        .std()
    )

    df.dropna(inplace=True)

    return df