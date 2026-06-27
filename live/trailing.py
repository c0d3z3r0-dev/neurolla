import MetaTrader5 as mt5


class TrailingStop:
    def __init__(
        self,
        trail_distance=0.0008
    ):
        self.trail_distance = trail_distance

    def update(
        self,
        position
    ):
        tick = mt5.symbol_info_tick(
            position.symbol
        )

        if position.type == mt5.ORDER_TYPE_BUY:
            new_sl = tick.bid - self.trail_distance

            if new_sl > position.sl:
                self.modify_sl(
                    position,
                    new_sl
                )

        elif position.type == mt5.ORDER_TYPE_SELL:
            new_sl = tick.ask + self.trail_distance

            if new_sl < position.sl:
                self.modify_sl(
                    position,
                    new_sl
                )

    def modify_sl(
        self,
        position,
        new_sl
    ):
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position.ticket,
            "sl": new_sl,
            "tp": position.tp
        }

        mt5.order_send(request)