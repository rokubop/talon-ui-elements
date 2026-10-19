"""The sets of values ui_elements takes beyond what its actions' signatures
say, each value described. `user.ui_elements_types()` hands them out as
plain dicts. A param that takes one says so in its docstring:
`Type: ui_elements.<name>`.

A set the code keeps no table for is listed here. Validation reads
justify_content, align_items, justify_self, align_self and position from
here; the rest are the strings the code compares against, which only
these describe. A set with a table that does the work
(anchors, easings, weights, ...) takes its values from that table, and
only its descriptions live here: tests/test_types.py checks the two name
the same values.
"""

# ---------------------------------------------------------------------------
# Sets with no table of their own: these are the table
# ---------------------------------------------------------------------------

FLEX_DIRECTION = {
    "column": "Top to bottom.",
    "row": "Left to right.",
}

JUSTIFY_CONTENT = {
    "flex_start": "At the start.",
    "center": "In the middle.",
    "flex_end": "At the end.",
    "space_between": "Spread out, first and last at the edges.",
    "space_evenly": "Spread out, with even space around each.",
}

ALIGN_ITEMS = {
    "stretch": "Stretched to fill it.",
    "flex_start": "At the start.",
    "center": "In the middle.",
    "flex_end": "At the end.",
}

JUSTIFY_SELF = {
    "flex_start": "Left.",
    "center": "Middle.",
    "flex_end": "Right.",
}

ALIGN_SELF = {
    "flex_start": "Start, or top.",
    "center": "Middle.",
    "flex_end": "End, or bottom.",
    "stretch": "Stretched to fill it.",
}

POSITION = {
    "static": "In the layout, as usual. The default.",
    "relative": "In the layout, then moved by top, left, bottom and right.",
    "absolute": "Out of the layout, placed in its parent by top, left, bottom and right.",
    "fixed": "Out of the layout, placed on the screen by top, left, bottom and right.",
}

OVERFLOW = {
    "visible": "Shows past the edge.",
    "hidden": "Is cut off.",
    "scroll": "Is cut off, and scrolls.",
    "auto": "Is cut off, and scrolls; the same as scroll.",
}

SCROLL_BAR = {
    "overlay": "Floats over the content and hides when idle.",
    "visible": "Always shows, and takes space in the layout.",
}

TEXT_ALIGN = {
    "left": "Left. The default.",
    "center": "Centered.",
    "right": "Right.",
}

WHITE_SPACE = {
    "normal": "Wraps to the container's width.",
    "nowrap": "Stays on one line.",
}

FONT_STYLE = {
    "normal": "Upright.",
    "italic": "Slanted. A real italic face when there is one, else synthesized.",
}

RESIZE_EDGE = {
    "top": "Top edge.",
    "right": "Right edge.",
    "bottom": "Bottom edge.",
    "left": "Left edge.",
}

SORT_DIRECTION = {
    "asc": "Smallest first. The default.",
    "desc": "Largest first.",
}

REGISTER_KIND = {
    "code_theme": "A color theme for code.",
    "code_language": "Highlighting rules for a language in code.",
}

# name: (what the set is, its values, the props that take it)
_OWN = {
    "flex_direction": ("Which way children are laid out. Column by default, unlike CSS.",
                       FLEX_DIRECTION, ["flex_direction"]),
    "justify_content": ("Where children sit along the layout direction.",
                        JUSTIFY_CONTENT, ["justify_content"]),
    "align_items": ("Where children sit across the layout direction.",
                    ALIGN_ITEMS, ["align_items"]),
    "justify_self": ("On an absolute or fixed node with no left or right: where it "
                     "sits across its parent. Ignored in flex layout.",
                     JUSTIFY_SELF, ["justify_self"]),
    "align_self": ("Where this node sits across its parent's layout direction, over "
                   "its parent's align_items. On an absolute or fixed node with no top "
                   "or bottom: where it sits down its parent.",
                   ALIGN_SELF, ["align_self"]),
    "position": ("How the node is placed.", POSITION, ["position"]),
    "overflow": ("What content past the node's edge does.",
                 OVERFLOW, ["overflow", "overflow_x", "overflow_y"]),
    "scroll_bar": ("How a scrolling node shows its scroll bar.", SCROLL_BAR, ["scroll_bar"]),
    "text_align": ("How lines of text line up.", TEXT_ALIGN, ["text_align"]),
    "white_space": ("Whether text wraps.", WHITE_SPACE, ["white_space"]),
    "font_style": ("Upright or italic.", FONT_STYLE, ["font_style"]),
    "resize_edge": ("An edge resizable lets you drag. True is all four, and a list "
                    "names several.", RESIZE_EDGE, ["resizable"]),
    "sort_direction": ("Which way a data_table sorts.", SORT_DIRECTION, ["sort_direction"]),
    "register_kind": ("What ui_elements_register adds.", REGISTER_KIND, []),
}

# ---------------------------------------------------------------------------
# Sets kept by a table that does the work: descriptions only, by value
# ---------------------------------------------------------------------------

ELEMENT = {
    "screen": "Full-screen root; wraps everything.",
    "active_window": "Root the size of the active window; wraps everything.",
    "div": "Generic container.",
    "form": "Container that submits: Enter in an input_text, or a button with type 'submit'.",
    "window": "Draggable window with a title bar and close button; first inside screen.",
    "modal": "Dialog over a backdrop, opened and closed by its open prop.",
    "cursor": "Container that follows the mouse.",
    "text": "A run of text.",
    "code": "Syntax-highlighted code, with a theme and a language.",
    "input_text": "One-line text input.",
    "textarea": "Multi-line text input with wrapping and scrolling.",
    "select": "Dropdown to pick one of its options.",
    "icon": "A built-in icon, by name.",
    "button": "Clickable button.",
    "checkbox": "Checkbox, checked or not.",
    "switch": "On/off switch.",
    "link": "Clickable link to a url.",
    "data_table": "Sortable, searchable table of data, optionally multi-select.",
    "table": "Table container.",
    "tr": "Table row.",
    "th": "Table header cell.",
    "td": "Table data cell.",
    "svg": "SVG container.",
    "path": "SVG path, inside svg.",
    "rect": "SVG rectangle, inside svg.",
    "circle": "SVG circle, inside svg.",
    "line": "SVG line, inside svg.",
    "polyline": "SVG connected lines, open, inside svg.",
    "polygon": "SVG closed shape, inside svg.",
    "state": "Reactive state: get, set, use.",
    "effect": "Runs on mount, or when the state it names changes.",
    "ref": "A handle on an element, to read or change it directly.",
    "component": "A reusable piece of UI from a render function.",
    "error_boundary": "Shows an error card for its subtree when rendering it raises, "
                      "instead of blanking the tree.",
    "style": "Styles for every element of a kind, an id or a class_name.",
}

ANCHOR = {
    "top_left": "Top left corner.",
    "top": "Top edge, centered.",
    "top_right": "Top right corner.",
    "left": "Left edge, centered.",
    "center": "Center.",
    "right": "Right edge, centered.",
    "bottom_left": "Bottom left corner.",
    "bottom": "Bottom edge, centered.",
    "bottom_right": "Bottom right corner.",
}

FONT_WEIGHT = {
    "light": "Lightest; also 100 to 300.",
    "semilight": "Between light and regular.",
    "regular": "Regular; also normal and 400.",
    "medium": "500.",
    "semibold": "600.",
    "bold": "700 and 800.",
    "black": "Heaviest; 900.",
}

STROKE_LINECAP = {
    "butt": "Flat, at the end.",
    "round": "Rounded past the end.",
    "square": "Squared past the end.",
}

STROKE_LINEJOIN = {
    "miter": "Sharp.",
    "round": "Rounded.",
    "bevel": "Cut off.",
}

EASING = {
    "ease_out": "Starts fast and slows into the end. The default.",
    "ease_in": "Starts slow and speeds up.",
    "ease_in_out": "Slow at both ends.",
    "linear": "The same pace throughout.",
    "ease_in_cubic": "Starts slow and speeds up, sharper: a cubed curve.",
    "ease_out_bounce": "Bounces at the end.",
}

GRADIENT_DIRECTION = {
    "to_bottom": "Top to bottom. The default.",
    "to_top": "Bottom to top.",
    "to_right": "Left to right.",
    "to_left": "Right to left.",
    "to_bottom_right": "Top left to bottom right.",
    "to_bottom_left": "Top right to bottom left.",
    "to_top_right": "Bottom left to top right.",
    "to_top_left": "Bottom right to top left.",
}


def _tables() -> dict:
    """name: (what the set is, the table whose keys are its values, their
    descriptions, the props that take it). Imported here, not at the top,
    since properties.py reads this module."""
    from .core.animations import EASING_FUNCTIONS
    from .elements import element_collection
    from .fonts import _WEIGHT_ORDER
    from .nodes.node_svg import linecap, linejoin
    from .properties import ANCHORS
    from .utils import GRADIENT_DIRECTIONS
    return {
        "element": ("An element ui_elements hands back by name.",
                    element_collection, ELEMENT, []),
        "anchor": ("Puts the node's matching point on its parent's. Implies position "
                   "absolute; replaces left, right, top and bottom.",
                   ANCHORS, ANCHOR, ["anchor"]),
        "font_weight": ("How heavy the text is. Uses a real installed face when there "
                        "is one, else synthesizes it. Also takes 100 to 900, and the "
                        "names in aliases.",
                        _WEIGHT_ORDER, FONT_WEIGHT, ["font_weight"]),
        "stroke_linecap": ("How an SVG stroke's open ends look.",
                           linecap, STROKE_LINECAP, ["stroke_linecap"]),
        "stroke_linejoin": ("How an SVG stroke's corners look.",
                            linejoin, STROKE_LINEJOIN, ["stroke_linejoin"]),
        "easing": ("How a transition paces itself.",
                   EASING_FUNCTIONS, EASING, []),
        "gradient_direction": ("Which way a linear_gradient background runs. Also "
                               "takes an angle, like 45deg.",
                               GRADIENT_DIRECTIONS, GRADIENT_DIRECTION, []),
    }


# Open sets: anything matching is taken too
_PATTERNS = {
    "font_weight": r"[1-9]00",
    "gradient_direction": r"-?\d+(\.\d+)?deg",
}


def _set(desc: str, values, descs: dict, props: list) -> dict:
    out = {"desc": desc,
           "values": [{"id": v, "desc": descs.get(v, "")} for v in values]}
    if props:
        out["props"] = list(props)
    return out


def types() -> dict:
    """Every set, as `{name: {"desc", "values": [{"id", "desc"}], ...}}`.
    An open set adds `accepts`, a full-match regex; font_weight adds
    `aliases`, the other names it takes and what each stands for."""
    out = {name: _set(desc, values, values, props)
           for name, (desc, values, props) in _OWN.items()}
    for name, (desc, table, descs, props) in _tables().items():
        out[name] = _set(desc, table, descs, props)
    for name, pattern in _PATTERNS.items():
        out[name]["accepts"] = pattern
    from .fonts import _WEIGHT_ALIASES
    out["font_weight"]["aliases"] = {
        k: v for k, v in _WEIGHT_ALIASES.items() if k and not k.isdigit()}
    return out
