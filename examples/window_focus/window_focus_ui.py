"""A window for judging the focus-detection strategies against each other.

Click into another app, alt-tab away, click your desktop, click back. The
banner says whether ui_elements thinks it still has focus, and the whole
window goes see-through while it thinks it does not.

Strategy and opacity are picked from the window so you can flip between them
and watch the difference without a reload.
"""

from talon import actions, cron

from ...src.window_focus import (
    get_strategy,
    get_unfocused_opacity,
    set_strategy,
    set_unfocused_opacity,
    window_focus_manager,
)

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
_last_focused = None


def _poll():
    """Focus is the only thing here that changes behind the UI's back, so it is
    the only thing polled. The pickers own their own state - having the poll
    push those too would overwrite a value the moment after you clicked it."""
    global _blur_count, _last_focused
    if not actions.user.ui_elements_is_active(window_focus_ui):
        # Something else took the tree down - "Go back", hide_all, escape.
        _stop_poll()
        return
    focused = window_focus_manager.is_focused
    if focused == _last_focused:
        return
    if _last_focused is not None and not focused:
        _blur_count += 1
    _last_focused = focused
    actions.user.ui_elements_set_state({"focused": focused, "blur_count": _blur_count})


def _pick_strategy(value):
    set_strategy(value)
    actions.user.ui_elements_set_state("strategy", value)


def _pick_opacity(value):
    set_unfocused_opacity(value)
    actions.user.ui_elements_set_state("opacity", value)


def _force_unfocused():
    """Fade without waiting on detection. Splits "never detected" from
    "never rendered"."""
    actions.user.ui_elements_force_unfocused()
    actions.user.ui_elements_set_state("focused", False)


def _release_forced():
    global _last_focused
    actions.user.ui_elements_release_forced_focus()
    _last_focused = None


def window_focus_ui():
    div, text, button, screen, state, window, style = actions.user.ui_elements(
        ["div", "text", "button", "screen", "state", "window", "style"]
    )

    focused = state.get("focused", True)
    blur_count = state.get("blur_count", 0)
    strategy = state.get("strategy", get_strategy())
    opacity = state.get("opacity", get_unfocused_opacity())

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

    def chip(value, current, on_pick):
        klass = "chip_on" if value == current else "chip"
        return button(str(value), class_name=klass, on_click=lambda: on_pick(value))

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
                        *[chip(s, strategy, _pick_strategy) for s in STRATEGIES]
                    ],
                ],
                div(gap=6)[
                    text("Unfocused opacity", class_name="label"),
                    div(class_name="row")[
                        *[chip(o, opacity, _pick_opacity) for o in OPACITIES]
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
                    button("Force unfocused", on_click=_force_unfocused, class_name="chip"),
                    button("Release", on_click=_release_forced, class_name="chip"),
                    button("Debug to log", on_click=actions.user.ui_elements_focus_debug, class_name="chip"),
                    button("Close", on_click=hide_window_focus, class_name="chip"),
                ],
            ],
        ],
    ]


def _stop_poll():
    global _poll_job
    if _poll_job:
        cron.cancel(_poll_job)
        _poll_job = None


def show_window_focus():
    global _poll_job, _blur_count, _last_focused
    _blur_count = 0
    _last_focused = None
    actions.user.ui_elements_show(window_focus_ui)
    if not _poll_job:
        _poll_job = cron.interval("100ms", _poll)


def hide_window_focus():
    _stop_poll()
    actions.user.ui_elements_release_forced_focus()
    actions.user.ui_elements_hide(window_focus_ui)
