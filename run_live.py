from live.trader import NeuroLLaTrader
from live.scanner import MultiPairScanner
from live.confluence import MultiTimeframeConfluence
from live.news_filter import NewsFilter


def main():
    news = NewsFilter()

    if not news.is_safe():
        print("News blackout active.")
        return

    scanner = MultiPairScanner()

    ranked = scanner.scan()

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

    trader = scanner.trader

    trader.place_trade(
        top["symbol"]
    )

    trader.shutdown()


if __name__ == "__main__":
    main()