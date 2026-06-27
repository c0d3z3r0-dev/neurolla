import sys
from core.analytics import NeuroLLaAnalytics


def main():
    if len(sys.argv) < 2:
        print("Usage: python analytics.py <user_id>")
        sys.exit(1)

    user_id = int(sys.argv[1])
    analytics = NeuroLLaAnalytics(user_id=user_id)

    print("Total Trades:", analytics.total_trades())
    print("Open Trades:", len(analytics.open_trades()))
    print("Closed Trades:", len(analytics.closed_trades()))
    print("Win Rate:", analytics.win_rate())
    print("Pair Breakdown:", analytics.pair_breakdown())
    print(
        "Confidence Stats:",
        analytics.confidence_stats()
    )

    analytics.close()


if __name__ == "__main__":
    main()
