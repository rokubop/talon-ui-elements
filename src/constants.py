from typing import TypedDict

HIGHLIGHT_COLOR = "FFFFFF66"
CLICK_COLOR = "FFFFFF88"

class ElementEnumType(TypedDict):
    button: str
    div: str
    input_text: str
    screen: str
    text: str

ELEMENT_ENUM_TYPE: ElementEnumType = {
    "button": "button",
    "div": "div",
    "input_text": "input_text",
    "screen": "screen",
    "text": "text",
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
    ELEMENT_ENUM_TYPE["div"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["input_text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["screen"]: NODE_ENUM_TYPE["root"],
    ELEMENT_ENUM_TYPE["text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["button"]: NODE_ENUM_TYPE["leaf"],
}

LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION = "Use actions.user.ui_elements_show(...) instead, passing it a function that returns an element tree composed of `screen`, `div`, `text`, etc."
LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION = "Use actions.user.ui_elements_hide(...) or actions.user.ui_elements_hide_all() instead."