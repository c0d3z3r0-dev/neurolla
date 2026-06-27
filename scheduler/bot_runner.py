import time
import traceback

from commander import NeuroLLaCommander
from core.risk_guard import RiskGuard
from core.features import build_features
from live.mt5_connector import MT5Connector

POLL_INTERVAL_SECONDS = 300


def fetch_latest_bars(broker, symbol="EURUSD", bars=300):
    """
    Pulls the latest market data for whichever broker is configured.
    Only MT5 is wired up for now since it's the only data source the
    rest of the codebase implements; other brokers fall back to None
    and the cycle is skipped for that iteration rather than crashing.
    """
    if broker == "mt5":
        connector = MT5Connector()
        df = connector.fetch_data(symbol=symbol, bars=bars)
        connector.shutdown()
        return df

    return None


def run_bot(broker, credentials, user_id=1, symbol="EURUSD"):
    commander = NeuroLLaCommander(
        broker=broker,
        credentials=credentials,
        user_id=user_id
    )

    guard = RiskGuard(user_id=user_id)

    try:
        while True:
            if not guard.can_trade():
                print("RiskGuard blocked trading.")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            try:
                df = fetch_latest_bars(broker, symbol=symbol)

                if df is None:
                    print(f"No market data source wired up for broker '{broker}'.")
                else:
                    df = build_features(df)
                    commander.cycle(df)

            except Exception:
                # A single bad cycle should never kill the whole bot
                # process - log it and keep the loop alive.
                print("Error during trading cycle:")
                traceback.print_exc()

            time.sleep(POLL_INTERVAL_SECONDS)
    finally:
        guard.close()
