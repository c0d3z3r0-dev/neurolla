import pandas as pd

from core.features import build_features
from core.inference import ModelInference
from core.config import MIN_CONFIDENCE


def test_model():
    df = pd.read_csv(
        "data/raw/market.csv"
    )
    df["time"] = pd.to_datetime(df["time"])

    df = build_features(df)

    inference = ModelInference()

    label_index, label_name, confidence = inference.predict(df)

    print("Prediction:", label_name)
    print("Confidence:", confidence)

    if confidence < MIN_CONFIDENCE:
        print("NO TRADE")
    else:
        print(label_name)


if __name__ == "__main__":
    test_model()
