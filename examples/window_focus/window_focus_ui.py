"""A window for judging the focus-detection strategies against each other.

Click into another app, alt-tab away, click your desktop, click back. The
banner says whether ui_elements thinks it still has focus, and the whole
window goes see-through while it thinks it does not.

Strategy and opacity are switched from the window rather than from settings so
you can flip between them without a reload and watch the difference.
"""

from talon import Context, actions, cron, settings

from ...src.window_focus import window_focus_manager

# Talon settings are read-only from Python; a Context override is how you move
# one at runtime. Here so the two pickers below can switch strategy and opacity
# without a settings file edit and a reload.
ctx = Context()

ACCENT = "3B82F6"
WINDOW_BG = "2D2D30"
BORDER = "454549"
TEXT_PRIMARY = "F0F0F0"
TEXT_SECONDARY = "A0A0A4"
FOCUSED_COLOR = "2E7D32"
BLURRED_COLOR = "B03A3A"

STRATEGIES = ["both", "canvas", "win_focus", "click", "all", "off"]
OPACITIES = [1.0, 0.75, 0.5, 0.25]

_poll_job = None
_blur_count = 0
_last_pushed = None


def _poll():
    """The library has no focus-changed callback for consumers yet, so the
    window asks. Only pushes state when something actually moved - setting it
    every tick would re-render the tree ten times a second for nothing."""
    global _blur_count, _last_pushed
    if not actions.user.ui_elements_is_active(window_focus_ui):
        # Something else took the tree down - "Go back", hide_all, escape.
        _stop_poll()
        return
    focused = window_focus_manager.is_focused
    was_focused = _last_pushed["focused"] if _last_pushed else focused
    if focused != was_focused and not focused:
        _blur_count += 1
    next_state = {
        "focused": focused,
        "blur_count": _blur_count,
        "strategy": settings.get("user.ui_elements_focus_strategy", "both"),
        "opacity": round(float(settings.get("user.ui_elements_unfocused_opacity", 1.0)), 2),
    }
    if next_state == _last_pushed:
        return
    _last_pushed = next_state
    actions.user.ui_elements_set_state(next_state)


def _set_strategy(value):
    ctx.settings["user.ui_elements_focus_strategy"] = value
    actions.user.ui_elements_set_state("strategy", value)


def _set_opacity(value):
    ctx.settings["user.ui_elements_unfocused_opacity"] = value
    actions.user.ui_elements_set_state("opacity", value)


def window_focus_ui():
    div, text, button, screen, state, window, style = actions.user.ui_elements(
        ["div", "text", "button", "screen", "state", "window", "style"]
    )

    focused = state.get("focused", True)
    blur_count = state.get("blur_count", 0)
    strategy = state.get("strategy", settings.get("user.ui_elements_focus_strategy", "both"))
    opacity = state.get("opacity", float(settings.get("user.ui_elements_unfocused_opacity", 1.0)))

    style({
        ".row": {"flex_direction": "row", "gap": 6, "flex_wrap": "wrap"},
        ".chip": {
            "padding": 8,
            "border_radius": 6,
            "border_width": 1,
            "border_color": BORDER,
            "font_size": 14,
        },
        ".chip_on": {
            "padding": 8,
            "border_radius": 6,
            "border_width": 1,
            "border_color": ACCENT,
            "background_color": ACCENT,
            "font_size": 14,
        },
        ".label": {"font_size": 13, "color": TEXT_SECONDARY},
    })

    def chip(label, value, current, on_pick):
        klass = "chip_on" if value == current else "chip"
        return button(str(label), class_name=klass, on_click=lambda: on_pick(value))

    return screen(justify_content="center", align_items="center")[
        window(title="Window focus", width=460, background_color=WINDOW_BG)[
            div(padding=20, gap=16)[
                div(
                    padding=12,
                    border_radius=8,
                    background_color=FOCUSED_COLOR if focused else BLURRED_COLOR,
                )[
                    text(
                        "FOCUSED" if focused else "NOT FOCUSED",
                        font_size=18,
                        font_weight="bold",
                        color=TEXT_PRIMARY,
                    ),
                ],
                div(gap=6)[
                    text("Detection strategy", class_name="label"),
                    div(class_name="row")[
                        *[chip(s, s, strategy, _set_strategy) for s in STRATEGIES]
                    ],
                ],
                div(gap=6)[
                    text("Unfocused opacity", class_name="label"),
                    div(class_name="row")[
                        *[chip(o, o, opacity, _set_opacity) for o in OPACITIES]
                    ],
                ],
                div(gap=4)[
                    text(f"Times blurred: {blur_count}", class_name="label"),
                    text(
                        "Click another app, alt-tab, or click the desktop. "
                        "Nothing should flicker while you click inside this window.",
                        class_name="label",
                    ),
                ],
                div(class_name="row")[
                    button("Focus debug to log", on_click=actions.user.ui_elements_focus_debug, class_name="chip"),
                    button("Close", on_click=hide_window_focus, class_name="chip"),
                ],
            ],
        ],
    ]


def show_window_focus():
    global _poll_job, _blur_count, _last_pushed
    _blur_count = 0
    _last_pushed = None
    actions.user.ui_elements_show(window_focus_ui)
    if not _poll_job:
        _poll_job = cron.interval("100ms", _poll)


def _stop_poll():
    global _poll_job
    if _poll_job:
        cron.cancel(_poll_job)
        _poll_job = None


def hide_window_focus():
    _stop_poll()
    actions.user.ui_elements_hide(window_focus_ui)
