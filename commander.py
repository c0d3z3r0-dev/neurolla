import os

from core.config import MIN_CONFIDENCE

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

from live.position_monitor import (
    PositionMonitor
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
            NeuroLLaAnalytics(user_id=user_id)
        )

        self.adaptive = (
            AdaptiveTrainer(user_id=None)
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

        self.position_monitor = PositionMonitor(
            self.portfolio
        )

        self.quality = TradeQuality()

        self.risk_guard = RiskGuard(
            user_id
        )

        self.notifier = (
            NeuroLLaNotifier(
                telegram_config={
                    "bot_token": os.environ.get(
                        "TELEGRAM_BOT_TOKEN", ""
                    ),
                    "chat_id": os.environ.get(
                        "TELEGRAM_CHAT_ID", ""
                    )
                }
            )
        )

    def cycle(
        self,
        market_data
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

        # Reconcile any trades that closed at the broker since the
        # last cycle, before deciding whether new symbols/clusters are
        # free to trade - otherwise a closed position's cluster would
        # stay blocked forever.
        self.position_monitor.reconcile()

        # Accept either a single dataframe (legacy single-symbol call)
        # or a {symbol: df} dict for genuine multi-pair scanning.
        if not isinstance(market_data, dict):
            symbol = self.scanner.watchlist[0]
            market_data = {symbol: market_data}

        ranked = self.scanner.scan(market_data)

        if len(ranked) == 0:
            print(
                "No opportunities found."
            )

            return

        for signal in ranked:
            symbol = signal["symbol"]
            prediction = signal[
                "prediction"
            ]

            df = market_data[symbol]

            quality_score = (
                self.quality.score(df)
            )

            if quality_score < 60:
                print(
                    f"{symbol} rejected: low quality"
                )
                continue

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

            # Use the model's own confidence (averaged across the
            # confirming timeframes) for position sizing, journaling,
            # and alerts - not a placeholder from the rule-based
            # scanner, which has no real confidence signal of its own.
            confidence = sum(
                tf["confidence"] for tf in tf_data.values()
            ) / len(tf_data)

            if confidence < MIN_CONFIDENCE:
                print(
                    f"{symbol} rejected: confidence {confidence:.2f} "
                    f"below minimum {MIN_CONFIDENCE}"
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