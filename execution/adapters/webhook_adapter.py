import requests


class WebhookAdapter:
    def __init__(
        self,
        credentials
    ):
        self.url = credentials.get(
            "url"
        )

    def execute(
        self,
        signal_packet
    ):
        response = requests.post(
            self.url,
            json=signal_packet
        )

        return response.json()