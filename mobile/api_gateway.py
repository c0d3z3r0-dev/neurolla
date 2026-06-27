import os

from fastapi import FastAPI, HTTPException, Depends

from commander import NeuroLLaCommander
from scheduler.bot_runner import fetch_latest_bars
from core.features import build_features
from server.auth import require_user

app = FastAPI()

# NeuroLLaCommander requires broker/credentials, which aren't known at
# import time for a generic mobile gateway - it's built lazily per
# request instead of as a module-level singleton, which previously
# crashed this whole file on import.
_commander_cache = {}


def get_commander(user_id, broker="mt5"):
    if user_id not in _commander_cache:
        _commander_cache[user_id] = NeuroLLaCommander(
            broker=broker,
            credentials={},
            user_id=user_id
        )

    return _commander_cache[user_id]


@app.get("/signal/{symbol}")
def get_signal(symbol: str, user_id: int = Depends(require_user)):
    commander = get_commander(user_id)

    df = fetch_latest_bars("mt5", symbol)

    if df is None:
        raise HTTPException(status_code=503, detail="No market data available")

    df = build_features(df)

    ranked = commander.scanner.scan({symbol: df})

    for signal in ranked:
        if signal["symbol"] == symbol:
            return signal

    return {
        "status": "No signal"
    }
