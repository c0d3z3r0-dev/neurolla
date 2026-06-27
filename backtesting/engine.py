import torch
import torch.nn.functional as F
import pandas as pd

from networks.hybrid_model import NeuroLLaCore
from core.features import build_features
from core.evaluator import build_sequences
from core.risk import fractional_kelly

from backtesting.metrics import (
    win_rate,
    profit_factor,
    expectancy,
    sharpe_ratio,
    max_drawdown,
    max_consecutive_losses
)


class NeuroLLaBacktester:
    def __init__(self):
        self.model = NeuroLLaCore()

        self.model.load_state_dict(
            torch.load(
                "models/trained/neurolla.pth"
            )
        )

        self.model.eval()

        self.spread_cost = 0.00015
        self.slippage_cost = 0.00005

    def run(
        self,
        csv_path
    ):
        df = pd.read_csv(csv_path)

        df = build_features(df)

        dummy_labels = [1] * len(df)

        X, _ = build_sequences(
            df,
            dummy_labels
        )

        trades = []
        equity = 1000
        equity_curve = [equity]

        for i in range(len(X) - 20):
            sequence = torch.tensor(
                X[i:i+1],
                dtype=torch.float32
            )

            with torch.no_grad():
                logits = self.model(sequence)

                probs = F.softmax(
                    logits,
                    dim=1
                )

            prediction = torch.argmax(
                probs,
                dim=1
            ).item()

            confidence = torch.max(
                probs
            ).item()

            if confidence < 0.68:
                continue

            entry = df["close"].iloc[i]
            exit_price = df["close"].iloc[i + 20]

            pnl = 0

            if prediction == 2:
                pnl = (
                    exit_price -
                    entry -
                    self.spread_cost -
                    self.slippage_cost
                )

            elif prediction == 0:
                pnl = (
                    entry -
                    exit_price -
                    self.spread_cost -
                    self.slippage_cost
                )

            else:
                continue

            kelly_fraction = fractional_kelly(
                confidence
            )

            trade_size = equity * kelly_fraction

            trade_return = pnl * trade_size

            equity += trade_return

            trades.append(trade_return)

            equity_curve.append(equity)

        print("===== NeuroLLa Report =====")
        print("Trades:", len(trades))
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