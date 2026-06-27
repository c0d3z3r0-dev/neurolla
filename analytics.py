from core.analytics import NeuroLLaAnalytics


def main():
    analytics = NeuroLLaAnalytics()

    print("Total Trades:", analytics.total_trades())
    print("Open Trades:", analytics.open_trades())
    print("Closed Trades:", analytics.closed_trades())
    print("Win Rate:", analytics.win_rate())
    print("Pair Breakdown:", analytics.pair_breakdown())
    print(
        "Confidence Stats:",
        analytics.confidence_stats()
    )


if __name__ == "__main__":
    main()