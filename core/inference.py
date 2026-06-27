import torch
import numpy as np
from core.config import (
    FEATURE_COLUMNS,
    SEQUENCE_LENGTH,
    MODEL_SAVE_PATH,
    SCALER_SAVE_PATH,
    DEVICE
)
from core.evaluator import load_scaler
from networks.hybrid_model import NeuroLLaCore

CLASS_NAMES = {0: "SELL", 1: "HOLD", 2: "BUY"}


class ModelInference:
    """
    Single, shared way to load NeuroLLaCore and run live/backtest
    inference on a features dataframe. Every module that needs a
    prediction (live/trader.py, live/confluence.py,
    execution/signal_engine.py, backtesting/engine.py) should use this
    instead of re-implementing model loading + scaling + windowing,
    which is what previously caused the same feature-mismatch bug to
    exist in four different places at once.
    """

    def __init__(
        self,
        model_path=MODEL_SAVE_PATH,
        scaler_path=SCALER_SAVE_PATH,
        sequence_length=SEQUENCE_LENGTH,
        device=DEVICE
    ):
        self.sequence_length = sequence_length
        self.device = device

        self.model = NeuroLLaCore().to(device)
        self.model.load_state_dict(
            torch.load(model_path, map_location=device)
        )
        self.model.eval()

        self.scaler = load_scaler(scaler_path)

    def predict(self, df):
        """
        df must already have every column in core.config.FEATURE_COLUMNS
        (i.e. it has already been through core.features.build_features)
        and at least `sequence_length` rows. Uses only the most recent
        `sequence_length` rows - this is for live/next-bar inference,
        not bulk backtesting (use predict_all for that).

        Returns (label_index, label_name, confidence) for the most
        recent bar.
        """
        if len(df) < self.sequence_length:
            raise ValueError(
                f"Need at least {self.sequence_length} rows to predict, got {len(df)}"
            )

        window = df[FEATURE_COLUMNS].values[-self.sequence_length:]
        normalized = self.scaler.transform(window)

        tensor = torch.tensor(normalized, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.model(tensor)
            probabilities = torch.softmax(logits, dim=1)
            confidence, predicted = torch.max(probabilities, dim=1)

        label_index = predicted.item()
        return label_index, CLASS_NAMES[label_index], confidence.item()

    def predict_all(self, df):
        """
        Bulk inference over every valid window in df - used by
        backtesting, where we want a prediction for every historical
        bar, not just the latest one. Returns parallel numpy arrays
        (label_indices, confidences) aligned so that prediction i
        corresponds to df.iloc[i + sequence_length - 1].
        """
        features = df[FEATURE_COLUMNS].values
        normalized = self.scaler.transform(features)

        windows = []
        for i in range(self.sequence_length, len(normalized) + 1):
            windows.append(normalized[i - self.sequence_length:i])

        if not windows:
            return [], []

        windows = np.array(windows, dtype=np.float32)
        tensor = torch.tensor(windows, dtype=torch.float32).to(self.device)

        label_indices = []
        confidences = []

        batch_size = 256
        with torch.no_grad():
            for start in range(0, len(tensor), batch_size):
                batch = tensor[start:start + batch_size]
                logits = self.model(batch)
                probabilities = torch.softmax(logits, dim=1)
                conf, pred = torch.max(probabilities, dim=1)
                label_indices.extend(pred.cpu().numpy().tolist())
                confidences.extend(conf.cpu().numpy().tolist())

        return label_indices, confidences
