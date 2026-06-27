import pandas as pd
import numpy as np
from core.config import FEATURE_COLUMNS


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    result = 100 - (100 / (1 + rs))
    return result.fillna(50)


def atr(df, period=14):
    high_low = df["high"] - df["low"]
    high_close = np.abs(df["high"] - df["close"].shift())
    low_close = np.abs(df["low"] - df["close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def bollinger(series, period=20, num_std=2):
    middle = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = middle + (num_std * std)
    lower = middle - (num_std * std)
    width = (upper - lower) / middle.replace(0, np.nan)
    position = (series - lower) / (upper - lower).replace(0, np.nan)
    return width.fillna(0), position.fillna(0.5)


def stochastic(df, period=14, smooth=3):
    lowest_low = df["low"].rolling(period).min()
    highest_high = df["high"].rolling(period).max()
    denom = (highest_high - lowest_low).replace(0, np.nan)
    k = 100 * (df["close"] - lowest_low) / denom
    k = k.fillna(50)
    d = k.rolling(smooth).mean()
    return k, d


def adx(df, period=14):
    up_move = df["high"].diff()
    down_move = -df["low"].diff()

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)

    tr_series = atr(df, period=1) * 1  # true range per bar (period=1 -> no smoothing yet)
    tr_smooth = tr_series.rolling(period).sum().replace(0, np.nan)

    plus_di = 100 * plus_dm.rolling(period).sum() / tr_smooth
    minus_di = 100 * minus_dm.rolling(period).sum() / tr_smooth

    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
    adx_value = dx.rolling(period).mean()

    return adx_value.fillna(0)


def build_features(df):
    """
    Builds every column listed in core.config.FEATURE_COLUMNS, in order.
    df must already have columns: time, open, high, low, close, tick_volume.
    Rows that can't be fully computed (warm-up period for rolling windows)
    are dropped at the end, so the returned df is ready for sequencing.
    """
    df = df.copy()

    df["ema10"] = ema(df["close"], 10)
    df["ema20"] = ema(df["close"], 20)
    df["ema50"] = ema(df["close"], 50)
    df["ema100"] = ema(df["close"], 100)

    df["rsi"] = rsi(df["close"])
    df["rsi_slope"] = df["rsi"].diff()

    df["atr"] = atr(df)
    df["atr_pct"] = df["atr"] / df["close"]

    df["returns"] = df["close"].pct_change()
    df["log_returns"] = np.log(df["close"] / df["close"].shift())

    df["volatility"] = df["returns"].rolling(20).std()
    rolling_vol_long = df["returns"].rolling(100).std()
    df["volatility_ratio"] = df["volatility"] / rolling_vol_long.replace(0, np.nan)

    macd_line, signal_line, hist = macd(df["close"])
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist

    bb_width, bb_position = bollinger(df["close"])
    df["bb_width"] = bb_width
    df["bb_position"] = bb_position

    stoch_k, stoch_d = stochastic(df)
    df["stoch_k"] = stoch_k
    df["stoch_d"] = stoch_d

    df["adx"] = adx(df)

    df["momentum"] = df["close"] - df["close"].shift(10)

    df["high_low_range"] = (df["high"] - df["low"]) / df["close"]
    df["body_size"] = (df["close"] - df["open"]) / df["close"]

    # Cyclical encoding of time-of-day so the model can learn session effects
    # without treating hour 23 and hour 0 as far apart.
    df["hour_sin"] = np.sin(2 * np.pi * df["time"].dt.hour / 24)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"build_features did not produce required columns: {missing}")

    return df
