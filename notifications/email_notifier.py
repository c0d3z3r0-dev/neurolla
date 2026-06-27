import smtplib
from email.message import EmailMessage


class EmailNotifier:
    def __init__(
        self,
        email_address,
        password
    ):
        self.email_address = email_address
        self.password = password

    def send(
        self,
        recipient,
        subject,
        body
    ):
        msg = EmailMessage()

        msg["Subject"] = subject
        msg["From"] = self.email_address
        msg["To"] = recipient

        msg.set_content(body)

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as server:
            server.starttls()

            server.login(
                self.email_address,
                self.password
            )

            server.send_message(msg)