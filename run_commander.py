from commander import NeuroLLaCommander
from scheduler.bot_runner import fetch_watchlist_data
from live.scanner import DEFAULT_WATCHLIST


def main():
    broker = input(
        "Broker (mt5/deriv/ctrader/binance/webhook): "
    )

    credentials = {}

    if broker == "deriv":
        credentials["api_token"] = input(
            "Deriv API Token: "
        )

    elif broker == "webhook":
        credentials["url"] = input(
            "Webhook URL: "
        )

    commander = NeuroLLaCommander(
        broker,
        credentials
    )

    market_data = fetch_watchlist_data(broker, DEFAULT_WATCHLIST)

    if not market_data:
        print(f"No market data available for broker '{broker}'.")
        return

    commander.cycle(market_data)
    commander.audit()
    commander.adapt()


if __name__ == "__main__":
    main()
