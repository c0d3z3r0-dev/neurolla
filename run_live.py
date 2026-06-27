from live.trader import NeuroLLaTrader
from live.scanner import MultiPairScanner, DEFAULT_WATCHLIST
from live.confluence import MultiTimeframeConfluence
from live.news_filter import NewsFilter
from scheduler.bot_runner import fetch_watchlist_data


def main():
    news = NewsFilter()

    if not news.is_safe():
        print("News blackout active.")
        return

    market_data = fetch_watchlist_data("mt5", DEFAULT_WATCHLIST)

    if not market_data:
        print("No market data available.")
        return

    scanner = MultiPairScanner()

    ranked = scanner.scan(market_data)

    if len(ranked) == 0:
        print("No signals.")
        return

    top = ranked[0]

    confluence = MultiTimeframeConfluence()

    aligned, tf_data = confluence.confirm(
        top["symbol"]
    )

    if not aligned:
        print(
            "Timeframe misalignment."
        )
        return

    trader = NeuroLLaTrader()

    trader.place_trade(
        top["symbol"]
    )

    trader.shutdown()


if __name__ == "__main__":
    main()
