# NeuroLLa Mobile - Deriv

A minimal, single-user mobile web app for running NeuroLLaCore from a
phone and trading directly on Deriv. This is deliberately separate
from `server/main.py` (the multi-user SaaS API) — there's no login,
no database, no bot scheduler. It holds one Deriv session in memory
per browser tab and is meant for one person using it themselves.

## Before running this

1. Train a model first if you haven't (`python train.py`) — this app
   loads whatever checkpoint exists at `core.config.MODEL_SAVE_PATH`
   (`models/trained/neurolla.pth`) plus its scaler. It will show a
   clear error on the page if that file doesn't exist yet rather than
   crashing the whole app.
2. Get a Deriv API token from Deriv's account settings → API token
   page, with trade permissions enabled.

## Running it

```bash
pip install -r requirements.txt
python -m mobile_app.main
```

This starts a server on port 8080, bound to `0.0.0.0` so a phone on
the same Wi-Fi network can reach it. The terminal output will show the
URL to use — on your phone, browse to
`http://<your-computer's-LAN-IP>:8080` (find that IP with `ipconfig`
on Windows or `ifconfig`/`ip addr` on Linux/Mac, on the same network
as the phone).

For access from outside your local network (e.g. a real deployed
phone app, not just testing on the same Wi-Fi), put this behind a
reverse proxy with HTTPS — never expose port 8080 directly to the
public internet, since the page itself has no login and anyone who
reaches it can type in a Deriv token and trade with it.

## What it does

1. **Connect** — paste a Deriv API token, tap Connect. This performs
   a real `authorize` call against Deriv's API
   (`execution/deriv_executor.py` → `execution/deriv_client.py`) and
   shows a clear error if the token is invalid or unreachable.
2. **Get signal** — fetches the last ~300 5-minute candles for the
   selected symbol from Deriv (`execution/deriv_market_data.py`), runs
   them through the same feature pipeline and model used everywhere
   else in this codebase (`core/features.py`, `core/inference.py`),
   and shows the prediction (BUY/SELL/HOLD), confidence, and the
   ATR-based entry/SL/TP the model implies.
3. **Place trade** — only enabled when the last signal was BUY or SELL
   *and* confidence is at or above `core.config.MIN_CONFIDENCE` (68%
   by default). Sends the trade to Deriv as a CALL/PUT contract via
   `DerivExecutor.execute()`.

## Known limitation: trading volume

Deriv's public candle API doesn't return tick/volume data the way MT5
does. This app fills `tick_volume` with a constant placeholder, which
is one of the model's 29 raw input features — so predictions made on
Deriv candle data lose whatever volume signal the model learned during
training on MT5 data. If volume signal matters for your results,
either retrain a Deriv-specific model without that column, or treat
Deriv-sourced signals as somewhat less reliable than ones computed
from real MT5 data.

## What this app deliberately does NOT do

- No multi-user accounts, no `/auth/google`, no session tokens — this
  is single-user by design.
- Does not go through `commander.py`, `BrokerRouter`, or the bot
  scheduler — it calls Deriv directly. If you want automated,
  always-on trading rather than a manual "check and tap" tool, that's
  `scheduler/bot_runner.py` via the main API
  (see `docs/FRONTEND_AND_BROKER_INTEGRATION.md`), not this app.
- Does not store trade history anywhere. Whatever Deriv's own app
  shows is the source of truth for what actually happened to your
  account.
