import random
import numpy as np


class MonteCarloEngine:
    def simulate(
        self,
        trade_results,
        runs=1000
    ):
        outcomes = []

        for _ in range(runs):
            shuffled = trade_results[:]
            random.shuffle(shuffled)

            equity = np.cumsum(
                shuffled
            )

            outcomes.append(
                equity[-1]
            )

        return {
            "mean": np.mean(outcomes),
            "worst": np.min(outcomes),
            "best": np.max(outcomes)
        }