# Notification System Documentation

NeuroLLa sends operational alerts.

---

# Channels

- Telegram
- Email

Future:

- WhatsApp
- Push notifications

---

# Alert Types

- trade executed
- trade closed
- risk blocked
- emergency stop
- runtime errors

---

# Telegram

File:

```text
notifications/telegram_notifier.py
```

Uses Telegram Bot API.

Supports mobile delivery.

---

# Email

File:

```text
notifications/email_notifier.py
```

Uses SMTP.

---

# Unified Layer

File:

```text
notifications/notifier.py
```

Central dispatch system.