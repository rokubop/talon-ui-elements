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
    get_unfocused_inert,
    get_unfocused_mask_color,
    get_unfocused_mask_scope,
    get_unfocused_mask_strength,
    get_unfocused_opacity,
    set_strategy,
    set_unfocused_inert,
    set_unfocused_mask_color,
    set_unfocused_mask_scope,
    set_unfocused_mask_strength,
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

STRATEGIES = ["poll", "both", "canvas", "win_focus", "click", "all", "off"]
# Tight steps near the top: a barely-there fade is the useful range, and 0.5
# was already far past it.
OPACITIES = [1.0, 0.97, 0.95, 0.92, 0.9, 0.85, 0.8, 0.75]
# "auto" takes the UI's own background colour.
MASKS = ["off", "auto", "000000", "2D2D30"]
# How far the mask pulls the colours toward it. 1.0 is a flat shape with no
# detail left; below that the text is still faintly there.
STRENGTHS = [0.15, 0.25, 0.4, 0.5, 0.75, 1.0]
SCOPES = ["all", "title_bar"]

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


def _pick_mask(value):
    set_unfocused_mask_color("" if value == "off" else value)
    actions.user.ui_elements_set_state("mask", value)


def _ensure_mask_on():
    """Scope and strength are inert without a colour, and picking one is always
    meant as "switch this on"."""
    if get_unfocused_mask_color():
        return
    set_unfocused_mask_color("auto")
    actions.user.ui_elements_set_state("mask", "auto")


def _pick_strength(value):
    set_unfocused_mask_strength(value)
    actions.user.ui_elements_set_state("strength", value)
    _ensure_mask_on()


def _pick_scope(value):
    set_unfocused_mask_scope(value)
    actions.user.ui_elements_set_state("scope", value)
    _ensure_mask_on()


def _effect_summary() -> str:
    """Exactly what will happen on blur, so nothing armed or unarmed is a
    surprise."""
    parts = []
    mask = get_unfocused_mask_color()
    if mask and get_unfocused_mask_strength() > 0:
        where = "whole window" if get_unfocused_mask_scope() == "all" else "title bar"
        parts.append(f"flatten {mask} at {get_unfocused_mask_strength()} over the {where}")
    opacity = get_unfocused_opacity()
    if opacity < 1.0:
        parts.append(f"fade to {opacity}")
    if get_unfocused_inert():
        parts.append("go inert")
    return ", ".join(parts) if parts else "nothing - pick a flatten color"


def _toggle_inert():
    value = not get_unfocused_inert()
    set_unfocused_inert(value)
    actions.user.ui_elements_set_state("inert", value)


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
    mask = state.get("mask", get_unfocused_mask_color() or "off")
    strength = state.get("strength", get_unfocused_mask_strength())
    scope = state.get("scope", get_unfocused_mask_scope())
    inert = state.get("inert", get_unfocused_inert())
    # Read live rather than from state: it is derived from all four pickers,
    # and any of them can move it.
    summary = _effect_summary()

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
                div(gap=6)[
                    text("Flatten to one color", class_name="label"),
                    div(class_name="row")[
                        *[chip(m, mask, _pick_mask) for m in MASKS]
                    ],
                ],
                div(gap=6)[
                    text("Flatten strength", class_name="label"),
                    div(class_name="row")[
                        *[chip(s, strength, _pick_strength) for s in STRENGTHS]
                    ],
                ],
                div(gap=6)[
                    text("Flatten covers", class_name="label"),
                    div(class_name="row")[
                        *[chip(s, scope, _pick_scope) for s in SCOPES]
                    ],
                ],
                div(
                    padding=10,
                    border_radius=6,
                    border_width=1,
                    border_color=BORDER,
                    gap=2,
                )[
                    text("On unfocus", class_name="label"),
                    text(summary, font_size=14, color=TEXT_PRIMARY),
                ],
                div(gap=4)[
                    text(f"Times blurred: {blur_count}", class_name="label"),
                    text(
                        "Click another app, alt-tab, or click the desktop. "
                        "Nothing should flicker while you click inside this window.",
                        class_name="label",
                    ),
                    text(
                        "Flatten color is the on switch - strength and scope do "
                        "nothing without it. These are runtime overrides and "
                        "reset when Talon reloads; the settings persist.",
                        class_name="label",
                    ),
                ],
                div(class_name="row")[
                    button(
                        f"Inert when unfocused: {'on' if inert else 'off'}",
                        on_click=_toggle_inert,
                        class_name="chip_on" if inert else "chip",
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
