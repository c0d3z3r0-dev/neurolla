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

        return None