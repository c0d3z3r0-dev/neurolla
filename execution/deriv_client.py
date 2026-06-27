import websocket
import json


class DerivClient:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = websocket.WebSocket()

        self.ws.connect(
            "wss://ws.derivws.com/websockets/v3?app_id=1089"
        )

    def authorize(self):
        payload = {
            "authorize": self.api_token
        }

        self.ws.send(
            json.dumps(payload)
        )

        response = json.loads(
            self.ws.recv()
        )

        return response

    def buy_contract(
        self,
        symbol,
        amount,
        contract_type,
        duration=5
    ):
        proposal = {
            "buy": 1,
            "price": amount,
            "parameters": {
                "symbol": symbol,
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": duration,
                "duration_unit": "m"
            }
        }

        self.ws.send(
            json.dumps(proposal)
        )

        response = json.loads(
            self.ws.recv()
        )

        return response