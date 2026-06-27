from commander import NeuroLLaCommander


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

    commander.cycle()
    commander.audit()
    commander.adapt()


if __name__ == "__main__":
    main()