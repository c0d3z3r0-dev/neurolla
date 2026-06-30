"""
NeuroLLa Mobile - Deriv

A minimal, mobile-first web app for connecting to Deriv with an API
token and using NeuroLLaCore directly from a phone: get a live
signal, see the model's confidence, and place the trade on Deriv.

This is intentionally a single-user, no-login tool - it holds one
DerivSession in memory per browser tab and talks to Deriv directly.
It does not go through server/main.py's multi-user API, the
BrokerRouter placeholder adapters, or the bot scheduler - those are
for the multi-tenant SaaS path documented in
docs/FRONTEND_AND_BROKER_INTEGRATION.md. This app is for one person
(you) running the model from a phone, nothing more.

Run with:
    python -m mobile_app.main
Then open the printed URL on your phone (same Wi-Fi network, or use
--host 0.0.0.0 and your machine's LAN IP - see the bottom of this file).
"""

from nicegui import ui, run

from mobile_app.session import DerivSession, DEFAULT_SYMBOL
from core.config import MIN_CONFIDENCE

session = DerivSession()

SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"]


def notify_error(error):
    ui.notify(str(error), type="negative", multi_line=True, close_button=True)


@ui.page("/")
def main_page():
    # ui.colors / dark mode kept minimal and high-contrast for outdoor
    # phone-screen readability, per frontend-design guidance on
    # intentional, legible mobile UI rather than default dense web layouts.
    ui.dark_mode().enable()

    with ui.column().classes("w-full max-w-md mx-auto p-4 gap-4"):
        ui.label("NeuroLLa").classes("text-2xl font-bold")
        ui.label("Deriv mobile console").classes("text-sm text-gray-400 -mt-3")

        # --- Connection card ---
        with ui.card().classes("w-full"):
            connection_status = ui.label("Not connected").classes("text-sm")
            token_input = ui.input(
                "Deriv API token",
                password=True,
                password_toggle_button=True
            ).classes("w-full")

            with ui.row().classes("w-full gap-2"):
                connect_btn = ui.button("Connect").classes("flex-1")
                disconnect_btn = ui.button(
                    "Disconnect", color="red"
                ).classes("flex-1")
                disconnect_btn.disable()

        # --- Signal card ---
        with ui.card().classes("w-full") as signal_card:
            symbol_select = ui.select(
                SYMBOLS, value=DEFAULT_SYMBOL, label="Symbol"
            ).classes("w-full")

            get_signal_btn = ui.button(
                "Get signal", icon="insights"
            ).classes("w-full")
            get_signal_btn.disable()

            signal_label = ui.label("—").classes("text-3xl font-bold mt-2")
            confidence_label = ui.label("").classes("text-sm text-gray-400")
            details_label = ui.label("").classes(
                "text-xs text-gray-500 whitespace-pre-line"
            )

        # --- Trade card ---
        with ui.card().classes("w-full"):
            trade_btn = ui.button(
                "Place trade on Deriv", icon="bolt", color="green"
            ).classes("w-full")
            trade_btn.disable()

            trade_result_label = ui.label("").classes("text-sm mt-2")

            ui.label(
                f"Trades only allowed at confidence ≥ {MIN_CONFIDENCE:.0%} "
                f"(core.config.MIN_CONFIDENCE)."
            ).classes("text-xs text-gray-500")

    def refresh_connection_ui():
        if session.is_connected:
            connection_status.set_text("Connected to Deriv")
            connection_status.classes(replace="text-sm text-green-400")
            connect_btn.disable()
            disconnect_btn.enable()
            get_signal_btn.enable()
        else:
            connection_status.set_text("Not connected")
            connection_status.classes(replace="text-sm text-gray-400")
            connect_btn.enable()
            disconnect_btn.disable()
            get_signal_btn.disable()
            trade_btn.disable()

    async def on_connect():
        token = token_input.value.strip()

        if not token:
            ui.notify("Enter your Deriv API token first.", type="warning")
            return

        connect_btn.disable()
        connect_btn.props("loading")

        try:
            # DerivClient/DerivExecutor do blocking websocket I/O -
            # run them off the event loop so the page stays responsive
            # instead of freezing for the duration of the connection.
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
        ui.notify("Disconnected.")

    async def on_get_signal():
        get_signal_btn.disable()
        get_signal_btn.props("loading")
        trade_btn.disable()

        try:
            # Candle fetch (websocket I/O) and model inference (CPU
            # work) are both blocking - offload so the UI doesn't
            # freeze on a phone's typically slower connection.
            packet = await run.io_bound(
                session.get_signal, symbol_select.value
            )

            signal_label.set_text(packet["signal"])

            color = {
                "BUY": "text-green-400",
                "SELL": "text-red-400",
                "HOLD": "text-gray-400"
            }[packet["signal"]]
            signal_label.classes(replace=f"text-3xl font-bold mt-2 {color}")

            confidence_label.set_text(
                f"Confidence: {packet['confidence']:.1%}"
            )

            detail_lines = [f"Entry: {packet['entry']:.5f}"]
            if packet["sl"] is not None:
                detail_lines.append(f"SL: {packet['sl']:.5f}")
            if packet["tp"] is not None:
                detail_lines.append(f"TP: {packet['tp']:.5f}")
            details_label.set_text("\n".join(detail_lines))

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

        except Exception as error:
            notify_error(f"Trade failed: {error}")

        finally:
            trade_btn.props(remove="loading")
            # Require a fresh signal before allowing another trade,
            # rather than letting the same stale signal be re-sent
            # repeatedly with one tap each.
            trade_btn.disable()

    connect_btn.on_click(on_connect)
    disconnect_btn.on_click(on_disconnect)
    get_signal_btn.on_click(on_get_signal)
    trade_btn.on_click(on_place_trade)

    refresh_connection_ui()


ui.run(
    title="NeuroLLa Mobile",
    favicon="📈",
    # 0.0.0.0 so a phone on the same Wi-Fi network can reach this by
    # the host machine's LAN IP, e.g. http://192.168.1.50:8080
    host="0.0.0.0",
    port=8080,
    reload=False
)
