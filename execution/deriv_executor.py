from execution.deriv_client import DerivClient

# Deriv's forex symbols use an "frx" prefix; synthetic indices and
# other instrument types use their own distinct naming and aren't
# covered by this simple mapping. Extend this dict as you add more
# tradeable symbols.
DERIV_SYMBOL_MAP = {
    "EURUSD": "frxEURUSD",
    "GBPUSD": "frxGBPUSD",
    "USDJPY": "frxUSDJPY",
    "AUDUSD": "frxAUDUSD",
    "USDCAD": "frxUSDCAD",
}


def to_deriv_symbol(symbol):
    return DERIV_SYMBOL_MAP.get(symbol, f"frx{symbol}")


class DerivExecutor:
    def __init__(
        self,
        api_token
    ):
        self.client = DerivClient(
            api_token
        )

        auth = self.client.authorize()

        print("Authorized:", auth)

    def execute(
        self,
        signal_packet
    ):
        signal = signal_packet["signal"]

        if signal == "HOLD":
            print("No trade.")
            return {"status": "hold"}

        contract_type = (
            "CALL"
            if signal == "BUY"
            else "PUT"
        )

        amount = max(
            1,
            round(
                signal_packet["risk"] * 100,
                2
            )
        )

        # Deriv requires its own symbol naming (the frx prefix for
        # forex), distinct from the plain "EURUSD" the model and the
        # rest of this codebase use internally.
        deriv_symbol = to_deriv_symbol(
            signal_packet.get("symbol", "EURUSD")
        )

        result = self.client.buy_contract(
            symbol=deriv_symbol,
            amount=amount,
            contract_type=contract_type
        )

        print("Trade result:", result)

        return result

    def close(self):
        self.client.close()