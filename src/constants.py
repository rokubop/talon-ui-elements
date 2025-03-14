from typing import TypedDict

# Don't make these a talon setting
# Shared UI's should be consistent from user to user
DEFAULT_COLOR = "FFFFFF"
DEFAULT_BORDER_COLOR = "555555"
DEFAULT_FONT_SIZE = 16
DEFAULT_FLEX_DIRECTION = "column"
DEFAULT_ALIGN_ITEMS = "stretch"
DEFAULT_JUSTIFY_CONTENT = "flex_start"
DEFAULT_FOCUS_OUTLINE_COLOR = "FFCC00"
DEFAULT_FOCUS_OUTLINE_WIDTH = 2
DRAG_INIT_THRESHOLD = 4

CASCADED_PROPERTIES = {
    "color",
    "font_size",
    "font_family",
    "opacity",
    "highlight_color",
    "focus_outline_color",
    "focus_outline_width",
}

NAMED_COLORS_TO_HEX = {
    "black": "000000",
    "white": "FFFFFF",
    "red": "e80725",
    "green": "0be056",
    "blue": "092fed",
    "yellow": "FFFF00",
    "cyan": "00FFFF",
    "gray": "808080",
    "silver": "C0C0C0",
    "lime": "00FF00",
    "purple": "#740af5",
    "teal": "008080",
    "navy": "000080",
    "orange": "f26c18",
    "pink": "f542dd",
    "brown": "A52A2A",
    "gold": "FFD700",
}

class ElementEnumType(TypedDict):
    button: str
    active_window: str
    div: str
    icon: str
    input_text: str
    screen: str
    text: str
    svg: str
    svg_path: str
    svg_rect: str
    svg_circle: str
    svg_polyline: str
    svg_polygon: str
    svg_line: str

ELEMENT_ENUM_TYPE: ElementEnumType = {
    "button": "button",
    "active_window": "active_window",
    "div": "div",
    "icon": "icon",
    "input_text": "input_text",
    "screen": "screen",
    "text": "text",
    "svg": "svg",
    "svg_path": "svg_path",
    "svg_rect": "svg_rect",
    "svg_circle": "svg_circle",
    "svg_polyline": "svg_polyline",
    "svg_polygon": "svg_polygon",
    "svg_line": "svg_line",
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
    ELEMENT_ENUM_TYPE["icon"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["input_text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["screen"]: NODE_ENUM_TYPE["root"],
    ELEMENT_ENUM_TYPE["text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["button"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["svg_path"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_rect"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_circle"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_polyline"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_line"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_polygon"]: NODE_ENUM_TYPE["leaf"],
}

LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION = "Use actions.user.ui_elements_show(...) instead, passing it a function that returns an element tree composed of `screen`, `div`, `text`, etc."
LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION = "Use actions.user.ui_elements_hide(...) or actions.user.ui_elements_hide_all() instead."