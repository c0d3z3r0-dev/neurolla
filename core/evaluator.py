import numpy as np
from sklearn.preprocessing import StandardScaler


def build_sequences(
    df,
    labels,
    sequence_length=50
):
    features = df[
        [
            "close",
            "ema20",
            "ema50",
            "rsi",
            "atr",
            "volatility"
        ]
    ].values

    X = []
    y = []

    scaler = StandardScaler()

    max_index = min(
        len(features),
        len(labels)
    )

    for i in range(
        sequence_length,
        max_index
    ):
        train_window = features[
            i-sequence_length:i
        ]

        scaler.fit(train_window)

        normalized = scaler.transform(
            train_window
        )

        X.append(normalized)
        y.append(labels[i])

    return (
        np.array(X),
        np.array(y)
    )