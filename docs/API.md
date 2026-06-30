# API Documentation

Base URL (local development):

```text
http://localhost:8000
```

All endpoints except `/auth/google` require a session token. See
`FRONTEND_AND_BROKER_INTEGRATION.md` for the full auth flow and request/response
bodies. This page is a quick reference for routes only.

---

# Auth

POST `/auth/google`

Exchanges a Google ID token for a NeuroLLa session token. No auth header
required on this one endpoint.

---

# Users

GET `/users/me`

Returns the authenticated caller's own user record. There is no endpoint
that lists or creates users directly — accounts are created automatically
on first successful `/auth/google` login.

---

# Broker

POST `/broker/register`

Registers and encrypts a broker's credentials for the authenticated user.

---

# Config

POST `/config/save`

Stores bot settings (capital, risk level, confidence threshold, auto-trade)
for the authenticated user.

---

# Bot Runtime

POST `/bot/start`
POST `/bot/stop`
GET `/bot/status`

All three act on the authenticated caller's own bot — there is no
`user_id` path parameter; the user is identified by the session token.

---

# Trades

GET `/trades`
GET `/trades/open`
GET `/trades/closed`

Return only the authenticated caller's own trades.

---

# Analytics

GET `/analytics`
GET `/analytics/equity`

Return only the authenticated caller's own performance figures.

---

# Risk

POST `/risk/save`
POST `/risk/emergency-stop`

`/risk/emergency-stop` halts only the authenticated caller's own bot.
