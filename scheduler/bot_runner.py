import time
import traceback

from commander import NeuroLLaCommander
from core.features import build_features
from live.mt5_connector import MT5Connector
from live.scanner import DEFAULT_WATCHLIST

POLL_INTERVAL_SECONDS = 300


def fetch_latest_bars(broker, symbol, bars=300):
    """
    Pulls the latest market data for whichever broker is configured.
    Only MT5 is wired up for now since it's the only data source the
    rest of the codebase implements; other brokers fall back to None
    and that symbol is skipped for this iteration rather than crashing.
    """
    if broker == "mt5":
        connector = MT5Connector()
        df = connector.fetch_data(symbol=symbol, bars=bars)
        connector.shutdown()
        return df

    return None


def fetch_watchlist_data(broker, watchlist):
    """
    Builds a {symbol: features_df} map for every symbol in the
    watchlist, skipping any symbol whose data couldn't be fetched.
    This is what MultiPairScanner.scan() expects for true multi-pair
    scanning, instead of always trading a single hardcoded symbol.
    """
    market_data = {}

    for symbol in watchlist:
        df = fetch_latest_bars(broker, symbol)

        if df is None:
            continue

        market_data[symbol] = build_features(df)

    return market_data


def run_bot(broker, credentials, user_id=1, watchlist=None):
    """
    Long-running poll loop. The RiskGuard.can_trade() check lives
    inside commander.cycle() itself - it isn't duplicated here, since
    constructing a second RiskGuard for the same user_id every
    iteration would mean two DB sessions running the identical daily
    PnL/trade-count query for no benefit.
    """
    watchlist = watchlist or DEFAULT_WATCHLIST

    commander = NeuroLLaCommander(
        broker=broker,
        credentials=credentials,
        user_id=user_id
    )

    try:
        while True:
            try:
                market_data = fetch_watchlist_data(broker, watchlist)

                if not market_data:
                    print(f"No market data available for broker '{broker}'.")
                else:
                    commander.cycle(market_data)

            except Exception:
                # A single bad cycle should never kill the whole bot
                # process - log it and keep the loop alive.
                print("Error during trading cycle:")
                traceback.print_exc()

            time.sleep(POLL_INTERVAL_SECONDS)
    finally:
        commander.shutdown()
