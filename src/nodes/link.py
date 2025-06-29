import webbrowser
from ..properties import (
    NodeTextProperties,
    combine_props,
    validate_props,
)
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_LINK_COLOR, DEFAULT_LINK_HOVER_COLOR
from .node_text import NodeText
from .node_button import NodeButton
from ..core.store import store
from ..core.state_manager import state_manager

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

    url = properties.get("url", "")
    print('close_on_click:', properties.get("close_on_click", None))

    def handle_click():
        if url:
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"Failed to open URL '{url}': {e}")
        else:
            print("No 'url' property provided for link")

        if properties.get("close_on_click"):
            if store.focused_tree:
                store.focused_tree.destroy()

        if properties.get("minimize_on_click"):
            if store.focused_tree:
                store.focused_tree.minimize()

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
            "on_click": handle_click
        })
        return NodeText(ELEMENT_ENUM_TYPE["link"], text, text_properties)

    if all_props.get("element_type", None):
        properties["element_type"] = all_props["element_type"]
    properties["on_click"] = handle_click

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