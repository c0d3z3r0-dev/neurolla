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
        if not self.bot_token or not self.chat_id:
            # TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID weren't set - log
            # locally instead of silently failing an HTTP call against
            # an empty bot token, which would otherwise look like a
            # successful send while actually doing nothing.
            print(f"[Telegram alert skipped - not configured]: {message}")
            return False

        url = (
            f"https://api.telegram.org/"
            f"bot{self.bot_token}/sendMessage"
        )

        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True

        except requests.RequestException as error:
            print(f"Telegram send failed: {error}")
            return False
