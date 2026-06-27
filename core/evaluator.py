import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from core.config import FEATURE_COLUMNS, SEQUENCE_LENGTH


def build_sequences(df, labels, sequence_length=SEQUENCE_LENGTH, scaler=None, fit_scaler=False):
    """
    Slices df into overlapping windows of length `sequence_length` over
    every column in core.config.FEATURE_COLUMNS, paired with the label
    at the end of each window.

    Scaling: a single StandardScaler is used for the whole call, not
    refit per window. Pass a previously-fitted scaler (from training)
    when building sequences for validation/test/live data so the same
    scale is applied everywhere. Pass fit_scaler=True only on the
    training split.

    Returns (X, y, scaler) where X has shape
    (num_windows, sequence_length, len(FEATURE_COLUMNS)).
    """
    features = df[FEATURE_COLUMNS].values.astype(np.float64)

    if scaler is None:
        scaler = StandardScaler()

    if fit_scaler:
        scaler.fit(features)

    normalized = scaler.transform(features)

    max_index = min(len(normalized), len(labels))

    X = []
    y = []

    for i in range(sequence_length, max_index):
        window = normalized[i - sequence_length:i]
        X.append(window)
        y.append(labels[i])

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.int64), scaler


def save_scaler(scaler, path):
    joblib.dump(scaler, path)


def load_scaler(path):
    return joblib.load(path)
