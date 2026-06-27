class ExposureEngine:
    """
    Tracks net currency exposure across all open positions.
    Each BUY of BASEQUOTE longs the base currency and shorts the quote
    currency (and vice-versa for SELL). Positions must be released via
    remove_position when they close, or exposure accumulates forever.
    """

    def __init__(self):
        self.currency_exposure = {}
        self.open_positions = {}

    def _adjust(self, base, quote, delta):
        self.currency_exposure[base] = self.currency_exposure.get(base, 0) + delta
        self.currency_exposure[quote] = self.currency_exposure.get(quote, 0) - delta

    def add_position(self, symbol, direction):
        base = symbol[:3]
        quote = symbol[3:]

        delta = 1 if direction == "BUY" else -1
        self._adjust(base, quote, delta)

        self.open_positions[symbol] = direction

    def remove_position(self, symbol):
        direction = self.open_positions.pop(symbol, None)

        if direction is None:
            return

        base = symbol[:3]
        quote = symbol[3:]

        # Reverse exactly what add_position applied.
        delta = -1 if direction == "BUY" else 1
        self._adjust(base, quote, delta)

    def report(self):
        return self.currency_exposure
