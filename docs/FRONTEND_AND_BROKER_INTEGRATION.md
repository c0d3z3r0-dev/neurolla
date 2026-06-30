# Frontend and Broker Integration Guide

This is the single reference for anyone connecting a client (web app,
mobile app, or any other frontend) to NeuroLLa, and for connecting
NeuroLLa to a broker or trading platform. It reflects the code as it
exists today, including the parts that are placeholders rather than
real execution — that distinction matters and is called out everywhere
it applies.

Related, narrower references:
- `API.md` — route list only, no detail.
- `BROKERS.md` — broker adapter behavior only, no detail.
- `mobile_app/README.md` — a ready-to-run, single-user mobile web app
  that connects to Deriv and runs the model directly, if you want
  something working on your phone today rather than building a
  frontend against the multi-user API described below.

---

## 1. Two ways to talk to NeuroLLa

There are two separate servers in this codebase. Connect to whichever
one matches what you're building.

| Server | File | Purpose | Auth |
|---|---|---|---|
| Main API | `server/main.py` | Account, broker registration, bot control, trades, analytics, risk | Required (session token) on every route except login |
| Mobile gateway | `mobile/api_gateway.py` | Read-only signal lookup for a single symbol | Required (session token) |

Both are FastAPI apps. Run either with `uvicorn`:

```bash
uvicorn server.main:app --reload --port 8000
uvicorn mobile.api_gateway:app --reload --port 8001
```

They are independent processes — running one does not start the
other, and they don't share any in-memory state (only the same SQLite
database file).

---

## 2. Environment setup (do this before anything else)

Copy `.env.example` to `.env` and fill in real values. Two of these
are not optional — the server will refuse to do anything useful
without them:

```bash
cp .env.example .env
```

```text
NEUROLLA_JWT_SECRET=        # required — server won't issue or verify sessions without it
NEUROLLA_ENCRYPTION_KEY=    # required — server refuses to store broker credentials without it
FIREBASE_CREDENTIALS_PATH=  # required only for /auth/google
TELEGRAM_BOT_TOKEN=         # optional — alerts are skipped (not crashed) if unset
TELEGRAM_CHAT_ID=           # optional, same as above
DERIV_API_TOKEN=            # only needed for run_deriv.py
MT5_TERMINAL_PATH=          # optional — auto-detects a running terminal if unset
```

Generate the two required secrets:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

`NEUROLLA_JWT_SECRET` should be at least 32 bytes — anything shorter
produces a warning and a weaker token. Never commit `.env`.

---

## 3. Frontend integration

### 3.1 Authentication flow

NeuroLLa uses Google Sign-In on the client, then exchanges that for
its own short-lived session token. The server never sees your Google
password — only the ID token your frontend's Google SDK already gave
you.

```text
Frontend (Google SDK)
  → gets a Google ID token
Frontend
  → POST /auth/google { "id_token": "<google id token>" }
Server
  → verifies it with Firebase
  → creates the user on first login, or finds the existing one
  → returns a NeuroLLa session token
Frontend
  → stores that token, sends it as a Bearer header on every other request
```

**Request:**

```http
POST /auth/google
Content-Type: application/json

{ "id_token": "<google-issued id token from your frontend's auth SDK>" }
```

**Response (first login):**

```json
{ "status": "account created", "user_id": 1, "session_token": "<jwt>" }
```

**Response (returning user):**

```json
{ "status": "login successful", "user_id": 1, "session_token": "<jwt>" }
```

From here on, every other request must include:

```http
Authorization: Bearer <session_token>
```

The token is valid for 24 hours. There is no refresh endpoint yet —
when it expires, send the user through `/auth/google` again. A
missing or invalid header returns `401`; there is no separate "token
expired" vs. "token invalid" distinction in the response body, just a
401 either way.

> **Do not** put `user_id` in a request body, query string, or URL
> path expecting the server to trust it. Every route derives the
> caller's identity from the bearer token alone, and ignores any
> `user_id` the client sends. This is deliberate — it's what stops one
> user from reading or controlling another user's account.

### 3.2 Typical screen-by-screen flow

**Onboarding:**
1. `POST /auth/google` → store the session token.
2. `GET /users/me` → display name/email.
3. `POST /broker/register` → connect at least one broker (see §4 for
   what each broker needs).
4. `POST /config/save` → capital, risk level, confidence threshold,
   auto-trade on/off.
5. `POST /risk/save` → daily loss limit, max trades/day, max drawdown.

**Dashboard:**
- `GET /bot/status` → is the bot currently running.
- `GET /trades`, `/trades/open`, `/trades/closed` → trade history.
- `GET /analytics` → win rate, profit factor, Sharpe, max drawdown.
- `GET /analytics/equity` → array of cumulative PnL for an equity
  curve chart.

**Controls:**
- `POST /bot/start` with `{ "broker": "...", "credentials": {...} }`
  starts the trading loop as a background process.
- `POST /bot/stop` stops it.
- `POST /risk/emergency-stop` sets a flag the running bot checks every
  cycle and halts on — this does **not** instantly kill open positions
  at the broker; it only stops the bot from opening new ones (see §3.4).

### 3.3 Request/response reference

All bodies are JSON. All protected routes need the `Authorization`
header from §3.1 — omitted below for brevity.

```http
GET /users/me
→ { "id": 1, "email": "...", "name": "...", "google_uid": "..." }
```

```http
POST /broker/register
{ "broker_name": "deriv", "credentials": { "api_token": "..." } }
→ { "status": "broker registered" }
   or { "status": "invalid token", "error": "..." }   (deriv only — see §4)
```

```http
POST /config/save
{ "capital": 1000, "risk_level": "moderate", "confidence_threshold": 0.7, "auto_trade": true }
→ { "status": "config saved" }
```

```http
POST /risk/save
{ "daily_loss_limit": 50, "max_trades_per_day": 10, "max_drawdown": 0.05 }
→ { "status": "risk saved" }
```

```http
POST /bot/start
{ "broker": "mt5", "credentials": {} }
→ { "status": "bot started" }  or  { "status": "already running" }
```

```http
POST /bot/stop
→ { "status": "bot stopped" }
```

```http
GET /bot/status
→ { "running": true }
```

```http
GET /trades
→ [ { "id": 1, "symbol": "EURUSD", "direction": "BUY", "entry": 1.1,
      "sl": 1.0995, "tp": 1.101, "confidence": 0.74, "volume": 0.5,
      "pnl": 0, "status": "OPEN", "opened_at": "...", "closed_at": null }, ... ]
```

```http
GET /analytics
→ { "total_trades": 12, "win_rate": 0.58, "total_pnl": 134.2,
    "profit_factor": 1.6, "sharpe_ratio": 0.9, "max_drawdown": 42.0 }
```

```http
GET /analytics/equity
→ { "equity_curve": [10.0, 22.0, 18.0, 41.0, ...] }
```

```http
POST /risk/emergency-stop
→ { "status": "bot halted" }
```

### 3.4 Things the frontend should know that aren't obvious from the routes

- **`/bot/start` runs the bot as a separate OS process**
  (`multiprocessing.Process`), not a background thread. If the API
  server restarts, that process registry is lost in memory — `GET
  /bot/status` after a server restart will show `false` even if a
  bot process is technically still alive in the background. Don't
  build a UI that assumes bot state survives an API server deploy.
- **`/risk/emergency-stop` is not instant flatten-all.** It sets
  `emergency_stop=True` on that user's risk row. The bot's next cycle
  (it polls broker data every 5 minutes by default —
  `POLL_INTERVAL_SECONDS` in `scheduler/bot_runner.py`) sees the flag
  and stops opening new trades. It does **not** close existing open
  positions at the broker. If you need a "close everything now" UI
  affordance, it doesn't exist yet — closing has to happen at the
  broker directly, or you'd need to add that.
- **There's no broker-credential update or delete endpoint yet** —
  only `/broker/register` to create one. Re-registering the same
  `broker_name` adds a second row rather than overwriting the first.
  If your UI needs "edit my broker connection," that's a gap to flag
  rather than something to work around silently.
- **MT5 has no login fields.** If your broker-connect screen shows a
  username/password form for MT5, that's misleading — see §4.1.
- **Confidence values you'll see in trade records are real model
  output**, not a UI placeholder — they come from
  `core/inference.py`'s softmax over the model's 3-class output
  (SELL/HOLD/BUY), averaged across the M5/M15/H1 confirmation
  timeframes in `live/confluence.py`.

---

## 4. Broker and platform integration

This section is what to put in a "Connect a broker" screen, and what
actually happens server-side for each one. See `BROKERS.md` for the
adapter-level detail (which ones are real execution vs. simulated).

### 4.1 MetaTrader 5

**What the user needs to do:** nothing through this API. MT5 connects
to whichever MT5 terminal is already installed and logged into an
account on the machine that runs the bot process — that's
`mt5.initialize()` in `live/mt5_connector.py`, called with no
credentials at all.

**What this means for your UI:** there is no username/password/server
form to build for MT5. If you call `/broker/register` with
`"broker_name": "mt5"`, it stores whatever `credentials` dict you send
unvalidated, purely for your own record-keeping — it has zero effect
on which MT5 account actually places trades. The real account is
whichever one is logged into the terminal on the host machine. This is
a deployment-time decision (which machine, which MT5 login), not
something configurable per-user through this API today.

**`MT5_TERMINAL_PATH`** (optional env var) only matters if you need to
launch a specific MT5 installation rather than use one that's already
running — most setups can leave it unset.

### 4.2 Deriv

**What the user needs to provide:** a Deriv API token (from Deriv's
account settings → API token page, with trade permissions enabled).

```json
{ "broker_name": "deriv", "credentials": { "api_token": "your-token-here" } }
```

POST this to `/broker/register`. The server validates the token live
against Deriv's websocket API before saving it (`DerivValidator` in
`server/broker_validation.py`) — if the token is bad or lacks
permissions, you'll get back `{"status": "invalid token", "error": "..."}`
instead of a success response. This is currently the only broker with
that server-side check.

**Important caveat:** registering a Deriv token through `/broker/register`
does not by itself make `/bot/start` place real Deriv orders. The
`BrokerRouter`'s `"deriv"` adapter only computes simulated SL/TP and
returns — it doesn't call Deriv's API. The real, order-placing Deriv
client (`execution/deriv_client.py` / `execution/deriv_executor.py`)
exists and works, but is currently only exercised through
`run_deriv.py`, not through the `/bot/start` → `commander.py` →
`BrokerRouter` path. If you're building toward real Deriv execution
through the bot loop, that wiring is the next piece of work, not
something already connected.

### 4.3 cTrader

**Status: registration only, no real execution path exists yet.**

```json
{ "broker_name": "ctrader", "credentials": { "client_id": "...", "client_secret": "..." } }
```

This stores OAuth-style credentials but nothing in the codebase
currently opens a real cTrader Open API session with them. The
`CTraderAdapter` is a labeled placeholder. Don't surface this as a
fully working option in a production UI yet — if you do, label it
clearly as "coming soon" or hide it behind a feature flag.

### 4.4 Binance

**Status: registration only, no real execution path exists yet.**

```json
{ "broker_name": "binance", "credentials": { "api_key": "...", "api_secret": "..." } }
```

Same caveat as cTrader — `BinanceAdapter` is a placeholder that
doesn't call the real Binance API.

### 4.5 Webhook (the one that's actually real today)

**What the user needs to provide:** a URL that accepts a POST with a
JSON body and ideally returns something useful back.

```json
{ "broker_name": "webhook", "credentials": { "url": "https://your-endpoint.example.com/trade" } }
```

This is the most reliable adapter to demo or to use as a bridge to a
broker this codebase doesn't natively support — point it at your own
small relay service that translates the signal packet into whatever
that broker's real API expects. It has a 10-second timeout and returns
a structured error (rather than crashing the bot loop) if the URL is
unreachable.

### 4.6 What a signal packet looks like, if you're building a webhook receiver

Whatever you put behind your webhook URL will receive exactly this
shape via POST, as JSON:

```json
{
  "symbol": "EURUSD",
  "signal": "BUY",
  "confidence": 0.74,
  "capital": 53.2,
  "entry": 1.10043,
  "atr": 0.00041
}
```

- `signal` is `"BUY"` or `"SELL"` — `"HOLD"` signals never reach
  execution; they're filtered out before the broker call.
- `confidence` is the model's softmax probability for the winning
  class (0–1), averaged across confirming timeframes.
- `capital` is the dollar amount NeuroLLa's own Kelly-based sizing
  decided to risk, already capped at `MAX_RISK_PER_TRADE` (2% by
  default) — your receiving service can use this directly for sizing,
  or recompute its own.
- `atr` is the latest Average True Range, in price units — useful if
  your receiving service wants to set its own stop distance
  consistent with what NeuroLLa used to size the trade
  (`TP_MULT`/`SL_MULT` in `core/config.py`, currently 2.0 / 1.0).

Your endpoint should return a JSON object. If you want the rest of the
pipeline (trade journaling) to behave the same way the built-in
adapters do, include `tp` and `sl` in your response:

```json
{ "status": "executed", "entry": 1.10043, "sl": 1.10002, "tp": 1.10125 }
```

### 4.7 Adding a broker that isn't listed here

1. Create `execution/adapters/<name>_adapter.py` with a class
   implementing `__init__(self, credentials)` and
   `execute(self, signal_packet) -> dict`. Use the existing adapters'
   ATR-based SL/TP pattern (import `TP_MULT`/`SL_MULT` from
   `core.config` so it stays consistent with everything else) unless
   you're calling a real API that returns its own fill price.
2. Register it in `execution/broker_router.py`'s `self.adapters` dict.
3. Document the credential shape it expects (mirror the tables in §4
   above) so the frontend team knows what form fields to build.
4. If real-money execution matters, write an integration test against
   that broker's sandbox/demo environment before wiring it into
   `/bot/start` — the simulated adapters currently in this codebase
   are easy to mistake for real execution if you don't check.

---

## 5. Quick checklist before going live with a frontend + broker

- [ ] `NEUROLLA_JWT_SECRET` and `NEUROLLA_ENCRYPTION_KEY` are set to
      real generated values, not left blank.
- [ ] Frontend sends `Authorization: Bearer <token>` on every request
      after login, and never sends `user_id` expecting it to be trusted.
- [ ] Frontend handles 401 by sending the user back through
      `/auth/google`, not by retrying the same request.
- [ ] You know, for whichever broker you're connecting, whether it's a
      **real** execution path or a **simulated** placeholder (§4) —
      don't advertise "live trading" on a broker that only computes
      fake SL/TP and returns.
- [ ] For MT5 specifically: confirm which machine and which logged-in
      account the bot process will actually use, since the API can't
      configure that per-user.
- [ ] Emergency stop is understood by support/ops staff as "stops new
      trades," not "closes everything right now."
