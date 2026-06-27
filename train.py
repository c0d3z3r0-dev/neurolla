import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from core.features import build_features
from core.evaluator import build_sequences
from backtesting.monte_carlo import (
    MonteCarloEngine
)


class NeuroLLaModel(nn.Module):
    def __init__(
        self,
        input_size=6,
        hidden_size=64,
        output_size=3
    ):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            batch_first=True
        )

        self.fc = nn.Linear(
            hidden_size,
            output_size
        )

    def forward(
        self,
        x
    ):
        out, _ = self.lstm(x)

        out = self.fc(
            out[:, -1, :]
        )

        return out


def triple_barrier_labels(
    df,
    horizon=20,
    tp_mult=2.0,
    sl_mult=1.0
):
    labels = []

    closes = df["close"].values
    atr_values = df["atr"].values

    for i in range(len(df)):
        if i + horizon >= len(df):
            labels.append(1)
            continue

        entry = closes[i]
        atr = atr_values[i]

        tp = entry + (
            atr * tp_mult
        )

        sl = entry - (
            atr * sl_mult
        )

        future = closes[
            i+1:i+horizon+1
        ]

        hit_tp = np.any(
            future >= tp
        )

        hit_sl = np.any(
            future <= sl
        )

        if hit_tp and not hit_sl:
            labels.append(2)

        elif hit_sl and not hit_tp:
            labels.append(0)

        else:
            labels.append(1)

    return np.array(labels)


def walk_forward_split(
    X,
    y,
    train_ratio=0.8
):
    split = int(
        len(X) * train_ratio
    )

    X_train = X[:split]
    y_train = y[:split]

    X_test = X[split:]
    y_test = y[split:]

    return (
        X_train,
        y_train,
        X_test,
        y_test
    )


def train_model(
    model,
    X_train,
    y_train,
    epochs=15
):
    criterion = nn.CrossEntropyLoss()

    optimizer = optim.Adam(
        model.parameters(),
        lr=0.001
    )

    X_train = torch.tensor(
        X_train,
        dtype=torch.float32
    )

    y_train = torch.tensor(
        y_train,
        dtype=torch.long
    )

    for epoch in range(epochs):
        optimizer.zero_grad()

        outputs = model(
            X_train
        )

        loss = criterion(
            outputs,
            y_train
        )

        loss.backward()
        optimizer.step()

        print(
            f"Epoch {epoch+1}/{epochs} "
            f"Loss={loss.item():.4f}"
        )


def evaluate_model(
    model,
    X_test,
    y_test
):
    X_test = torch.tensor(
        X_test,
        dtype=torch.float32
    )

    outputs = model(
        X_test
    )

    predictions = torch.argmax(
        outputs,
        dim=1
    ).numpy()

    accuracy = np.mean(
        predictions == y_test
    )

    print(
        f"Accuracy: {accuracy:.4f}"
    )

    return predictions


def monte_carlo_validation(
    predictions,
    y_test
):
    trade_results = []

    for pred, actual in zip(
        predictions,
        y_test
    ):
        if pred == actual:
            trade_results.append(
                10
            )
        else:
            trade_results.append(
                -10
            )

    mc = MonteCarloEngine()

    results = mc.simulate(
        trade_results
    )

    print(
        "Monte Carlo Results:"
    )

    print(results)


def main():
    print(
        "Loading market data..."
    )

    df = pd.read_csv(
        "data/market_data.csv"
    )

    print(
        "Building features..."
    )

    df = build_features(df)

    print(
        "Generating labels..."
    )

    labels = triple_barrier_labels(
        df
    )

    print(
        "Building sequences..."
    )

    X, y = build_sequences(
        df,
        labels
    )

    print(
        "Walk-forward split..."
    )

    (
        X_train,
        y_train,
        X_test,
        y_test
    ) = walk_forward_split(
        X,
        y
    )

    print(
        "Training model..."
    )

    model = NeuroLLaModel()

    train_model(
        model,
        X_train,
        y_train
    )

    print(
        "Evaluating..."
    )

    predictions = evaluate_model(
        model,
        X_test,
        y_test
    )

    monte_carlo_validation(
        predictions,
        y_test
    )

    torch.save(
        model.state_dict(),
        "neurolla.pt"
    )

    print(
        "Model saved."
    )


if __name__ == "__main__":
    main()