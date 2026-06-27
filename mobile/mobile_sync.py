import requests


class MobileSync:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def push_trade(self, trade_data):
        requests.post(
            self.endpoint,
            json=trade_data
        )