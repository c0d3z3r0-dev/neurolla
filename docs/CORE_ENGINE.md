# Core Engine Documentation

The Core Engine is the intelligence center of NeuroLLa.

It transforms raw market data into executable trading decisions.

---

# Core Pipeline

```text
Raw Market Data
↓
Feature Engineering
↓
Label Generation
↓
Sequence Builder
↓
Neural Model
↓
Regime Detection
↓
Strategy Selection
↓
Trade Quality Filter
↓
Risk Guard
↓
Broker Execution
```

---

# 1. Feature Engine

File:

```text
core/features.py
```

Purpose:

Transforms raw OHLC data into intelligence-ready features.

## Features

### EMA20

Short-term trend strength.

Formula:

EMA(price, 20)

---

### EMA50

Medium-term trend strength.

Formula:

EMA(price, 50)

---

### RSI

Momentum oscillator.

Used for:

- overbought detection
- oversold detection
- mean reversion triggers

Range:

0–100

Rules:

RSI < 30 → Oversold  
RSI > 70 → Overbought

---

### ATR

Average True Range.

Purpose:

Volatility measurement.

Used for:

- stop-loss placement
- take-profit placement
- label generation

Critical for adaptive exits.

---

### Returns

Percentage price movement.

Used for volatility profiling.

---

### Volatility

Rolling standard deviation of returns.

Used for:

- regime classification
- breakout detection
- risk weighting

---

# 2. Label Engine

File:

```text
train.py
```

Method:

Triple Barrier Labeling.

## Labels

0 = SELL  
1 = HOLD  
2 = BUY

Logic:

```text
Entry price
↓
ATR-based TP
↓
ATR-based SL
↓
Future horizon inspection
```

Rules:

If TP hit first → BUY  
If SL hit first → SELL  
Else → HOLD

This avoids naive future-return labels.

---

# 3. Sequence Engine

File:

```text
core/evaluator.py
```

Purpose:

Converts time-series data into neural sequences.

Structure:

```text
(sequence_length, features)
```

Default:

```text
50 x 6
```

Features:

- close
- ema20
- ema50
- rsi
- atr
- volatility

---

# Walk-forward normalization

Critical anti-leak mechanism.

Process:

```text
Fit scaler on historical window
↓
Transform same window
↓
Build sequence
```

This prevents future contamination.

---

# 4. Neural Model

File:

```text
train.py
```

Architecture:

LSTM

Input:

```text
50 x 6
```

Output:

```text
3 classes
```

Meaning:

SELL / HOLD / BUY

---

## Layers

LSTM → Dense

Default:

Input size = 6  
Hidden size = 64  
Output size = 3

---

# Why LSTM?

Because markets are temporal.

LSTM captures:

- sequence memory
- trend continuation
- momentum persistence
- reversal pressure

---

# 5. Adaptive Training

File:

```text
adaptive_train.py
```

Purpose:

Continuously improve from live trade outcomes.

Data source:

```text
Trade journal
```

Process:

```text
Collect new trades
↓
Append historical set
↓
Rebuild labels
↓
Retrain
↓
Deploy new weights
```

This makes NeuroLLa self-improving.

---

# 6. Commander Engine

File:

```text
commander.py
```

Main orchestrator.

Responsibilities:

- check news safety
- check risk guard
- scan market
- apply strategies
- filter quality
- route execution
- journal trades
- send notifications

Flow:

```text
Cycle Start
↓
News Filter
↓
Risk Guard
↓
Scanner
↓
Quality Filter
↓
Confluence
↓
Portfolio Approval
↓
Broker Execution
↓
Trade Journal
↓
Notifications
↓
Cycle End
```

---

# 7. Monte Carlo Validation

File:

```text
backtesting/monte_carlo.py
```

Purpose:

Stress-test profitability robustness.

Method:

Randomize trade order.

Measures:

- best case
- worst case
- average case

This exposes sequence fragility.

---

# Core Engine Principles

- No forward leakage
- Volatility-aware
- Risk-aware
- Strategy-adaptive
- Broker-agnostic
- Self-improving
- Persistent