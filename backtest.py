from core.db_init import init_db  # must be first - creates tables before any query

# Initialise all DB tables before importing anything that opens a session
init_db()
from backtesting.engine import NeuroLLaBacktester


def main():
    bt = NeuroLLaBacktester()

    bt.run(
        "data/raw/market.csv"
    )


if __name__ == "__main__":
    main()
