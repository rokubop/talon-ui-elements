from talon import actions
from dataclasses import dataclass
from ..constants import (
    ELEMENT_ENUM_TYPE,
    DEFAULT_DISABLED_OPACITY,
    DEFAULT_SWITCH_OFF_COLOR,
    DEFAULT_SWITCH_ON_COLOR,
    DEFAULT_SWITCH_SIZE,
    DEFAULT_SWITCH_THUMB_COLOR,
    DEFAULT_SWITCH_TRANSITION_MS,
)
from ..properties import validate_combined_props
from .component import Component

SWITCH_PROP_KEYS = {
    "checked", "on_change", "size", "color", "track_color",
    "thumb_color", "animated", "disabled",
}

def split_switch_props(props):
    switch_props = {}
    button_props = {}
    for key, value in props.items():
        if key in SWITCH_PROP_KEYS:
            switch_props[key] = value
        else:
            button_props[key] = value
    return switch_props, button_props

@dataclass
class SwitchEvent:
    checked: bool
    id: str = None

def switch_impl(props):
    switch_props, button_props = split_switch_props(props)
    div, button, state = actions.user.ui_elements(["div", "button", "state"])
    checked_prop = switch_props.get("checked", False)
    on_change = switch_props.get("on_change")
    is_checked, set_is_checked = state.use_local("switch", checked_prop)

    # Sync with controlled prop only when used as a controlled component.
    # Without on_change, checked_prop is just the initial value and must not
    # clobber local state on re-render.
    if on_change is not None and checked_prop != is_checked:
        set_is_checked(checked_prop)
        is_checked = checked_prop

    def on_trigger(e):
        new_checked = not is_checked
        set_is_checked(new_checked)
        if on_change is not None:
            on_change(
                SwitchEvent(checked=new_checked, id=button_props.get("id", None))
            )

    # size = track height in px. Width/thumb/padding scale proportionally
    # from a 22px-tall reference (40 wide, 16 thumb, 2 padding).
    size = int(switch_props.get("size", DEFAULT_SWITCH_SIZE))
    track_height = int(button_props.pop("height", size))
    track_width = int(button_props.pop("width", size * 40 / 22))
    thumb_size = int(button_props.pop("thumb_size", size * 16 / 22))
    padding = max(1, int(button_props.pop("padding", size * 2 / 22)))
    on_color = switch_props.get("color") or button_props.pop("background_color", None) or DEFAULT_SWITCH_ON_COLOR
    off_color = switch_props.get("track_color") or DEFAULT_SWITCH_OFF_COLOR
    track_color = on_color if is_checked else off_color
    thumb_color = switch_props.get("thumb_color") or DEFAULT_SWITCH_THUMB_COLOR
    border_radius = int(button_props.pop("border_radius", track_height // 2))
    animated = switch_props.get("animated", False)
    disabled = bool(switch_props.get("disabled"))

    thumb_transition = {"left": (DEFAULT_SWITCH_TRANSITION_MS, "ease_in_out")} if animated else None

    if animated:
        track_bg_transition = {"background_color": (DEFAULT_SWITCH_TRANSITION_MS, "ease_in_out")}
        return button(
            **button_props,
            disabled=disabled,
            opacity=DEFAULT_DISABLED_OPACITY if disabled else 1.0,
            width=track_width,
            height=track_height,
            background_color="00000000",
            border_radius=border_radius,
            position="relative",
            align_items="center",
            on_click=on_trigger,
            highlight_color="00000000",
            hint_style={"background_color": track_color},
        )[
            div(
                width=track_width,
                height=track_height,
                background_color=track_color,
                border_radius=border_radius,
                position="absolute",
                top=0,
                left=0,
                transition=track_bg_transition,
            ),
            div(
                width=thumb_size,
                height=thumb_size,
                background_color=thumb_color,
                border_radius=thumb_size // 2,
                position="absolute",
                top=(track_height - thumb_size) // 2,
                left=(track_width - thumb_size - padding) if is_checked else padding,
                transition=thumb_transition,
            )
        ]

    return button(
        **button_props,
        disabled=disabled,
        opacity=DEFAULT_DISABLED_OPACITY if disabled else 1.0,
        width=track_width,
        height=track_height,
        background_color=track_color,
        border_radius=border_radius,
        position="relative",
        align_items="center",
        on_click=on_trigger,
    )[
        div(
            width=thumb_size,
            height=thumb_size,
            background_color=thumb_color,
            border_radius=thumb_size // 2,
            position="absolute",
            top=(track_height - thumb_size) // 2,
            left=(track_width - thumb_size - padding) if is_checked else padding,
        )
    ]

def switch(props=None, **additional_props):
    properties = validate_combined_props(
        props,
        additional_props,
        ELEMENT_ENUM_TYPE["switch"]
    )
    if properties.get("on_click"):
        raise ValueError("switch does not support on_click, use on_change instead.")

    return Component(switch_impl, props=properties)