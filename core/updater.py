import pandas as pd


class TradeUpdater:
    def __init__(
        self,
        path="logs/trade_journal.csv"
    ):
        self.path = path

    def update_trade(
        self,
        index,
        result
    ):
        df = pd.read_csv(self.path)

        if index < len(df):
            df.loc[index, "result"] = result

            df.to_csv(
                self.path,
                index=False
            )

            print(
                f"Trade {index} updated to {result}"
            )