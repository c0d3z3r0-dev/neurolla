# Risk Management Documentation

NeuroLLa uses layered risk controls.

---

# Risk Layers

1. Portfolio Risk
2. Strategy Risk
3. Runtime Risk
4. Emergency Controls

---

# RiskGuard

File:

```text
core/risk_guard.py
```

Controls:

- daily loss limit
- max trades per day
- emergency stop

Logic:

```text
If limits exceeded:
Block trading
```

---

# ATR Stops

Dynamic:

```text
SL = ATR x 1.5
TP = ATR x 3.0
```

Benefits:

- volatility-adjusted
- adaptive

---

# Portfolio Manager

Prevents:

- overexposure
- correlated trades
- oversized positions

---

# Emergency Stop

API:

```text
/risk/emergency-stop
```

Purpose:

Immediate runtime halt.