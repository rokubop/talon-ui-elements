import platform
from typing import TypedDict, Union

IS_MAC = platform.system() == "Darwin"

# Platform-aware modifier and key constants
# On macOS, Cmd (reported as "super") is the primary modifier.
# On Windows/Linux, Ctrl (reported as "ctrl"/"control") is the primary modifier.
PRIMARY_MOD = "super" if IS_MAC else "ctrl"

KEY_ENTER = "enter"
KEY_RETURN = "return"
KEY_ESCAPE = "escape"
KEY_SPACE = "space"
KEY_BACKSPACE = "backspace"
KEY_DELETE = "delete"
KEY_TAB = "tab"
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_UP = "up"
KEY_DOWN = "down"
KEY_HOME = "home"
KEY_END = "end"

MODIFIER_KEYS = frozenset({
    "shift", "ctrl", "control", "alt", "win", "super",
    "capslock", "numlock", "scrolllock", "fn",
})

def parse_mods(mods: list) -> tuple:
    """Parse raw Talon e.mods into (shift, ctrl, alt) booleans.
    Maps the platform's primary modifier to ctrl."""
    lowered = [m.lower() for m in mods] if mods else []
    shift = "shift" in lowered
    ctrl = PRIMARY_MOD in lowered
    alt = "alt" in lowered
    return shift, ctrl, alt

# Don't make these a talon setting
# Shared UI's should be consistent from user to user
DEFAULT_COLOR = "FFFFFF"
DEFAULT_BORDER_COLOR = "555555"
DEFAULT_CHECKBOX_SIZE = 20.0
DEFAULT_SWITCH_SIZE = 22
DEFAULT_SWITCH_ON_COLOR = "2196F3"
DEFAULT_SWITCH_OFF_COLOR = "444444"
DEFAULT_SWITCH_THUMB_COLOR = "FFFFFF"
DEFAULT_SWITCH_TRANSITION_MS = 150
DEFAULT_DISABLED_OPACITY = 0.5
DEFAULT_FONT_SIZE = 16.0
DEFAULT_FLEX_DIRECTION = "column"
DEFAULT_ALIGN_ITEMS = "stretch"
DEFAULT_JUSTIFY_CONTENT = "flex_start"
DEFAULT_FOCUS_OUTLINE_COLOR = "FFFFFF"
DEFAULT_FOCUS_OUTLINE_WIDTH = 1.5
DEFAULT_INPUT_BACKGROUND_COLOR = "333333"
DEFAULT_INTERACTIVE_BORDER_COLOR = "888888"
DEFAULT_INTERACTIVE_BORDER_WIDTH = 1.0
DEFAULT_HIGHLIGHT_ALPHA = "33"
DEFAULT_INTERACTIVE_HIGHLIGHT_COLOR = "888888" + DEFAULT_HIGHLIGHT_ALPHA
DEFAULT_CURSOR_REFRESH_RATE = 16
DEFAULT_SCROLL_BAR_WIDTH = 10.0
DEFAULT_SCROLL_BAR_TRACK_COLOR = "FFFFFF22"
DEFAULT_SCROLL_BAR_THUMB_COLOR = "FFFFFF44"
DEFAULT_SCROLL_BAR_FADE_IN_MS = 150
DEFAULT_SCROLL_BAR_FADE_OUT_MS = 400
DEFAULT_SCROLL_BAR_IDLE_MS = 1200
DEFAULT_SCROLL_BUTTON_SIZE = 28.0
DEFAULT_SCROLL_BUTTON_INSET = 8.0
DEFAULT_SCROLL_BUTTON_BACKGROUND_COLOR = "222222CC"
DEFAULT_SCROLL_BUTTON_HOVER_BACKGROUND_COLOR = "333333EE"
DEFAULT_SCROLL_BUTTON_BORDER_COLOR = "666666"
DEFAULT_SCROLL_BUTTON_ICON_COLOR = "DDDDDD"
DEFAULT_LINK_COLOR = "#67A4FF"
DEFAULT_WINDOW_BACKGROUND_COLOR = "222222"
DEFAULT_ERROR_COLOR = "BD2F3E"
DEFAULT_ERROR_LINK_COLOR = "5F9FE3"
DEFAULT_DROP_SHADOW = (0, 20, 25, 25, "000000CC")
DEFAULT_HIGHLIGHT_DURATION_MS = 150
# DEFAULT_LINK_COLOR = "#589ADB"
DEFAULT_LINK_HOVER_COLOR = "#90C1F2"
DRAG_INIT_THRESHOLD = 4.0
RESIZE_EDGE_THRESHOLD = 6
RESIZE_GHOST_COLOR = "FFFFFF55"
RESIZE_GHOST_STROKE_WIDTH = 2.0
RESIZE_EDGE_HIGHLIGHT_COLOR = "FFFFFF44"
RESIZE_EDGE_HIGHLIGHT_WIDTH = 3.0

CASCADED_PROPERTIES = {
    "color",
    "focus_outline_color",
    "focus_outline_width",
    "font_family",
    "font_size",
    "highlight_color",
    "highlight_style",
    "opacity",
    "stroke_width",
    "stroke",
    "z_index",
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
    active_window: str
    button: str
    checkbox: str
    code: str
    cursor: str
    data_table: str
    div: str
    form: str
    icon: str
    input_text: str
    link: str
    select: str
    modal: str
    screen: str
    svg_circle: str
    svg_line: str
    svg_path: str
    svg_polygon: str
    svg_polyline: str
    svg_rect: str
    svg: str
    table: str
    td: str
    text: str
    textarea: str
    th: str
    tr: str
    window: str

ELEMENT_ENUM_TYPE: ElementEnumType = {
    "active_window": "active_window",
    "button": "button",
    "checkbox": "checkbox",
    "code": "code",
    "cursor": "cursor",
    "data_table": "data_table",
    "div": "div",
    "form": "form",
    "icon": "icon",
    "input_text": "input_text",
    "link": "link",
    "select": "select",
    "modal": "modal",
    "screen": "screen",
    "svg_circle": "svg_circle",
    "svg_line": "svg_line",
    "svg_path": "svg_path",
    "svg_polygon": "svg_polygon",
    "svg_polyline": "svg_polyline",
    "svg_rect": "svg_rect",
    "svg": "svg",
    "switch": "switch",
    "table": "table",
    "td": "td",
    "text": "text",
    "textarea": "textarea",
    "th": "th",
    "tr": "tr",
    "window": "window",
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
    ELEMENT_ENUM_TYPE["active_window"]: NODE_ENUM_TYPE["root"],
    ELEMENT_ENUM_TYPE["button"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["checkbox"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["code"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["cursor"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["data_table"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["div"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["form"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["link"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["icon"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["input_text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["select"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["modal"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["screen"]: NODE_ENUM_TYPE["root"],
    ELEMENT_ENUM_TYPE["svg_circle"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_line"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_path"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_polygon"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_polyline"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg_rect"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["svg"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["switch"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["table"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["td"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["text"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["textarea"]: NODE_ENUM_TYPE["leaf"],
    ELEMENT_ENUM_TYPE["th"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["tr"]: NODE_ENUM_TYPE["node"],
    ELEMENT_ENUM_TYPE["window"]: NODE_ENUM_TYPE["node"],
}

LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION = "Use actions.user.ui_elements_show(...) instead, passing it a function that returns an element tree composed of `screen`, `div`, `text`, etc."
LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION = "Use actions.user.ui_elements_hide(...) or actions.user.ui_elements_hide_all() instead."