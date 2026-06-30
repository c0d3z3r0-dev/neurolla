import websocket
import json

DERIV_WS_URL = "wss://ws.derivws.com/websockets/v3?app_id=1089"


class DerivClient:
    def __init__(self, api_token, timeout=10):
        self.api_token = api_token
        self.ws = websocket.WebSocket()
        self.ws.settimeout(timeout)

        try:
            self.ws.connect(DERIV_WS_URL)
        except (websocket.WebSocketException, OSError) as error:
            raise ConnectionError(
                f"Failed to connect to Deriv websocket: {error}"
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

        if "error" in response:
            raise PermissionError(
                f"Deriv authorization failed: {response['error']}"
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

    def get_candles(
        self,
        symbol,
        granularity=300,
        count=300
    ):
        """
        Fetches recent OHLC candles via Deriv's ticks_history API.
        granularity is in seconds (300 = 5 minutes, matching the M5
        timeframe the model was trained on). Returns a list of dicts
        with epoch/open/high/low/close - the caller is responsible for
        turning this into the dataframe shape core.features.build_features
        expects (time, open, high, low, close, tick_volume).
        """
        request = {
            "ticks_history": symbol,
            "adjust_start_time": 1,
            "count": count,
            "end": "latest",
            "start": 1,
            "style": "candles",
            "granularity": granularity
        }

        self.ws.send(
            json.dumps(request)
        )

        response = json.loads(
            self.ws.recv()
        )

        if "error" in response:
            raise RuntimeError(
                f"Deriv candle fetch failed: {response['error']}"
            )

        return response.get("candles", [])

    def close(self):
        self.ws.close()
