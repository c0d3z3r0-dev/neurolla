import torch
import torch.nn.functional as F
import pandas as pd

from networks.hybrid_model import NeuroLLaCore
from core.features import build_features
from core.evaluator import build_sequences


def test_model():
    df = pd.read_csv(
        "data/raw/market.csv"
    )

    df = build_features(df)

    dummy_labels = [1] * len(df)

    X, _ = build_sequences(
        df,
        dummy_labels
    )

    latest = torch.tensor(
        X[-1:],
        dtype=torch.float32
    )

    model = NeuroLLaCore()

    model.load_state_dict(
        torch.load(
            "models/trained/neurolla.pth"
        )
    )

    model.eval()

    with torch.no_grad():
        logits = model(latest)

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

    print("Prediction:", prediction)
    print("Confidence:", confidence)

    if confidence < 0.68:
        print("NO TRADE")

    else:
        if prediction == 0:
            print("SELL")

        elif prediction == 1:
            print("HOLD")

        elif prediction == 2:
            print("BUY")


if __name__ == "__main__":
    test_model()