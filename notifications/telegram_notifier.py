import requests


class TelegramNotifier:
    def __init__(
        self,
        bot_token,
        chat_id
    ):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send(
        self,
        message
    ):
        url = (
            f"https://api.telegram.org/"
            f"bot{self.bot_token}/sendMessage"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        requests.post(
            url,
            json=payload
        )