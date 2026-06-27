# NeuroLLa

NeuroLLa is an autonomous AI-powered multi-broker forex trading infrastructure built for live execution, adaptive learning, portfolio-level risk control, and SaaS deployment.

## Core Capabilities

- Multi-strategy execution
- Multi-broker support
- AI-driven signal generation
- Persistent autonomous bot sessions
- Real-time analytics
- Trade journaling
- Risk guard system
- Notifications
- SaaS backend
- Google authentication
- Mobile compatibility

## Supported Brokers

- MetaTrader 5
- Deriv
- cTrader
- Binance
- Webhook brokers

## Core Philosophy

NeuroLLa is not a single strategy bot.

It is a modular intelligence framework capable of selecting optimal execution behavior depending on market regime.

## Runtime Flow

Market Data
↓
Feature Engine
↓
Regime Detection
↓
Strategy Portfolio
↓
Quality Filter
↓
Risk Guard
↓
Broker Router
↓
Trade Execution
↓
Trade Journal
↓
Analytics
↓
Adaptive Retraining

## Main Components

core/
execution/
live/
strategies/
server/
scheduler/
notifications/
terminal/
backtesting/

## Startup

Train model:

```bash
python train.py
```

Run local bot:

```bash
python run_commander.py
```

Run SaaS API:

```bash
uvicorn server.main:app --reload
```

## Production Goal

NeuroLLa is designed to operate as:

- Retail autonomous trader
- Broker-agnostic signal infrastructure
- Multi-user trading SaaS
- Institutional strategy orchestration system