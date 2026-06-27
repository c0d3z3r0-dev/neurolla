# Developer Guide

---

# Project Structure

core/
execution/
strategies/
server/
scheduler/
notifications/
backtesting/
terminal/

---

# Adding New Strategy

1. Create strategy file.
2. Implement evaluate(df).
3. Register in scanner.

---

# Adding New Broker

1. Create adapter.
2. Implement execute().
3. Register in BrokerRouter.

---

# Adding New Metrics

Add in:

```text
core/analytics.py
```

Expose in:

```text
server/routes/analytics.py
```

---

# Debugging

Use:

```bash
python terminal/dev_terminal.py
```