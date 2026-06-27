from core.exposure import ExposureEngine
from core.clusters import PairClusters
from core.allocator import CapitalAllocator


class PortfolioManager:
    def __init__(
        self,
        balance
    ):
        self.exposure = ExposureEngine()
        self.clusters = PairClusters()
        self.allocator = CapitalAllocator(
            balance
        )

        self.active_clusters = set()

    def approve_trade(
        self,
        symbol,
        direction,
        confidence
    ):
        cluster = self.clusters.get_cluster(
            symbol
        )

        if cluster in self.active_clusters:
            return False, 0

        capital = self.allocator.allocate(
            confidence
        )

        self.exposure.add_position(
            symbol,
            direction
        )

        self.active_clusters.add(
            cluster
        )

        return True, capital

    def release_trade(self, symbol):
        """
        Must be called when a position on `symbol` closes, or its
        cluster stays blocked and its exposure stays counted forever.
        """
        cluster = self.clusters.get_cluster(symbol)
        self.active_clusters.discard(cluster)
        self.exposure.remove_position(symbol)
