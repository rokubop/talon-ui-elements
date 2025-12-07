from talon import actions
from dataclasses import dataclass
from ..constants import (
    ELEMENT_ENUM_TYPE,
    DEFAULT_INTERACTIVE_BORDER_COLOR,
    DEFAULT_INTERACTIVE_BORDER_WIDTH,
    DEFAULT_INTERACTIVE_HIGHLIGHT_COLOR,
    scale_value
)
from ..properties import validate_combined_props
from .component import Component

def split_switch_props(props):
    switch_props = {}
    button_props = {}
    for key, value in props.items():
        if key in ["checked", "on_change", "size", "color"]:
            switch_props[key] = value
        else:
            button_props[key] = value
    return switch_props, button_props

@dataclass
class SwitchEvent:
    checked: bool
    id: str = None

default_button_props = {
    "border_width": int(scale_value(DEFAULT_INTERACTIVE_BORDER_WIDTH)),
    "border_color": DEFAULT_INTERACTIVE_BORDER_COLOR,
    "border_radius": int(scale_value(4.0)),
    "highlight_color": DEFAULT_INTERACTIVE_HIGHLIGHT_COLOR,
}

default_svg_props = {
    "size": int(scale_value(14.0)),
    "stroke_width": int(scale_value(2.0)),
}

def switch_impl(props):
    switch_props, button_props = split_switch_props(props)
    div, button, state = actions.user.ui_elements(["div", "button", "state"])
    is_checked, set_is_checked = state.use_local("switch", switch_props.get("checked", False))

    def on_trigger(e):
        new_checked = not is_checked
        set_is_checked(new_checked)
        if switch_props.get("on_change"):
            switch_props["on_change"](
                SwitchEvent(checked=new_checked, id=button_props.get("id", None))
            )

    # Extract styles from props
    size = int(switch_props.get("size", 14))  # Default size scaling factor is 14
    track_width = int(button_props.get("width", 40) * size / 14)
    track_height = int(button_props.get("height", 22) * size / 14)
    thumb_size = int(button_props.get("thumb_size", 16) * size / 14)
    padding = int(button_props.get("padding", 2) * size / 14)
    track_color = button_props.get("background_color", "#444444" if not is_checked else "#2196f3")
    thumb_color = button_props.get("thumb_color", "#ffffff")
    border_radius = int(button_props.get("border_radius", track_height // 2))

    return button(
        **button_props,
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