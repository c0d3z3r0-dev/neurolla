import pandas as pd


class CorrelationEngine:
    def __init__(self):
        self.threshold = 0.80

    def compute(
        self,
        price_map
    ):
        df = pd.DataFrame(price_map)

        corr = df.corr()

        return corr

    def highly_correlated(
        self,
        symbol_a,
        symbol_b,
        corr_matrix
    ):
        value = corr_matrix.loc[
            symbol_a,
            symbol_b
        ]

        return abs(value) >= self.threshold