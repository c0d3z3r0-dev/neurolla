import websocket
import json


class DerivValidator:
    def __init__(self):
        self.url = (
            "wss://ws.derivws.com/"
            "websockets/v3?app_id=1089"
        )

    def validate(self, token):
        ws = websocket.WebSocket()
        ws.connect(self.url)

        payload = {
            "authorize": token
        }

        ws.send(
            json.dumps(payload)
        )

        response = json.loads(
            ws.recv()
        )

        ws.close()

        if "error" in response:
            return False, response["error"]

        return True, response