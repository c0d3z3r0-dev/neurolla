class PairClusters:
    def __init__(self):
        self.clusters = {
            "USD_MAJORS": [
                "EURUSD",
                "GBPUSD",
                "AUDUSD",
                "NZDUSD"
            ],
            "JPY_CROSSES": [
                "USDJPY",
                "EURJPY",
                "GBPJPY"
            ],
            "COMMODITY": [
                "USDCAD",
                "AUDUSD"
            ]
        }

    def get_cluster(
        self,
        symbol
    ):
        for cluster, pairs in self.clusters.items():
            if symbol in pairs:
                return cluster

        # Symbols outside the known clusters get their own cluster keyed
        # by symbol, instead of all sharing the same "unclustered" bucket
        # (which previously meant the first unlisted symbol traded would
        # block every other unlisted symbol from ever trading).
        return f"UNCLUSTERED_{symbol}"