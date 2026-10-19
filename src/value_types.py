"""Value sets for user.ui_elements_types().

Validation reads justify_content, align_items, justify_self, align_self and
position from here; the other own sets only describe. Sets with a real table
(anchors, easings, ...) take values from it; tests/test_types.py keeps them in sync.
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
    "left": "The default.",
    "center": "",
    "right": "",
}

WHITE_SPACE = {
    "normal": "Wraps to the container's width.",
    "nowrap": "Stays on one line.",
}

FONT_STYLE = {
    "normal": "",
    "italic": "",
}

RESIZE_EDGE = {
    "top": "",
    "right": "",
    "bottom": "",
    "left": "",
}

SORT_DIRECTION = {
    "asc": "Smallest first. The default.",
    "desc": "Largest first.",
}

REGISTER_KIND = {
    "code_theme": "A color theme for code.",
    "code_language": "Highlighting rules for a language in code.",
}

# name: what the set is, its values, the props that take it
_OWN = {
    "flex_direction": {
        "desc": "Which way children are laid out. Column by default, unlike CSS.",
        "values": FLEX_DIRECTION,
        "props": ["flex_direction"],
    },
    "justify_content": {
        "desc": "Where children sit along the layout direction.",
        "values": JUSTIFY_CONTENT,
        "props": ["justify_content"],
    },
    "align_items": {
        "desc": "Where children sit across the layout direction.",
        "values": ALIGN_ITEMS,
        "props": ["align_items"],
    },
    "justify_self": {
        "desc": "On an absolute or fixed node with no left or right: where it sits across its parent. Ignored in flex layout.",
        "values": JUSTIFY_SELF,
        "props": ["justify_self"],
    },
    "align_self": {
        "desc": "Where this node sits across its parent's layout direction, over its parent's align_items. On an absolute or fixed node with no top or bottom: where it sits down its parent.",
        "values": ALIGN_SELF,
        "props": ["align_self"],
    },
    "position": {
        "desc": "How the node is placed.",
        "values": POSITION,
        "props": ["position"],
    },
    "overflow": {
        "desc": "What content past the node's edge does.",
        "values": OVERFLOW,
        "props": ["overflow", "overflow_x", "overflow_y"],
    },
    "scroll_bar": {
        "desc": "How a scrolling node shows its scroll bar.",
        "values": SCROLL_BAR,
        "props": ["scroll_bar"],
    },
    "text_align": {
        "desc": "How lines of text line up.",
        "values": TEXT_ALIGN,
        "props": ["text_align"],
    },
    "white_space": {
        "desc": "Whether text wraps.",
        "values": WHITE_SPACE,
        "props": ["white_space"],
    },
    "font_style": {
        "desc": "Upright or italic.",
        "values": FONT_STYLE,
        "props": ["font_style"],
    },
    "resize_edge": {
        "desc": "An edge resizable lets you drag. True is all four, and a list names several.",
        "values": RESIZE_EDGE,
        "props": ["resizable"],
    },
    "sort_direction": {
        "desc": "Which way a data_table sorts.",
        "values": SORT_DIRECTION,
        "props": ["sort_direction"],
    },
    "register_kind": {
        "desc": "What ui_elements_register adds.",
        "values": REGISTER_KIND,
    },
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
    "text": "",
    "code": "Syntax-highlighted code, with a theme and a language.",
    "input_text": "One-line text input.",
    "textarea": "Multi-line text input with wrapping and scrolling.",
    "select": "Dropdown to pick one of its options.",
    "icon": "A built-in icon, by name.",
    "button": "Clickable button.",
    "checkbox": "",
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
    "error_boundary": "Shows an error card for its subtree when rendering it raises, instead of blanking the tree.",
    "style": "Styles for every element of a kind, an id or a class_name.",
}

ANCHOR = {
    "top_left": "",
    "top": "",
    "top_right": "",
    "left": "",
    "center": "",
    "right": "",
    "bottom_left": "",
    "bottom": "",
    "bottom_right": "",
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
    "to_bottom": "The default.",
    "to_top": "",
    "to_right": "",
    "to_left": "",
    "to_bottom_right": "",
    "to_bottom_left": "",
    "to_top_right": "",
    "to_top_left": "",
}


def _tables() -> dict:
    """Imported here, not at the top: properties.py reads this module."""
    from .core.animations import EASING_FUNCTIONS
    from .elements import element_collection
    from .fonts import _WEIGHT_ORDER
    from .nodes.node_svg import linecap, linejoin
    from .properties import ANCHORS
    from .utils import GRADIENT_DIRECTIONS
    return {
        "element": {
            "desc": "An element ui_elements hands back by name.",
            "values": element_collection,
            "descs": ELEMENT,
        },
        "anchor": {
            "desc": "Puts the node's matching point on its parent's. Implies position absolute; replaces left, right, top and bottom.",
            "values": ANCHORS,
            "descs": ANCHOR,
            "props": ["anchor"],
        },
        "font_weight": {
            "desc": "How heavy the text is. Uses a real installed face when there is one, else synthesizes it. Also takes 100 to 900, and the names in aliases.",
            "values": _WEIGHT_ORDER,
            "descs": FONT_WEIGHT,
            "props": ["font_weight"],
            "accepts": r"[1-9]00",
        },
        "stroke_linecap": {
            "desc": "How an SVG stroke's open ends look.",
            "values": linecap,
            "descs": STROKE_LINECAP,
            "props": ["stroke_linecap"],
        },
        "stroke_linejoin": {
            "desc": "How an SVG stroke's corners look.",
            "values": linejoin,
            "descs": STROKE_LINEJOIN,
            "props": ["stroke_linejoin"],
        },
        "easing": {
            "desc": "How a transition paces itself.",
            "values": EASING_FUNCTIONS,
            "descs": EASING,
        },
        "gradient_direction": {
            "desc": "Which way a linear_gradient background runs. Also takes an angle, like 45deg.",
            "values": GRADIENT_DIRECTIONS,
            "descs": GRADIENT_DIRECTION,
            "accepts": r"-?\d+(\.\d+)?deg",
        },
    }


def _set(spec: dict) -> dict:
    descs = spec.get("descs", spec["values"])
    out = {
        "desc": spec["desc"],
        "values": [{"id": v, "desc": descs.get(v, "")} for v in spec["values"]],
    }
    for key in ("props", "accepts"):
        if key in spec:
            out[key] = spec[key]
    return out


def types() -> dict:
    """`accepts`: full-match regex for values beyond the list. `aliases`: other names font_weight takes."""
    out = {name: _set(spec) for name, spec in {**_OWN, **_tables()}.items()}
    from .fonts import _WEIGHT_ALIASES
    out["font_weight"]["aliases"] = {
        k: v for k, v in _WEIGHT_ALIASES.items() if k and not k.isdigit()
    }
    return out
