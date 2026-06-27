# Broker Integration Documentation

NeuroLLa is broker-agnostic.

Execution is abstracted through adapters.

---

# Broker Router

File:

```text
execution/broker_router.py
```

Flow:

```text
Signal Packet
↓
Broker Router
↓
Adapter Selection
↓
Execution
```

---

# Supported Brokers

## MetaTrader 5

Adapter:

```text
execution/adapters/mt5_adapter.py
```

Supports:

- forex
- indices
- commodities

Capabilities:

- order placement
- account management
- balance checks

---

## Deriv

Supports:

- synthetic indices
- forex
- multipliers

Authentication:

API token

Validation:

Live websocket authorization

---

## cTrader

Supports:

- ECN forex
- CFDs

---

## Binance

Supports:

- crypto spot
- futures

---

## Webhook

Universal adapter.

Allows:

Any external broker integration.

Payload:

```json
{
  "symbol": "...",
  "signal": "...",
  "confidence": ...
}
```

---

# Adapter Interface

All adapters implement:

```python
execute(signal_packet)
```

This standardizes execution.