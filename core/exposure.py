class ExposureEngine:
    def __init__(self):
        self.currency_exposure = {}

    def add_position(
        self,
        symbol,
        direction
    ):
        base = symbol[:3]
        quote = symbol[3:]

        if direction == "BUY":
            self.currency_exposure[base] = (
                self.currency_exposure.get(base, 0) + 1
            )

            self.currency_exposure[quote] = (
                self.currency_exposure.get(quote, 0) - 1
            )

        elif direction == "SELL":
            self.currency_exposure[base] = (
                self.currency_exposure.get(base, 0) - 1
            )

            self.currency_exposure[quote] = (
                self.currency_exposure.get(quote, 0) + 1
            )

    def report(self):
        return self.currency_exposure