import pandas as pd

from core.features import build_features
from core.inference import ModelInference
from core.risk import fractional_kelly
from core.config import (
    TP_MULT, SL_MULT, MIN_CONFIDENCE, SEQUENCE_LENGTH, MAX_DAILY_DRAWDOWN
)

from backtesting.metrics import (
    win_rate,
    profit_factor,
    expectancy,
    sharpe_ratio,
    max_drawdown,
    max_consecutive_losses
)

STANDARD_LOT_UNITS = 100_000  # 1.0 lot = 100,000 units of base currency


class NeuroLLaBacktester:
    """
    Walks forward through historical bars, asks the model for a signal
    at each one, and simulates the resulting trade's PnL in real dollars.

    Position sizing: risk_amount = equity * fractional_kelly(confidence)
    is a target dollar risk. Dividing that by the ATR-based stop
    distance (in price units) gives the lot size that would lose
    exactly risk_amount if the stop is hit - this is standard
    risk-based position sizing, and it's what makes the PnL numbers
    below correspond to real money rather than an arbitrary unit
    mismatch between price deltas and a dollar trade_size.
    """

    def __init__(self):
        self.inference = ModelInference()

        self.spread_cost = 0.00015
        self.slippage_cost = 0.00005
        self.starting_equity = 1000.0

    def run(
        self,
        csv_path,
        horizon=20
    ):
        df = pd.read_csv(csv_path)
        df["time"] = pd.to_datetime(df["time"])

        df = build_features(df)

        label_indices, confidences = self.inference.predict_all(df)

        # predict_all returns one prediction per window ending at
        # df.iloc[i + SEQUENCE_LENGTH - 1], so offset is needed to line
        # predictions back up with rows in df.
        offset = SEQUENCE_LENGTH - 1

        trades = []
        equity = self.starting_equity
        equity_curve = [equity]
        equity_floor = self.starting_equity * (1 - MAX_DAILY_DRAWDOWN)
        halted = False

        for i, (prediction, confidence) in enumerate(zip(label_indices, confidences)):
            if equity <= equity_floor:
                # Mirrors live/trader.py's check_drawdown circuit breaker:
                # a real account would stop trading once the configured
                # drawdown limit is breached, rather than continuing to
                # compound losses toward zero over thousands more trades.
                halted = True
                break

            row_index = i + offset

            if row_index + horizon >= len(df):
                break

            if confidence < MIN_CONFIDENCE:
                continue

            if prediction == 1:
                continue

            entry = df["close"].iloc[row_index]
            atr = df["atr"].iloc[row_index]

            if atr <= 0:
                continue

            stop_distance = atr * SL_MULT
            target_distance = atr * TP_MULT

            if prediction == 2:
                stop_price = entry - stop_distance
                target_price = entry + target_distance
            else:
                stop_price = entry + stop_distance
                target_price = entry - target_distance

            # Walk forward bar-by-bar (up to `horizon` bars) and exit at
            # whichever barrier is actually touched first - mirroring
            # core.labels.triple_barrier_labels exactly. Exiting at a
            # fixed bar count regardless of price path lets occasional
            # large overshoots (which happen often: a 20-bar move
            # averages over 2x ATR) inflate PnL far beyond what the
            # ATR-based TP/SL the position was actually sized for would
            # have captured.
            exit_price = None

            for offset in range(1, horizon + 1):
                if row_index + offset >= len(df):
                    break

                bar_close = df["close"].iloc[row_index + offset]

                if prediction == 2:
                    if bar_close >= target_price:
                        exit_price = target_price
                        break
                    if bar_close <= stop_price:
                        exit_price = stop_price
                        break
                else:
                    if bar_close <= target_price:
                        exit_price = target_price
                        break
                    if bar_close >= stop_price:
                        exit_price = stop_price
                        break

            if exit_price is None:
                # Neither barrier was touched within the horizon -
                # close at the final bar's price, same as a HOLD
                # outcome in the label scheme.
                last_offset = min(horizon, len(df) - 1 - row_index)
                exit_price = df["close"].iloc[row_index + last_offset]

            if prediction == 2:
                pnl_per_unit = (
                    exit_price - entry -
                    self.spread_cost - self.slippage_cost
                )
            else:
                pnl_per_unit = (
                    entry - exit_price -
                    self.spread_cost - self.slippage_cost
                )

            kelly_fraction = fractional_kelly(confidence)
            risk_amount = equity * kelly_fraction

            # Lots sized so a stop-out would cost exactly risk_amount.
            lots = risk_amount / (stop_distance * STANDARD_LOT_UNITS)

            trade_return = pnl_per_unit * lots * STANDARD_LOT_UNITS

            equity += trade_return
            trades.append(trade_return)
            equity_curve.append(equity)

        print("===== NeuroLLa Report =====")
        print("Trades:", len(trades))
        if halted:
            print(f"HALTED: equity floor ({equity_floor:.2f}) breached before all data was used.")
        print("Win Rate:", win_rate(trades))
        print("Profit Factor:", profit_factor(trades))
        print("Expectancy:", expectancy(trades))
        print("Sharpe Ratio:", sharpe_ratio(trades))
        print("Max Drawdown:", max_drawdown(equity_curve))
        print(
            "Max Consecutive Losses:",
            max_consecutive_losses(trades)
        )
        print("Final Equity:", equity)

        return {
            "trades": trades,
            "equity_curve": equity_curve,
            "final_equity": equity,
            "halted": halted
        }
