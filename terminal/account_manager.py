import MetaTrader5 as mt5


class AccountManager:
    def __init__(self):
        mt5.initialize()

    def show(self):
        info = mt5.account_info()

        if info:
            print(info)

    def positions(self):
        positions = mt5.positions_get()

        if positions:
            for p in positions:
                print(p)