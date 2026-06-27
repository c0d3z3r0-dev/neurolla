# NeuroLLa Architecture

## High-Level Architecture

```text
User Layer
↓
Auth Layer
↓
Broker Registry
↓
Bot Runtime
↓
Commander Engine
↓
Strategy Layer
↓
Execution Layer
↓
Journal Layer
↓
Analytics Layer
↓
Risk Layer
↓
Notification Layer
```

## Core Modules

### commander.py

Main orchestration engine.

Responsibilities:

- Runs trading cycles
- Selects trades
- Applies filters
- Routes execution
- Logs trades

---

### core/

Contains:

- features
- analytics
- risk guard
- journal
- quality

---

### strategies/

Contains:

- trend following
- breakout
- mean reversion

---

### execution/

Contains:

- broker adapters
- broker router

---

### scheduler/

Handles persistent background bot sessions.

---

### server/

SaaS API layer.

---

### notifications/

Real-time alerting.

---

## Design Principles

- Broker agnostic
- Strategy modular
- Fail-safe
- Scalable
- Persistent
- Adaptive