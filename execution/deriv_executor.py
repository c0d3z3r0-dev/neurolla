from execution.deriv_client import DerivClient


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

        result = self.client.buy_contract(
            symbol="frxEURUSD",
            amount=amount,
            contract_type=contract_type
        )

        print("Trade result:", result)