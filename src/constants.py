from typing import TypedDict

# Don't make these a talon setting
# Shared UI's should be consistent from user to user
DEFAULT_COLOR = "FFFFFF"
DEFAULT_BORDER_COLOR = "555555"
DEFAULT_FONT_SIZE = 16
DEFAULT_FLEX_DIRECTION = "column"
DEFAULT_ALIGN_ITEMS = "stretch"
DEFAULT_JUSTIFY_CONTENT = "flex_start"

class ElementEnumType(TypedDict):
    button: str
    active_window: str
    div: str
    input_text: str
    screen: str
    text: str
    svg: str
    svg_path: str

ELEMENT_ENUM_TYPE: ElementEnumType = {
    "button": "button",
    "active_window": "active_window",
    "div": "div",
    "input_text": "input_text",
    "screen": "screen",
    "text": "text",
    "svg": "svg",
    "svg_path": "svg_path",
}

class NodeEnumType(TypedDict):
    leaf: str
    node: str
    root: str

NODE_ENUM_TYPE: NodeEnumType = {
    "leaf": "leaf",
    "node": "node",
    "root": "root",
}

NODE_TYPE_MAP = {
    ELEMENT_ENUM_TYPE["button"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["active_window"]: NODE_ENUM_TYPE["root"],
    ELEMENT_ENUM_TYPE["div"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["input_text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["screen"]: NODE_ENUM_TYPE["root"],
    ELEMENT_ENUM_TYPE["text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["button"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["svg_path"]: NODE_ENUM_TYPE["leaf"],
}

LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION = "Use actions.user.ui_elements_show(...) instead, passing it a function that returns an element tree composed of `screen`, `div`, `text`, etc."
LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION = "Use actions.user.ui_elements_hide(...) or actions.user.ui_elements_hide_all() instead."