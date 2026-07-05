"""
train_from_mt5.py

Collects fresh OHLCV data from the running MT5 terminal and
immediately retrains NeuroLLaCore on it, replacing both the dataset
and the model checkpoint in one step.

Usage (from the project root):
    python train_from_mt5.py
    python train_from_mt5.py --symbol GBPUSD --bars 100000

This is the correct workflow before going live with real money:
    1.  python train_from_mt5.py       <- real data + retrain
    2.  python backtest.py             <- verify the model has real edge
    3.  python run_commander.py        <- live execution

Never skip step 2. A lower backtest Sharpe than expected is useful
information; an unvalidated model running on real capital is not.
"""

import argparse  # CLI flag parsing

# Collect step (pulls real bars from MT5)
from scripts.collect_mt5_data import collect

# Train step (reads the CSV collect() just wrote)
from train import main as train_model

from core.logger import setup_logger  # file + console logging

logger = setup_logger()

# These defaults match collect_mt5_data.py so the two scripts stay in sync
DEFAULT_SYMBOL = "EURUSD"
DEFAULT_BARS   = 50000
DEFAULT_OUTPUT = "data/raw/market.csv"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Collect MT5 data and retrain NeuroLLaCore in one step."
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
        help=f"Number of M5 bars to collect (default: {DEFAULT_BARS:,})"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    logger.info("=== NeuroLLa: collect + train ===")

    # Step 1: pull real bars from MT5 into data/raw/market.csv
    logger.info(
        f"Step 1/2  Collecting {args.bars:,} bars "
        f"of {args.symbol} from MT5..."
    )

    collect(
        symbol=args.symbol,
        bars=args.bars,
        output_path=DEFAULT_OUTPUT
    )

    # Step 2: train NeuroLLaCore on the data just collected
    logger.info(
        "Step 2/2  Training NeuroLLaCore on collected data..."
    )

    train_model()

    logger.info(
        "Done. Model checkpoint and scaler saved. "
        "Run backtest.py to validate before going live."
    )


if __name__ == "__main__":
    main()
