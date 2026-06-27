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
        if not self.url:
            return {
                "status": "error",
                "detail": "No webhook URL configured"
            }

        try:
            response = requests.post(
                self.url,
                json=signal_packet,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.RequestException as error:
            return {
                "status": "error",
                "detail": str(error)
            }
