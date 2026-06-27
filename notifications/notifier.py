from notifications.telegram_notifier import (
    TelegramNotifier
)

from notifications.email_notifier import (
    EmailNotifier
)


class NeuroLLaNotifier:
    def __init__(
        self,
        telegram_config=None,
        email_config=None
    ):
        self.telegram = None
        self.email = None

        if telegram_config:
            self.telegram = TelegramNotifier(
                telegram_config["bot_token"],
                telegram_config["chat_id"]
            )

        if email_config:
            self.email = EmailNotifier(
                email_config["email"],
                email_config["password"]
            )

    def alert(
        self,
        message
    ):
        if self.telegram:
            self.telegram.send(
                message
            )

    def email_alert(
        self,
        recipient,
        subject,
        body
    ):
        if self.email:
            self.email.send(
                recipient,
                subject,
                body
            )