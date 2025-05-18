from talon import actions
from dataclasses import dataclass
from ..constants import (
    ELEMENT_ENUM_TYPE,
    DEFAULT_INTERACTIVE_BORDER_COLOR,
    DEFAULT_INTERACTIVE_BORDER_WIDTH,
    DEFAULT_INTERACTIVE_HIGHLIGHT_COLOR
)
from ..properties import validate_combined_props
from .component import Component

def split_switch_props(props):
    svg_props = {}
    button_props = {}
    switch_props = {}
    for key, value in props.items():
        if key in ["checked", "on_change"]:
            switch_props[key] = value
        elif key in ["size", "stroke_width", "background_color", "view_box", "stroke_linejoin", "stroke_linecap"]:
            svg_props[key] = value
        elif key in ["color", "stroke", "fill"]:
            if key == "color":
                svg_props["stroke"] = value
            button_props["highlight_color"] = value + "33"
            button_props[key] = value
        else:
            button_props[key] = value
    return svg_props, button_props, switch_props

@dataclass
class SwitchEvent:
    checked: bool
    id: str = None

default_button_props = {
    "border_width": DEFAULT_INTERACTIVE_BORDER_WIDTH,
    "border_color": DEFAULT_INTERACTIVE_BORDER_COLOR,
    "border_radius": 4,
    "highlight_color": DEFAULT_INTERACTIVE_HIGHLIGHT_COLOR,
}

default_svg_props = {
    "size": 20,
    "stroke_width": 2,
}

def switch_impl(props):
    svg_props, button_props, switch_props = split_switch_props(props)
    div, button, state = actions.user.ui_elements(["div", "button", "state"])
    is_checked, set_is_checked = state.use_local("switch", switch_props.get("checked", False))
    svg, polyline = actions.user.ui_elements_svg(["svg", "polyline"])

    def on_trigger(e):
        new_checked = not is_checked
        set_is_checked(new_checked)
        if switch_props.get("on_change"):
            switch_props["on_change"](
                SwitchEvent(checked=new_checked, id=button_props.get("id", None))
            )

    return button(
        {
            **default_button_props,
            **button_props,
        },
        on_click=on_trigger,
    )[
        svg({ **default_svg_props, **svg_props })[
            polyline(points="20 6 9 17 4 12")
        ] if is_checked else div(width=20, height=20)
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