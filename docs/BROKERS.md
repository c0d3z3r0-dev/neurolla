# Broker Integration Documentation

NeuroLLa is broker-agnostic at the interface level. Execution is
abstracted through adapters, all implementing the same `execute(signal_packet)`
method. See `FRONTEND_AND_BROKER_INTEGRATION.md` for the full credential
shapes and setup steps per broker. This page summarizes what each one
actually does today.

---

# Broker Router

File: `execution/broker_router.py`

```text
Signal Packet → BrokerRouter → Adapter Selection → execute()
```

`BrokerRouter("mt5"|"deriv"|"ctrader"|"binance"|"webhook", credentials)`
picks the adapter by name and forwards every `execute()` call to it.

---

# Real execution vs. simulated adapters

This is the most important distinction for anyone integrating a broker:

| Broker     | Through BrokerRouter            | Real order placement                  |
|------------|----------------------------------|----------------------------------------|
| MT5        | Simulated (SL/TP math only)      | `live/trader.py` (direct, not via router) |
| Deriv      | Simulated (SL/TP math only)      | `execution/deriv_executor.py` (not yet wired into the router) |
| cTrader    | Simulated only                   | Not implemented                        |
| Binance    | Simulated only                   | Not implemented                        |
| Webhook    | Real HTTP POST to your URL       | Whatever your endpoint does with it    |

The MT5 and Deriv adapters inside `execution/adapters/` compute the same
ATR-based stop-loss/take-profit every other adapter computes and return a
`status: "simulated"` response — they do not place a live order. Real MT5
orders go through `live/trader.py`, which calls `mt5.order_send()` directly
and is used by the live trading loop (`scheduler/bot_runner.py` →
`commander.py`), not through `BrokerRouter`. A real, websocket-based Deriv
order client exists (`execution/deriv_client.py` + `execution/deriv_executor.py`)
but isn't yet called from `BrokerRouter` either — use `run_deriv.py` directly
if you want to exercise it.

If you are building a UI that shows "order placed" to a user, make sure
you know which path produced that response.

---

# MetaTrader 5

Adapter: `execution/adapters/mt5_adapter.py` (simulated only)
Real execution: `live/trader.py`

MT5 does not take login credentials through this codebase at all. It
connects to whichever MT5 terminal is already installed and logged in on
the machine running the bot (`mt5.initialize()`). There is no
`username`/`password` field to register — registering `"mt5"` via
`/broker/register` only stores a placeholder credentials blob for
record-keeping; it has no effect on which account actually trades.

Supports: forex, indices, commodities (whatever the logged-in MT5 account has access to).

---

# Deriv

Adapter: `execution/adapters/deriv_adapter.py` (simulated)
Real client: `execution/deriv_client.py`, `execution/deriv_executor.py`

Authentication: API token only.

Credentials shape:

```json
{ "api_token": "your-deriv-api-token" }
```

`/broker/register` validates the token live against Deriv's websocket API
before storing it — this is the only broker with server-side validation
today.

Supports: synthetic indices, forex, multipliers.

---

# cTrader

Adapter: `execution/adapters/ctrader_adapter.py` (simulated only — no real execution path exists yet)

Credentials shape:

```json
{ "client_id": "...", "client_secret": "..." }
```

Stored, but not validated, and not connected to a real cTrader Open API session.

---

# Binance

Adapter: `execution/adapters/binance_adapter.py` (simulated only — no real execution path exists yet)

Credentials shape:

```json
{ "api_key": "...", "api_secret": "..." }
```

Stored, but not validated, and not connected to the real Binance API.

---

# Webhook

Adapter: `execution/adapters/webhook_adapter.py` — the only adapter that
makes a real outbound call by default.

Use this to forward signals to any broker or service this codebase
doesn't natively support.

Credentials shape:

```json
{ "url": "https://your-endpoint.example.com/trade" }
```

`execute()` POSTs the full signal packet to your URL as JSON and returns
your endpoint's JSON response. A failed or unreachable URL returns
`{"status": "error", "detail": "..."}` rather than raising.

---

# Adapter interface

Every adapter implements:

```python
execute(signal_packet) -> dict
```

`signal_packet` always contains `symbol`, `signal` (`"BUY"`/`"SELL"`/`"HOLD"`),
`confidence`, `entry`, and `atr`. A successful simulated response looks like:

```json
{ "status": "simulated", "entry": 1.1000, "sl": 1.0995, "tp": 1.1010 }
```
