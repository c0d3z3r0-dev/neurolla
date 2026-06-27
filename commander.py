from live.news_filter import NewsFilter
from live.confluence import (
    MultiTimeframeConfluence
)

from live.scanner import (
    MultiPairScanner
)

from core.portfolio import (
    PortfolioManager
)

from core.analytics import (
    NeuroLLaAnalytics
)

from adaptive_train import (
    AdaptiveTrainer
)

from execution.broker_router import (
    BrokerRouter
)

from core.journal import (
    TradeJournal
)

from core.quality import (
    TradeQuality
)

from core.risk_guard import (
    RiskGuard
)

from notifications.notifier import (
    NeuroLLaNotifier
)


class NeuroLLaCommander:
    def __init__(
        self,
        broker,
        credentials,
        user_id=1
    ):
        self.user_id = user_id

        self.news = NewsFilter()

        self.scanner = MultiPairScanner()

        self.confluence = (
            MultiTimeframeConfluence()
        )

        self.analytics = (
            NeuroLLaAnalytics()
        )

        self.adaptive = (
            AdaptiveTrainer()
        )

        self.router = BrokerRouter(
            broker,
            credentials
        )

        self.portfolio = (
            PortfolioManager(
                balance=1000
            )
        )

        self.journal = TradeJournal()

        self.quality = TradeQuality()

        self.risk_guard = RiskGuard(
            user_id
        )

        self.notifier = (
            NeuroLLaNotifier(
                telegram_config={
                    "bot_token":
                    "YOUR_TELEGRAM_BOT_TOKEN",
                    "chat_id":
                    "YOUR_CHAT_ID"
                }
            )
        )

    def cycle(
        self,
        df
    ):
        print(
            "=== NeuroLLa Commander ==="
        )

        if not self.news.is_safe():
            print(
                "News blackout active."
            )

            self.notifier.alert(
                "News blackout active."
            )

            return

        if not self.risk_guard.can_trade():
            print(
                "RiskGuard blocked trading."
            )

            return

        ranked = self.scanner.scan(df)

        if len(ranked) == 0:
            print(
                "No opportunities found."
            )

            return

        quality_score = (
            self.quality.score(df)
        )

        if quality_score < 60:
            print(
                "Trade rejected: low quality"
            )

            return

        for signal in ranked:
            symbol = signal["symbol"]
            prediction = signal[
                "prediction"
            ]
            confidence = signal[
                "confidence"
            ]

            direction = None

            if prediction == 2:
                direction = "BUY"

            elif prediction == 0:
                direction = "SELL"

            else:
                continue

            aligned, tf_data = (
                self.confluence.confirm(
                    symbol
                )
            )

            if not aligned:
                print(
                    f"{symbol} rejected: timeframe misalignment"
                )
                continue

            approved, capital = (
                self.portfolio.approve_trade(
                    symbol,
                    direction,
                    confidence
                )
            )

            if not approved:
                print(
                    f"{symbol} rejected: portfolio conflict"
                )
                continue

            entry_price = df[
                "close"
            ].iloc[-1]

            atr_value = df[
                "atr"
            ].iloc[-1]

            signal_packet = {
                "symbol": symbol,
                "signal": direction,
                "confidence": confidence,
                "capital": capital,
                "entry": entry_price,
                "atr": atr_value
            }

            result = (
                self.router.execute(
                    signal_packet
                )
            )

            self.journal.log_trade(
                user_id=self.user_id,
                signal_packet={
                    **signal_packet,
                    "tp": result["tp"],
                    "sl": result["sl"]
                }
            )

            self.notifier.alert(
                f"Trade executed: "
                f"{symbol} "
                f"{direction} "
                f"Confidence={confidence}"
            )

            print(
                f"{symbol} executed:",
                result
            )

        print(
            "Cycle complete."
        )

    def audit(self):
        print(
            "=== Performance Audit ==="
        )

        print(
            "Total Trades:",
            self.analytics.total_trades()
        )

        print(
            "Win Rate:",
            self.analytics.win_rate()
        )

        print(
            "Total PnL:",
            self.analytics.total_pnl()
        )

        print(
            "Profit Factor:",
            self.analytics.profit_factor()
        )

        print(
            "Sharpe Ratio:",
            self.analytics.sharpe_ratio()
        )

        print(
            "Max Drawdown:",
            self.analytics.max_drawdown()
        )

    def adapt(self):
        print(
            "=== Adaptive Check ==="
        )

        self.adaptive.run()