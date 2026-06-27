# API Documentation

Base:

```text
http://localhost:8000
```

---

# Auth

POST:

```text
/auth/google
```

Purpose:

Google authentication.

---

# Users

POST:

```text
/users/create
```

GET:

```text
/users
```

---

# Broker

POST:

```text
/broker/register
```

Registers broker credentials.

---

# Config

POST:

```text
/config/save
```

Stores bot settings.

---

# Bot Runtime

POST:

```text
/bot/start
```

POST:

```text
/bot/stop
```

GET:

```text
/bot/status/{user_id}
```

---

# Trades

GET:

```text
/trades/{user_id}
```

GET:

```text
/trades/open/{user_id}
```

GET:

```text
/trades/closed/{user_id}
```

---

# Analytics

GET:

```text
/analytics
```

GET:

```text
/analytics/equity
```

---

# Risk

POST:

```text
/risk/save
```

POST:

```text
/risk/emergency-stop
```