import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

from core.features import build_features
from core.inference import ModelInference
from core.risk import fractional_kelly
from core.journal import TradeJournal
from core.config import TP_MULT, SL_MULT, MIN_CONFIDENCE, MAX_DAILY_DRAWDOWN


class NeuroLLaTrader:
    """
    Single-symbol MT5 live trader driven directly by NeuroLLaCore.
    SL/TP are ATR-based using the same multipliers the model was
    trained against (core.config.TP_MULT / SL_MULT), so what the model
    was trained to predict matches what actually gets executed - fixed
    pip offsets unrelated to the labeling scheme would otherwise mean
    the model's "win" doesn't correspond to the trade's real outcome.
    """

    def __init__(self, user_id=1):
        if not mt5.initialize():
            raise Exception(
                f"MT5 init failed: {mt5.last_error()}"
            )

        self.user_id = user_id
        self.journal = TradeJournal()
        self.inference = ModelInference()

        self.daily_start_balance = self.get_balance()
        self.max_drawdown = MAX_DAILY_DRAWDOWN
        self.last_trade_time = None
        self.cooldown_minutes = 15

    def get_balance(self):
        account = mt5.account_info()
        return account.balance

    def check_drawdown(self):
        current_balance = self.get_balance()

        dd = (
            self.daily_start_balance -
            current_balance
        ) / self.daily_start_balance

        return dd < self.max_drawdown

    def spread_filter(
        self,
        symbol,
        max_spread=0.00025
    ):
        tick = mt5.symbol_info_tick(symbol)

        spread = tick.ask - tick.bid

        return spread <= max_spread

    def cooldown_active(self):
        if self.last_trade_time is None:
            return False

        return (
            datetime.now() -
            self.last_trade_time
        ) < timedelta(
            minutes=self.cooldown_minutes
        )

    def fetch_market_data(
        self,
        symbol="EURUSD",
        bars=300
    ):
        rates = mt5.copy_rates_from_pos(
            symbol,
            mt5.TIMEFRAME_M5,
            0,
            bars
        )

        df = pd.DataFrame(rates)

        df["time"] = pd.to_datetime(
            df["time"],
            unit="s"
        )

        df = df[
            [
                "time",
                "open",
                "high",
                "low",
                "close",
                "tick_volume"
            ]
        ]

        return df

    def infer_signal(self, symbol):
        df = self.fetch_market_data(symbol)
        df = build_features(df)

        label_index, label_name, confidence = self.inference.predict(df)

        # Return the latest ATR too, since place_trade needs it to
        # size SL/TP consistently with how the model was trained.
        latest_atr = df["atr"].iloc[-1]

        return label_index, confidence, latest_atr

    def place_trade(self, symbol="EURUSD"):
        if not self.check_drawdown():
            print("Daily drawdown exceeded.")
            return

        if self.cooldown_active():
            print("Cooldown active.")
            return

        if not self.spread_filter(symbol):
            print("Spread too high.")
            return

        prediction, confidence, atr = self.infer_signal(symbol)

        if confidence < MIN_CONFIDENCE:
            print("Confidence too low.")
            return

        tick = mt5.symbol_info_tick(symbol)

        if prediction == 0:
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
            sl = price + (atr * SL_MULT)
            tp = price - (atr * TP_MULT)

        elif prediction == 2:
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
            sl = price - (atr * SL_MULT)
            tp = price + (atr * TP_MULT)

        else:
            print("HOLD signal.")
            return

        kelly_fraction = fractional_kelly(
            confidence
        )

        balance = self.get_balance()

        risk_amount = balance * kelly_fraction

        volume = max(
            0.01,
            round(risk_amount / 1000, 2)
        )

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 9001,
            "comment": "NeuroLLa",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }

        result = mt5.order_send(request)

        direction = "BUY" if prediction == 2 else "SELL"

        self.journal.log_trade(
            self.user_id,
            {
                "symbol": symbol,
                "signal": direction,
                "confidence": confidence,
                "entry": price,
                "sl": sl,
                "tp": tp,
                "volume": volume
            }
        )

        self.last_trade_time = datetime.now()

        print("Trade placed:", result)

    def shutdown(self):
        self.journal.close()
        mt5.shutdown()
