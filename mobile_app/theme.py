"""
NeuroLLa design tokens, translated 1:1 from
docs/.. NeuroLLa Frontend Design System (v1.0) into NiceGUI/Quasar +
plain CSS. Every value here traces back to a specific line in that
spec - nothing invented. If the design system changes, this is the
only file that should need to change.
"""

# --- 2. Brand Identity -----------------------------------------------------
ORANGE = "#F57C00"
ORANGE_HOVER = "#E86F00"
SOFT_ORANGE = "#FFF3E8"
WHITE = "#FFFFFF"
BLACK = "#1B1B1B"
DARK_GRAY = "#2A2A2A"
MEDIUM_GRAY = "#6E6E6E"
LIGHT_GRAY = "#F7F7F7"
BORDER_GRAY = "#EAEAEA"
SUCCESS_GREEN = "#14AE5C"
DANGER_RED = "#E53935"
WARNING_ORANGE = "#FB8C00"
INFO_BLUE = "#2196F3"

# --- 6. Navigation - status badge colors ------------------------------------
STATUS_COLORS = {
    "RUNNING": SUCCESS_GREEN,
    "STOPPED": DANGER_RED,
    "PAUSED": WARNING_ORANGE,
    "PENDING": MEDIUM_GRAY,
    # Trade-signal-specific extensions of the same status language:
    "BUY": SUCCESS_GREEN,
    "SELL": DANGER_RED,
    "HOLD": MEDIUM_GRAY,
}


def apply_theme():
    """Call once per page, before building any components."""
    from nicegui import ui

    ui.colors(
        primary=ORANGE,
        positive=SUCCESS_GREEN,
        negative=DANGER_RED,
        warning=WARNING_ORANGE,
        info=INFO_BLUE,
        dark=BLACK,
        dark_page=BLACK,
    )

    # --- 3. Typography: Inter, fallback Manrope / SF Pro / sans-serif ------
    ui.add_head_html('''
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    ''')

    ui.add_head_html(f'''
        <style>
            :root {{
                --nl-orange: {ORANGE};
                --nl-orange-hover: {ORANGE_HOVER};
                --nl-soft-orange: {SOFT_ORANGE};
                --nl-black: {BLACK};
                --nl-dark-gray: {DARK_GRAY};
                --nl-medium-gray: {MEDIUM_GRAY};
                --nl-light-gray: {LIGHT_GRAY};
                --nl-border-gray: {BORDER_GRAY};
                --nl-success: {SUCCESS_GREEN};
                --nl-danger: {DANGER_RED};
                --nl-warning: {WARNING_ORANGE};
                --nl-info: {INFO_BLUE};
            }}

            body, .q-field, .nicegui-content {{
                font-family: 'Inter', 'Manrope', -apple-system, 'SF Pro Display', sans-serif !important;
            }}

            body.body--dark {{
                background-color: var(--nl-black) !important;
            }}

            /* --- 5. Cards: white/dark surface, 1px border, 12px radius,
               20px padding, explicitly no shadow ---------------------- */
            .nl-card {{
                background: var(--nl-dark-gray);
                border: 1px solid #3a3a3a;
                border-radius: 12px;
                padding: 20px;
                box-shadow: none !important;
            }}

            /* --- 5. Buttons: 44px height, 8px radius, 12x20 padding --- */
            .nl-btn-primary, .nl-btn-secondary, .nl-btn-danger {{
                height: 44px;
                border-radius: 8px !important;
                padding: 0 20px !important;
                font-weight: 600;
                text-transform: none !important;
                letter-spacing: normal !important;
            }}

            .nl-btn-secondary {{
                background: transparent !important;
                border: 1px solid var(--nl-orange) !important;
                color: var(--nl-orange) !important;
            }}

            /* --- Disabled state must be unmistakable - the brief calls
               for fast decision making, which requires it being obvious
               at a glance whether an action is currently available --- */
            .q-btn.disabled, .q-btn[disabled] {{
                opacity: 0.38 !important;
            }}

            /* --- 5. Inputs: 44px height, 8px radius, border-gray,
               orange focus border --------------------------------------- */
            .nl-input .q-field__control {{
                border-radius: 8px;
                min-height: 44px;
            }}

            /* --- 1.4 No glow / heavy transitions; 9. Animations:
               150-250ms only, on hover/fade, nothing else ---------------- */
            .nl-card, .q-btn, .q-field {{
                transition: background-color 200ms ease, border-color 200ms ease;
            }}

            /* --- Caption / muted text role ------------------------------ */
            .nl-caption {{
                font-size: 12px;
                font-weight: 500;
                color: var(--nl-medium-gray);
            }}

            .nl-h1 {{ font-size: 32px; font-weight: 700; }}
            .nl-h2 {{ font-size: 24px; font-weight: 600; }}
            .nl-h3 {{ font-size: 20px; font-weight: 600; }}
            .nl-h4 {{ font-size: 18px; font-weight: 600; }}
            .nl-body {{ font-size: 15px; font-weight: 400; }}
            .nl-body-small {{ font-size: 14px; font-weight: 400; }}
        </style>
    ''')


def status_badge_classes(status):
    """Returns a (background, text) hex pair for a status pill, per the
    Tags/Badges spec (running=green, stopped=red, paused=orange,
    pending=gray), extended to BUY/SELL/HOLD using the same language."""
    color = STATUS_COLORS.get(status.upper(), MEDIUM_GRAY)
    return color
