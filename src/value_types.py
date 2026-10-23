"""Value sets for user.ui_elements_types()."""

# ---------------------------------------------------------------------------
# Sets with no table of their own: these are the table
# ---------------------------------------------------------------------------

FLEX_DIRECTION = {
    "column": "Children stack top to bottom. Important: column is default in ui_elements unlike standard HTML.",
    "row": "Children sit side by side, left to right.",
}

JUSTIFY_CONTENT = {
    "flex_start": "",
    "center": "",
    "flex_end": "",
    "space_between": "",
    "space_evenly": "",
}

ALIGN_ITEMS = {
    "stretch": "",
    "flex_start": "",
    "center": "",
    "flex_end": "",
}

JUSTIFY_SELF = {
    "flex_start": "",
    "center": "",
    "flex_end": "",
}

ALIGN_SELF = {
    "flex_start": "",
    "center": "",
    "flex_end": "",
    "stretch": "",
}

POSITION = {
    "static": "Default element placement.",
    "relative": "Default element placement, then offset relative to itself using top, left, bottom, right. Absolute children place inside it.",
    "absolute": "Removed from normal layout flow and instead placed inside the nearest non-static ancestor using top, left, bottom, right.",
    "fixed": "Removed from normal layout flow and instead placed on the screen using top, left, bottom, right. Doesn't scroll.",
}

OVERFLOW = {
    "visible": "Content draws past the edge.",
    "hidden": "Content is clipped past edges with no scrolling.",
    "scroll": "Content is clipped past edges and scrollable.",
    "auto": "Same as scroll, unlike CSS.",
}

SCROLL_BAR = {
    "overlay": "Floats over content, hides when idle.",
    "visible": "Always shows, takes space.",
}

TEXT_ALIGN = {
    "left": "Default.",
    "center": "",
    "right": "",
}

WHITE_SPACE = {
    "normal": "Wraps.",
    "nowrap": "",
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
    "asc": "Default.",
    "desc": "",
}

REGISTER_KIND = {
    "code_theme": "A color theme for code.",
    "code_language": "Highlighting rules for a language in code.",
}

# name: what the set is, its values, the props that take it
_OWN = {
    "flex_direction": {
        "desc": "Which way children are laid out.",
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
        "desc": "Horizontal place in its parent, for an absolute or fixed node with no left or right. Ignored in flex layout.",
        "values": JUSTIFY_SELF,
        "props": ["justify_self"],
    },
    "align_self": {
        "desc": "Where this node sits across its parent's layout direction, overriding align_items. For an absolute or fixed node with no top or bottom: vertical place in its parent.",
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
        "desc": "An edge resizable lets you drag. True for all four, or a list.",
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
    "screen": "Full-screen root. Typically the first element.",
    "active_window": "Root element the size of the active window. Use instead of screen.",
    "div": "Generic container.",
    "form": "Container that submits: Enter in an input_text, or a button with type 'submit'.",
    "window": "Draggable window with a title bar and close button. Goes first inside screen.",
    "modal": "Dialog over a backdrop, opened and closed by its open prop.",
    "cursor": "Follows the mouse.",
    "text": "",
    "code": "Syntax-highlighted code, with a theme and a language.",
    "input_text": "Single-line input text box.",
    "textarea": "Multi-line input text box.",
    "select": "Single choice dropdown.",
    "icon": "A built-in icon, by name.",
    "button": "",
    "checkbox": "",
    "switch": "",
    "link": "Opens a url.",
    "data_table": "Sortable, searchable table of data, optionally multi-select.",
    "table": "",
    "tr": "Table row.",
    "th": "Table header cell.",
    "td": "Table data cell.",
    "svg": "",
    "path": "Used inside an svg element.",
    "rect": "Used inside an svg element.",
    "circle": "Used inside an svg element.",
    "line": "Used inside an svg element.",
    "polyline": "Open shape. Used inside an svg element.",
    "polygon": "Closed shape. Used inside an svg element.",
    "state": "Reactive state: get, set, use.",
    "effect": "Runs on mount, or when the state it names changes.",
    "ref": "A handle on an element, to read or change it directly.",
    "component": "Usually not necessary. Only use if you need state.use_local (multiple UIs each with their own local state) or scoped style.",
    "error_boundary": "Shows an error card when its subtree raises.",
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
    "light": "100 to 300",
    "semilight": "Between light and regular.",
    "regular": "Same as normal and 400.",
    "medium": "500",
    "semibold": "600",
    "bold": "700, 800",
    "black": "900",
}

STROKE_LINECAP = {
    "butt": "Flat at the end.",
    "round": "Rounded past the end.",
    "square": "Squared past the end.",
}

STROKE_LINEJOIN = {
    "miter": "Sharp.",
    "round": "Rounded.",
    "bevel": "Cut off.",
}

EASING = {
    "ease_out": "Default.",
    "ease_in": "",
    "ease_in_out": "",
    "linear": "",
    "ease_in_cubic": "Sharper ease_in.",
    "ease_out_bounce": "",
}

GRADIENT_DIRECTION = {
    "to_bottom": "Default.",
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
            "desc": "Element by name, e.g. div, button, screen.",
            "values": element_collection,
            "descs": ELEMENT,
        },
        "anchor": {
            "desc": "Pins the node's matching point to its parent's. Implies position absolute, in place of left, right, top and bottom.",
            "values": ANCHORS,
            "descs": ANCHOR,
            "props": ["anchor"],
        },
        "font_weight": {
            "desc": "Keyword or number, e.g. bold, light, 100, 700. Synthesized when no installed face matches.",
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
            "desc": "Which way a linear_gradient background runs: a direction, or an angle like 45deg.",
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
