class CapitalAllocator:
    def __init__(
        self,
        total_balance
    ):
        self.total_balance = total_balance
        self.max_per_trade = 0.20

    def allocate(
        self,
        confidence
    ):
        capital = (
            self.total_balance *
            self.max_per_trade *
            confidence
        )

        return capital