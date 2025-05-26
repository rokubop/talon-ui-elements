from talon import actions
from dataclasses import dataclass
from ..constants import (
    ELEMENT_ENUM_TYPE,
    DEFAULT_INTERACTIVE_BORDER_COLOR,
    DEFAULT_INTERACTIVE_BORDER_WIDTH,
    DEFAULT_INPUT_BACKGROUND_COLOR,
    DEFAULT_CHECKBOX_SIZE,
    DEFAULT_INTERACTIVE_HIGHLIGHT_COLOR
)
from ..properties import validate_combined_props
from .component import Component

def split_checkbox_props(props):
    svg_props = {}
    button_props = {}
    checkbox_props = {}
    for key, value in props.items():
        if key in ["checked", "on_change"]:
            checkbox_props[key] = value
        elif key in ["size", "stroke_width", "background_color", "view_box", "stroke_linejoin", "stroke_linecap"]:
            svg_props[key] = value
        elif key in ["color", "stroke", "fill"]:
            if key == "color":
                svg_props["stroke"] = value
            button_props["highlight_color"] = value + "33"
            button_props[key] = value
        else:
            button_props[key] = value
    return svg_props, button_props, checkbox_props

@dataclass
class CheckboxEvent:
    checked: bool
    id: str = None

default_button_props = {
    # "border_width": DEFAULT_INTERACTIVE_BORDER_WIDTH,
    # "border_color": DEFAULT_INTERACTIVE_BORDER_COLOR,
    # "border_radius": 4,
    "background_color": DEFAULT_INPUT_BACKGROUND_COLOR,
    "highlight_color": DEFAULT_INTERACTIVE_HIGHLIGHT_COLOR,
}

default_svg_props = {
    "size": DEFAULT_CHECKBOX_SIZE,
    "stroke_width": 3,
}

def checkbox_impl(props):
    svg_props, button_props, checkbox_props = split_checkbox_props(props)
    div, button, state = actions.user.ui_elements(["div", "button", "state"])
    is_checked, set_is_checked = state.use_local("checkbox", checkbox_props.get("checked", False))
    svg, polyline = actions.user.ui_elements_svg(["svg", "polyline"])

    def on_trigger(e):
        new_checked = not is_checked
        set_is_checked(new_checked)
        if checkbox_props.get("on_change"):
            checkbox_props["on_change"](
                CheckboxEvent(checked=new_checked, id=button_props.get("id", None))
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

def checkbox(props=None, **additional_props):
    properties = validate_combined_props(
        props,
        additional_props,
        ELEMENT_ENUM_TYPE["checkbox"]
    )
    if properties.get("on_click"):
        raise ValueError("checkbox does not support on_click, use on_change instead.")

    return Component(checkbox_impl, props=properties)