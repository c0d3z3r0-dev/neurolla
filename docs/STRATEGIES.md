# Strategy Portfolio Documentation

NeuroLLa uses a multi-strategy execution model.

It does not depend on a single strategy.

Instead:

```text
Market Regime
↓
Strategy Selection
↓
Signal Execution
```

This increases robustness.

---

# Strategy Selection Logic

File:

```text
core/regime.py
```

Regimes:

- TREND
- RANGE
- VOLATILE

Mapping:

```text
TREND → Trend Following
RANGE → Mean Reversion
VOLATILE → Breakout
```

---

# 1. Trend Following Strategy

File:

```text
strategies/trend_following.py
```

Purpose:

Capture directional continuation.

Logic:

BUY:

EMA20 > EMA50

SELL:

EMA20 < EMA50

Best for:

- EURUSD
- GBPUSD
- Boom/Crash
- Volatility indices

Strengths:

- high trend persistence
- simple
- reliable

Weaknesses:

- poor in ranging markets

---

# 2. Mean Reversion Strategy

File:

```text
strategies/mean_reversion.py
```

Purpose:

Capture exhaustion reversals.

Logic:

BUY:

RSI < 30

SELL:

RSI > 70

Best for:

- Synthetic indices
- Sideways forex

Strengths:

- frequent entries
- good in low volatility

Weaknesses:

- dangerous in strong trends

---

# 3. Breakout Strategy

File:

```text
strategies/breakout.py
```

Purpose:

Capture volatility expansion.

Logic:

BUY:

Close >= 20-period high

SELL:

Close <= 20-period low

Best for:

- London open
- New York open
- News volatility

Strengths:

- explosive reward potential

Weaknesses:

- false breakouts

---

# Future Strategies

Planned:

- Liquidity Sweep
- Smart Money Concepts
- Session Scalping
- News Fade
- Order Block Reversal

---

# Strategy Philosophy

Diversification through logic diversity.

Instead of:

One model.

NeuroLLa uses:

Multiple tactical systems.