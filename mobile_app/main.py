"""
NeuroLLa Mobile - Deriv

A minimal, mobile-first web app for connecting to Deriv with an API
token and using NeuroLLaCore directly from a phone: get a live
signal, see the model's confidence, and place the trade on Deriv.

Restyled to the NeuroLLa Frontend Design System v1.0 (see
docs/FRONTEND_AND_BROKER_INTEGRATION.md for where this app fits, and
mobile_app/theme.py for the token translation). Structured as three
bottom-nav tabs mirroring the design system's mobile pattern:
Dashboard, Bots (signal + trade control), Trades.

This is intentionally a single-user, no-login tool - it holds one
DerivSession in memory per browser tab and talks to Deriv directly.
It does not go through server/main.py's multi-user API, the
BrokerRouter placeholder adapters, or the bot scheduler - those are
for the multi-tenant SaaS path documented in
docs/FRONTEND_AND_BROKER_INTEGRATION.md. This app is for one person
(you) running the model from a phone, nothing more.

Run with:
    python -m mobile_app.main
Then open the printed URL on your phone (same Wi-Fi network).
"""

from datetime import timezone

from nicegui import ui, run

from mobile_app.session import DerivSession, DEFAULT_SYMBOL
from mobile_app.theme import apply_theme, STATUS_COLORS
from core.config import MIN_CONFIDENCE

session = DerivSession()

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]


def notify_error(error):
    ui.notify(str(error), type="negative", multi_line=True, close_button=True)


def status_pill(text, status_key):
    """Small rounded label, colored per the design system's status
    language (Running=green, Stopped=red, Paused=orange, Pending=gray),
    used for both bot/connection state and BUY/SELL/HOLD signals."""
    color = STATUS_COLORS.get(status_key.upper(), STATUS_COLORS["PENDING"])
    return ui.label(text).classes("nl-body-small font-semibold px-3 py-1 rounded-full").style(
        f"background-color: {color}22; color: {color};"
    )


@ui.page("/")
def main_page():
    ui.dark_mode().enable()
    apply_theme()

    with ui.column().classes("w-full max-w-md mx-auto p-4 gap-4 pb-24"):
        # --- Header, matches the topbar's branding + identity role ----
        with ui.row().classes("w-full items-center justify-between"):
            with ui.row().classes("items-center gap-2"):
                ui.icon("bolt", color="orange").classes("text-2xl")
                ui.label("NeuroLLa").classes("nl-h3")
            connection_pill = status_pill("Not connected", "STOPPED")

        # ============================================================
        # TAB: Dashboard
        # ============================================================
        with ui.column().classes("w-full gap-4") as dashboard_tab:
            ui.label("Dashboard").classes("nl-h2")
            ui.label(
                "This app has no trade database of its own - figures "
                "below reflect only this session, not your full Deriv "
                "account history."
            ).classes("nl-caption")

            with ui.row().classes("w-full gap-3"):
                with ui.column().classes("nl-card flex-1 gap-1"):
                    ui.label("CONNECTION").classes("nl-caption")
                    dash_connection_label = ui.label("Offline").classes("nl-h4")

                with ui.column().classes("nl-card flex-1 gap-1"):
                    ui.label("SESSION TRADES").classes("nl-caption")
                    dash_trade_count_label = ui.label("0").classes("nl-h4")

            with ui.column().classes("nl-card w-full gap-1"):
                ui.label("LATEST SIGNAL").classes("nl-caption")
                dash_signal_label = ui.label("—").classes("nl-h1")
                dash_confidence_label = ui.label("No signal yet").classes(
                    "nl-body text-gray-400"
                )

            with ui.column().classes("nl-card w-full gap-2"):
                ui.label("MARKET SIGNAL").classes("nl-caption")
                dash_symbol_label = ui.label(DEFAULT_SYMBOL).classes("nl-h4")
                ui.label(
                    "Switch to the Bots tab to choose a symbol and "
                    "request a fresh signal."
                ).classes("nl-caption")

        # ============================================================
        # TAB: Bots (connect + get signal + trade)
        # ============================================================
        with ui.column().classes("w-full gap-4") as bots_tab:
            ui.label("Bot Control").classes("nl-h2")

            # --- Connection card --------------------------------------
            with ui.column().classes("nl-card w-full gap-3"):
                ui.label("BROKER").classes("nl-caption")
                with ui.row().classes("items-center gap-2"):
                    ui.label("Deriv").classes("nl-h4")
                    conn_status_pill = status_pill("Stopped", "STOPPED")

                token_input = ui.input(
                    "Deriv API token",
                    password=True,
                    password_toggle_button=True
                ).classes("nl-input w-full").props("outlined dense")

                with ui.row().classes("w-full gap-2"):
                    connect_btn = ui.button("Connect").classes(
                        "nl-btn-primary flex-1"
                    )
                    disconnect_btn = ui.button("Disconnect").classes(
                        "nl-btn-danger flex-1"
                    ).props("color=negative")
                    disconnect_btn.disable()

            # --- Strategy / signal card --------------------------------
            with ui.column().classes("nl-card w-full gap-3"):
                ui.label("STRATEGY").classes("nl-caption")
                with ui.row().classes("items-center gap-2"):
                    ui.label("NeuroLLaCore").classes("nl-h4")
                    ui.label("Mode: Manual").classes("nl-caption")

                symbol_select = ui.select(
                    SYMBOLS, value=DEFAULT_SYMBOL, label="Symbol"
                ).classes("nl-input w-full").props("outlined dense")

                get_signal_btn = ui.button(
                    "Get signal", icon="insights"
                ).classes("nl-btn-secondary w-full").props("outline color=primary")
                get_signal_btn.disable()

                signal_label = ui.label("—").classes("nl-h1")
                confidence_label = ui.label("").classes("nl-body text-gray-400")
                details_label = ui.label("").classes(
                    "nl-body-small text-gray-500 whitespace-pre-line"
                )

            # --- Trade controls -----------------------------------------
            with ui.column().classes("nl-card w-full gap-2"):
                ui.label("EXECUTE").classes("nl-caption")
                trade_btn = ui.button(
                    "Place trade on Deriv", icon="bolt"
                ).classes("nl-btn-primary w-full")
                trade_btn.disable()

                trade_result_label = ui.label("").classes("nl-body-small mt-1")

                ui.label(
                    f"Trades only allowed at confidence ≥ {MIN_CONFIDENCE:.0%} "
                    f"(core.config.MIN_CONFIDENCE)."
                ).classes("nl-caption")

        bots_tab.set_visibility(False)

        # ============================================================
        # TAB: Trades (this session's journal)
        # ============================================================
        with ui.column().classes("w-full gap-3") as trades_tab:
            ui.label("Trades").classes("nl-h2")
            ui.label("This session only - not Deriv's full history.").classes(
                "nl-caption"
            )

            trades_list_container = ui.column().classes("w-full gap-2")

            def render_trades():
                trades_list_container.clear()

                if not session.trade_log:
                    with trades_list_container:
                        with ui.column().classes("nl-card w-full items-center gap-1 py-8"):
                            ui.icon("receipt_long", color="grey").classes("text-3xl")
                            ui.label("No trades placed yet this session.").classes(
                                "nl-body-small text-gray-400"
                            )
                    return

                with trades_list_container:
                    for trade in session.trade_log:
                        with ui.row().classes(
                            "nl-card w-full items-center justify-between"
                        ):
                            with ui.column().classes("gap-0"):
                                with ui.row().classes("items-center gap-2"):
                                    ui.label(trade["symbol"]).classes("nl-h4")
                                    status_pill(trade["signal"], trade["signal"])
                                ui.label(
                                    trade["placed_at"]
                                    .astimezone(timezone.utc)
                                    .strftime("%H:%M:%S UTC")
                                ).classes("nl-caption")

                            with ui.column().classes("gap-0 items-end"):
                                ui.label(f"Entry {trade['entry']:.5f}").classes(
                                    "nl-body-small"
                                )
                                ui.label(
                                    f"Confidence {trade['confidence']:.0%}"
                                ).classes("nl-caption")

        trades_tab.set_visibility(False)

    # --- Bottom navigation, per design system section 8 (sidebar becomes
    # bottom nav below 768px) - this app is mobile-first so it's always
    # the bottom nav, never the desktop sidebar. -----------------------
    tabs = {"dashboard": dashboard_tab, "bots": bots_tab, "trades": trades_tab}

    def switch_tab(name):
        for key, tab in tabs.items():
            tab.set_visibility(key == name)

        for key, btn in nav_buttons.items():
            btn.classes(
                replace=(
                    "flex-1 flex flex-col items-center gap-0 py-1 "
                    + ("text-orange-500" if key == name else "text-gray-500")
                )
            )

        if name == "trades":
            render_trades()

        if name == "dashboard":
            refresh_dashboard()

    nav_buttons = {}

    with ui.row().classes(
        "fixed bottom-0 left-0 right-0 bg-[#1B1B1B] border-t border-[#3a3a3a] "
        "justify-around py-2 z-50"
    ):
        for key, icon, label in [
            ("dashboard", "dashboard", "Dashboard"),
            ("bots", "smart_toy", "Bots"),
            ("trades", "receipt_long", "Trades"),
        ]:
            with ui.column().classes(
                "flex-1 flex flex-col items-center gap-0 py-1 cursor-pointer"
            ).on("click", lambda _, k=key: switch_tab(k)) as nav_item:
                ui.icon(icon).classes("text-xl")
                ui.label(label).classes("text-xs")
            nav_buttons[key] = nav_item

    # --- shared refresh helpers --------------------------------------
    def refresh_connection_ui():
        if session.is_connected:
            connection_pill.set_text("Connected")
            conn_status_pill.set_text("Running")
            connect_btn.disable()
            disconnect_btn.enable()
            get_signal_btn.enable()
        else:
            connection_pill.set_text("Not connected")
            conn_status_pill.set_text("Stopped")
            connect_btn.enable()
            disconnect_btn.disable()
            get_signal_btn.disable()
            trade_btn.disable()

        refresh_dashboard()

    def refresh_dashboard():
        dash_connection_label.set_text(
            "Online" if session.is_connected else "Offline"
        )
        dash_trade_count_label.set_text(str(len(session.trade_log)))
        dash_symbol_label.set_text(symbol_select.value)

        if session.last_signal_packet:
            dash_signal_label.set_text(session.last_signal_packet["signal"])
            dash_confidence_label.set_text(
                f"Confidence: {session.last_confidence:.1%}"
            )
        else:
            dash_signal_label.set_text("—")
            dash_confidence_label.set_text("No signal yet")

    # --- event handlers (unchanged behavior from the previous version,
    # only the rendering calls below are new) --------------------------
    async def on_connect():
        token = token_input.value.strip()

        if not token:
            ui.notify("Enter your Deriv API token first.", type="warning")
            return

        connect_btn.disable()
        connect_btn.props("loading")

        try:
            await run.io_bound(session.connect, token)
            ui.notify("Connected to Deriv.", type="positive")

        except PermissionError as error:
            notify_error(f"Deriv rejected this token: {error}")

        except ConnectionError as error:
            notify_error(f"Could not reach Deriv: {error}")

        except Exception as error:
            notify_error(f"Unexpected error connecting: {error}")

        finally:
            connect_btn.props(remove="loading")
            refresh_connection_ui()

    def on_disconnect():
        session.disconnect()
        signal_label.set_text("—")
        confidence_label.set_text("")
        details_label.set_text("")
        trade_result_label.set_text("")
        refresh_connection_ui()
        render_trades()
        ui.notify("Disconnected.")

    async def on_get_signal():
        get_signal_btn.disable()
        get_signal_btn.props("loading")
        trade_btn.disable()

        try:
            packet = await run.io_bound(
                session.get_signal, symbol_select.value
            )

            signal_label.set_text(packet["signal"])

            color = STATUS_COLORS.get(packet["signal"], STATUS_COLORS["HOLD"])
            signal_label.style(f"color: {color};")

            confidence_label.set_text(
                f"Confidence: {packet['confidence']:.1%}"
            )

            detail_lines = [f"Entry: {packet['entry']:.5f}"]
            if packet["sl"] is not None:
                detail_lines.append(f"SL: {packet['sl']:.5f}")
            if packet["tp"] is not None:
                detail_lines.append(f"TP: {packet['tp']:.5f}")
            details_label.set_text("\n".join(detail_lines))

            refresh_dashboard()

            if session.can_trade():
                trade_btn.enable()
            else:
                trade_btn.disable()

                if packet["signal"] == "HOLD":
                    ui.notify("Model says HOLD - no trade to place.")
                else:
                    ui.notify(
                        f"Confidence {packet['confidence']:.1%} is below "
                        f"the {MIN_CONFIDENCE:.0%} minimum - trade blocked.",
                        type="warning"
                    )

        except RuntimeError as error:
            notify_error(error)

        except Exception as error:
            notify_error(f"Failed to get signal: {error}")

        finally:
            get_signal_btn.props(remove="loading")
            get_signal_btn.enable()

    async def on_place_trade():
        trade_btn.disable()
        trade_btn.props("loading")

        try:
            result = await run.io_bound(session.place_trade)
            trade_result_label.set_text(f"Result: {result}")
            ui.notify("Trade sent to Deriv.", type="positive")
            refresh_dashboard()

        except Exception as error:
            notify_error(f"Trade failed: {error}")

        finally:
            trade_btn.props(remove="loading")
            trade_btn.disable()

    connect_btn.on_click(on_connect)
    disconnect_btn.on_click(on_disconnect)
    get_signal_btn.on_click(on_get_signal)
    trade_btn.on_click(on_place_trade)

    refresh_connection_ui()
    switch_tab("dashboard")


ui.run(
    title="NeuroLLa Mobile",
    favicon="📈",
    host="0.0.0.0",
    port=8080,
    reload=False
)
