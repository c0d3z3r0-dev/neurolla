from backtesting.engine import NeuroLLaBacktester


def main():
    bt = NeuroLLaBacktester()

    bt.run(
        "data/raw/market.csv"
    )


if __name__ == "__main__":
    main()