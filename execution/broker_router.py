from execution.adapters.mt5_adapter import MT5Adapter
from execution.adapters.deriv_adapter import DerivAdapter
from execution.adapters.ctrader_adapter import CTraderAdapter
from execution.adapters.binance_adapter import BinanceAdapter
from execution.adapters.webhook_adapter import WebhookAdapter


class BrokerRouter:
    def __init__(self, broker, credentials):
        self.broker = broker

        self.adapters = {
            "mt5": MT5Adapter(credentials),
            "deriv": DerivAdapter(credentials),
            "ctrader": CTraderAdapter(credentials),
            "binance": BinanceAdapter(credentials),
            "webhook": WebhookAdapter(credentials)
        }

    def execute(self, signal_packet):
        adapter = self.adapters.get(self.broker)

        if not adapter:
            raise Exception(
                "Unsupported broker"
            )

        return adapter.execute(signal_packet)