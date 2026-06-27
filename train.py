import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

from core.config import (
    MODEL_DIR,
    MODEL_SAVE_PATH,
    SCALER_SAVE_PATH,
    SEQUENCE_LENGTH,
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    VALIDATION_SPLIT,
    TEST_SPLIT,
    EARLY_STOPPING_PATIENCE,
    GRADIENT_CLIP_NORM,
    DEVICE
)
from core.features import build_features
from core.labels import triple_barrier_labels
from core.evaluator import build_sequences, save_scaler
from core.dataset import MarketDataset
from core.trainer import Trainer
from networks.hybrid_model import NeuroLLaCore
from backtesting.monte_carlo import MonteCarloEngine

DATA_PATH = "data/raw/market.csv"


def chronological_split(df, val_split=VALIDATION_SPLIT, test_split=TEST_SPLIT):
    """
    Splits a time-ordered dataframe into train/val/test, in that
    chronological order. This must never be a random shuffle split -
    a model that has seen future bars during training would report
    unrealistically good validation/test accuracy (lookahead bias).
    """
    n = len(df)
    test_start = int(n * (1 - test_split))
    val_start = int(test_start * (1 - val_split))

    train_df = df.iloc[:val_start].reset_index(drop=True)
    val_df = df.iloc[val_start:test_start].reset_index(drop=True)
    test_df = df.iloc[test_start:].reset_index(drop=True)

    return train_df, val_df, test_df


def compute_class_weights(labels, num_classes=3):
    """
    Triple-barrier labels are rarely balanced (HOLD usually dominates),
    so an unweighted CrossEntropyLoss would let the model get a
    deceptively low loss by mostly predicting HOLD. Weighting inversely
    by class frequency counteracts that.
    """
    counts = np.bincount(labels, minlength=num_classes).astype(np.float64)
    counts[counts == 0] = 1  # avoid divide-by-zero for an absent class
    weights = counts.sum() / (num_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)


def run_epoch(model, loader, criterion, optimizer=None, device=DEVICE):
    """
    One pass over `loader`. Pass optimizer=None for validation/test so
    no gradient step is taken and dropout/batchnorm behave in eval mode.
    """
    is_training = optimizer is not None
    model.train() if is_training else model.eval()

    total_loss = 0.0
    correct = 0
    total = 0

    context = torch.enable_grad() if is_training else torch.no_grad()

    with context:
        for X_batch, y_batch in loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            if is_training:
                optimizer.zero_grad()

            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)

            if is_training:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), GRADIENT_CLIP_NORM)
                optimizer.step()

            total_loss += loss.item() * X_batch.size(0)
            predictions = torch.argmax(outputs, dim=1)
            correct += (predictions == y_batch).sum().item()
            total += X_batch.size(0)

    return total_loss / total, correct / total


def monte_carlo_validation(predictions, y_test):
    trade_results = []

    for pred, actual in zip(predictions, y_test):
        if pred == actual:
            trade_results.append(10)
        else:
            trade_results.append(-10)

    mc = MonteCarloEngine()
    results = mc.simulate(trade_results)

    print("Monte Carlo Results:")
    print(results)


def main():
    print("Loading market data...")
    df = pd.read_csv(DATA_PATH)
    df["time"] = pd.to_datetime(df["time"])

    print("Building features...")
    df = build_features(df)

    print("Chronological train/val/test split...")
    train_df, val_df, test_df = chronological_split(df)
    print(f"  train={len(train_df)} val={len(val_df)} test={len(test_df)}")

    print("Generating labels...")
    train_labels = triple_barrier_labels(train_df["close"].values, train_df["atr"].values)
    val_labels = triple_barrier_labels(val_df["close"].values, val_df["atr"].values)
    test_labels = triple_barrier_labels(test_df["close"].values, test_df["atr"].values)

    print("Building sequences (fitting scaler on train split only)...")
    X_train, y_train, scaler = build_sequences(
        train_df, train_labels, sequence_length=SEQUENCE_LENGTH, fit_scaler=True
    )
    X_val, y_val, _ = build_sequences(
        val_df, val_labels, sequence_length=SEQUENCE_LENGTH, scaler=scaler
    )
    X_test, y_test, _ = build_sequences(
        test_df, test_labels, sequence_length=SEQUENCE_LENGTH, scaler=scaler
    )

    if len(X_train) == 0 or len(X_val) == 0:
        raise RuntimeError(
            "Not enough rows to build even one sequence in every split. "
            "Either lower SEQUENCE_LENGTH in core/config.py or provide more data."
        )

    print(f"  X_train={X_train.shape} X_val={X_val.shape} X_test={X_test.shape}")

    train_loader = DataLoader(
        MarketDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True
    )
    val_loader = DataLoader(
        MarketDataset(X_val, y_val), batch_size=BATCH_SIZE, shuffle=False
    )
    test_loader = DataLoader(
        MarketDataset(X_test, y_test), batch_size=BATCH_SIZE, shuffle=False
    )

    print("Building model...")
    model = NeuroLLaCore().to(DEVICE)

    class_weights = compute_class_weights(y_train).to(DEVICE)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    trainer = Trainer(model, optimizer, criterion)

    print("Training...")
    best_val_loss = float("inf")
    epochs_without_improvement = 0

    for epoch in range(EPOCHS):
        train_loss, train_acc = run_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, criterion, optimizer=None)

        print(
            f"Epoch {epoch + 1}/{EPOCHS} | "
            f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} | "
            f"val_loss={val_loss:.4f} val_acc={val_acc:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_without_improvement = 0
            trainer.save_checkpoint(epoch, val_loss)
        else:
            epochs_without_improvement += 1

            if epochs_without_improvement >= EARLY_STOPPING_PATIENCE:
                print(f"No val improvement for {EARLY_STOPPING_PATIENCE} epochs, stopping early.")
                break

    print("Loading best checkpoint (by validation loss) for final evaluation...")
    trainer.load_checkpoint()

    print("Evaluating on held-out test split...")
    test_loss, test_acc = run_epoch(model, test_loader, criterion, optimizer=None)
    print(f"Test loss={test_loss:.4f} Test accuracy={test_acc:.4f}")

    model.eval()
    all_predictions = []
    with torch.no_grad():
        for X_batch, _ in test_loader:
            outputs = model(X_batch.to(DEVICE))
            preds = torch.argmax(outputs, dim=1).cpu().numpy()
            all_predictions.extend(preds)

    monte_carlo_validation(all_predictions, y_test)

    print("Saving final model and scaler...")
    os.makedirs(MODEL_DIR, exist_ok=True)
    torch.save(model.state_dict(), MODEL_SAVE_PATH)
    save_scaler(scaler, SCALER_SAVE_PATH)

    print(f"Model saved to {MODEL_SAVE_PATH}")
    print(f"Scaler saved to {SCALER_SAVE_PATH}")


if __name__ == "__main__":
    main()
