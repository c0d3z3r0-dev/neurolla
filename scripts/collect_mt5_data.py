"""
scripts/collect_mt5_data.py

Pulls real OHLCV bars from the running MetaTrader 5 terminal and
saves them as data/raw/market.csv, replacing any placeholder or
previously collected dataset.

Usage (from the project root):
    python scripts/collect_mt5_data.py
    python scripts/collect_mt5_data.py --symbol GBPUSD --bars 100000

MT5 must be installed on this machine and logged into an account
before running this script. The terminal does not need to be visible,
but it must be running.

The resulting CSV is the training dataset train.py reads from
DATA_PATH = "data/raw/market.csv". After collecting, run:
    python train.py
to retrain NeuroLLaCore on the real data.
"""

import argparse     # CLI argument parsing
import os           # path and directory helpers
import sys          # exit on fatal errors

import MetaTrader5 as mt5  # real MT5 terminal connection

from live.mt5_connector import MT5Connector  # shared connector wrapper
from core.logger import setup_logger         # file + console logging

logger = setup_logger()

# Default collection parameters - override via CLI flags if needed
DEFAULT_SYMBOL = "EURUSD"
DEFAULT_BARS   = 50000        # ~174 days of M5 data
DEFAULT_OUTPUT = os.path.join("data", "raw", "market.csv")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect MT5 OHLCV data for NeuroLLa training."
    )

    parser.add_argument(
        "--symbol",
        default=DEFAULT_SYMBOL,
        help=f"MT5 symbol to collect (default: {DEFAULT_SYMBOL})"
    )

    parser.add_argument(
        "--bars",
        type=int,
        default=DEFAULT_BARS,
        help=f"Number of M5 bars to collect (default: {DEFAULT_BARS})"
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output CSV path (default: {DEFAULT_OUTPUT})"
    )

    parser.add_argument(
        "--timeframe",
        default="M5",
        choices=["M1", "M5", "M15", "M30", "H1", "H4", "D1"],
        help="MT5 timeframe (default: M5 - matches model training)"
    )

    return parser.parse_args()


# Map CLI timeframe strings to MT5 constants
TIMEFRAME_MAP = {
    "M1":  mt5.TIMEFRAME_M1,
    "M5":  mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1":  mt5.TIMEFRAME_H1,
    "H4":  mt5.TIMEFRAME_H4,
    "D1":  mt5.TIMEFRAME_D1,
}


def collect(symbol, bars, output_path, timeframe_key="M5"):
    logger.info(f"Connecting to MT5 terminal...")

    try:
        connector = MT5Connector()
    except Exception as exc:
        logger.error(f"Could not connect to MT5: {exc}")
        sys.exit(1)

    timeframe = TIMEFRAME_MAP[timeframe_key]

    logger.info(
        f"Fetching {bars:,} {timeframe_key} bars "
        f"for {symbol}..."
    )

    try:
        df = connector.fetch_data(
            symbol=symbol,
            timeframe=timeframe,
            bars=bars
        )

    except Exception as exc:
        logger.error(f"Data fetch failed: {exc}")
        connector.shutdown()
        sys.exit(1)

    connector.shutdown()

    # Ensure output directory exists before writing
    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    df.to_csv(output_path, index=False)

    logger.info(
        f"Saved {len(df):,} rows to {output_path}"
    )
    logger.info(
        f"Date range: "
        f"{df['time'].iloc[0]} "
        f"to "
        f"{df['time'].iloc[-1]}"
    )

    return df


if __name__ == "__main__":
    args = parse_args()

    collect(
        symbol=args.symbol,
        bars=args.bars,
        output_path=args.output,
        timeframe_key=args.timeframe
    )
