from ..properties import (
    NodeTextProperties,
    combine_props,
    validate_props,
)
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_LINK_COLOR, DEFAULT_LINK_HOVER_COLOR
from .node_text import NodeText
from .node_button import NodeButton

def link(*args, text=None, **additional_props):
    if args and isinstance(args[0], str):
        text = args[0]
        args = args[1:]

    props = args[0] if args and isinstance(args[0], dict) else {}

    all_props = combine_props(props, additional_props)

    properties = validate_props(
        all_props,
        ELEMENT_ENUM_TYPE["link"]
    )

    if text:
        properties["type"] = "link"
        text_properties = NodeTextProperties(**{
            "color": DEFAULT_LINK_COLOR,
            "highlight_style": {
                # "color": "#FF0000",
                # "stroke": "#FF0000",
                "color": DEFAULT_LINK_HOVER_COLOR,
            },
            **properties,
            "on_click": lambda: print("Link clicked!")
        })
        return NodeText(ELEMENT_ENUM_TYPE["link"], text, text_properties)

    if all_props.get("element_type", None):
        properties["element_type"] = all_props["element_type"]
    properties["on_click"] = lambda: print("Link clicked!")

    button_properties = NodeTextProperties(**{
        "highlight_style": {
            # "color": "#FF0000",
            # "stroke": "#FF0000",
            "color": DEFAULT_LINK_HOVER_COLOR,
        },
        **properties
    })
    button_properties.element_type = ELEMENT_ENUM_TYPE["link"]
    return NodeButton(button_properties)