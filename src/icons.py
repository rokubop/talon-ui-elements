from talon import actions
from .constants import ELEMENT_ENUM_TYPE
from .properties import validate_combined_props

# Use for references:
# https://iconsvg.xyz/
# https://lucide.dev/icons
ICON_SVG_PATH_ONLY = {
    "arrow_down": "M12 5v13M5 12l7 7 7-7",
    "arrow_left": "M19 12H6M12 5l-7 7 7 7",
    "arrow_right": "M5 12h13M12 5l7 7-7 7",
    "arrow_up": "M12 19V6M5 12l7-7 7 7",
    "chevron_down": "M 6 9 L 12 15 L 18 9",
    "chevron_left": "M 15 6 L 9 12 L 15 18",
    "chevron_right": "M 9 6 L 15 12 L 9 18",
    "chevron_up": "M 6 15 L 12 9 L 18 15",
    "close": "M 6 6 L 18 18 M 18 6 L 6 18",
    "delta": "M3 20h18L12 4z",
    "diamond": "M12 2 L22 12 L12 22 L2 12 Z",
    "download": "M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 9l-5 5-5-5M12 12.8V2.5",
    "edit": "M 16 3 L 21 8 L 8 21 L 3 21 L 3 16 L 16 3",
    "external_link": "M18 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8c0-1.1.9-2 2-2h5M15 3h6v6M10 14L20.2 3.8",
    "file": ["M13 2H6a2 2 0 0 0-2 2v16c0 1.1.9 2 2 2h12a2 2 0 0 0 2-2V9l-7-7z", "M13 3v6h6"],
    "file_text": ["M14 2H6a2 2 0 0 0-2 2v16c0 1.1.9 2 2 2h12a2 2 0 0 0 2-2V8l-6-6z", "M14 3v5h5M16 13H8M16 17H8M10 9H8"],
    "folder": "M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z",
    "menu": "M 3 6 H 18 M 3 12 H 18 M 3 18 H 18",
    "mic": ["M12 2c-1.7 0-3 1.2-3 2.6v6.8c0 1.4 1.3 2.6 3 2.6s3-1.2 3-2.6V4.6C15 3.2 13.7 2 12 2z", "M19 10v1a7 7 0 0 1-14 0v-1M12 18.4v3.3M8 22h8"],
    "maximize": "M 5 5 H 19 V 19 H 5 Z",
    "minimize": "M 4 14 H 19",
    "multiply": "M 6 18 L 18 6 M 6 6 L 18 18",
    "plus": "M 12 5 V 19 M 5 12 H 19",
    "rotate_left": "M2.5 2v6h6M2.66 15.57a10 10 0 1 0 .57-8.38",
    "upload": "M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 8l-5-5-5 5M12 4.2v10.3",
    "shrink": "M4 14h6v6M3 21l6.1-6.1M20 10h-6V4M21 3l-6.1 6.1",
    "stop": "M6 6h12v12H6z",
}

svg_only_props = [
    "stroke",
    "stroke_width",
    "stroke_linecap",
    "stroke_linejoin",
    "fill",
    "size",
    "width",
    "height",
    "rx",
    "ry",
    "d",
    "view_box",
]

def parse_icon_properties(props, **additional_props):
    div_props = {}
    svg_props = {
        **(props or {}),
        **additional_props
    }

    for prop in list(svg_props):
        if prop == "color":
            svg_props["stroke"] = svg_props["color"]
            del svg_props["color"]
            continue

        if prop not in svg_only_props:
            div_props[prop] = svg_props[prop]
            del svg_props[prop]

    return div_props, svg_props

def icon_testing(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, path = actions.user.ui_elements_svg(["svg", "path"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(stroke_linejoin="round", stroke_linecap="round", **svg_props)[
            path(d="m15 15 6 6m-6-6v4.8m0-4.8h4.8"),
            path(d="M9 19.8V15m0 0H4.2M9 15l-6 6"),
            path(d="M15 4.2V9m0 0h4.8M15 9l6-6"),
            path(d="M9 4.2V9m0 0H4.2M9 9 3 3"),
        ]
    ]

def icon_testing2(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, path = actions.user.ui_elements_svg(["svg", "path"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(stroke_linejoin="round", stroke_linecap="round", **svg_props)[
            path(d="M21 21l-6-6m6 6v-4.8m0 4.8h-4.8"),
            path(d="M3 16.2V21m0 0h4.8M3 21l6-6"),
            path(d="M21 7.8V3m0 0h-4.8M21 3l-6 6"),
            path(d="M3 7.8V3m0 0h4.8M3 3l6 6"),
        ]
    ]

def icon_home(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, path = actions.user.ui_elements_svg(["svg", "path"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            path(d="M20 9v11a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9"),
            path(d="M9 22V12h6v10M2 10.6L12 2l10 8.6")
        ]
    ]

def icon_clock(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, circle, path = actions.user.ui_elements_svg(["svg", "circle", "path"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            circle(cx=12, cy=12, r=10),
            path(d="M12 6v6l4 2"),
        ]
    ]

def icon_copy(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, rect, path = actions.user.ui_elements_svg(["svg", "rect", "path"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            rect(x=2, y=7, width=12, height=12, rx=2, ry=2),
            path(d="M6 4.75V3.75a2.5 2.5 0 0 1 2.5-2.5h8a2.5 2.5 0 0 1 2.5 2.5v9a2 2 0 0 1-2 2h-1"),
        ]
    ]

def icon_trash(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, path, polyline, line = actions.user.ui_elements_svg(["svg", "path", "polyline", "line"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            polyline(points="3 6 5 6 21 6"),
            path(d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"),
            line(x1=10, y1=11, x2=10, y2=17),
            line(x1=14, y1=11, x2=14, y2=17),
        ]
    ]

def icon_settings(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, circle, path = actions.user.ui_elements_svg(["svg", "circle", "path"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            circle(cx=12, cy=12, r=3),
            path(d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"),
        ]
    ]

def icon_play(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, polygon = actions.user.ui_elements_svg(["svg", "polygon"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            polygon(points="5 3 19 12 5 21 5 3", fill=True),
        ]
    ]

def icon_pause(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, rect = actions.user.ui_elements_svg(["svg", "rect"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            rect(x=6, y=4, width=4, height=16, fill=True),
            rect(x=14, y=4, width=4, height=16, fill=True),
        ]
    ]

def icon_check(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, polyline = actions.user.ui_elements_svg(["svg", "polyline"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            polyline(points="20 6 9 17 4 12")
        ]
    ]

def icon_plus(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, line = actions.user.ui_elements_svg(["svg", "line"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            line(x1=12, y1=5, x2=12, y2=19),
            line(x1=5, y1=12, x2=19, y2=12),
        ]
    ]

def icon_minus(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, line = actions.user.ui_elements_svg(["svg", "line"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            line(x1=5, y1=12, x2=19, y2=12),
        ]
    ]

def more_horizontal(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, circle = actions.user.ui_elements_svg(["svg", "circle"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            circle(cx=12, cy=12, r=1),
            circle(cx=19, cy=12, r=1),
            circle(cx=5, cy=12, r=1),
        ]
    ]

def more_vertical(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, circle = actions.user.ui_elements_svg(["svg", "circle"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            circle(cx=12, cy=12, r=1),
            circle(cx=12, cy=19, r=1),
            circle(cx=12, cy=5, r=1),
        ]
    ]

def icon_star(props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, polygon = actions.user.ui_elements_svg(["svg", "polygon"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    return div(**div_props)[
        svg(**svg_props)[
            polygon(points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2")
        ]
    ]

ICON_CUSTOM_SVG = {
    "check": icon_check,
    "clock": icon_clock,
    "copy": icon_copy,
    "home": icon_home,
    "minus": icon_minus,
    "more_horizontal": more_horizontal,
    "more_vertical": more_vertical,
    "pause": icon_pause,
    "play": icon_play,
    "plus": icon_plus,
    "trash": icon_trash,
    "settings": icon_settings,
    "star": icon_star,
    "testing": icon_testing,
    "testing2": icon_testing2,
}

VALID_ICON_NAMES = list(ICON_SVG_PATH_ONLY.keys() | ICON_CUSTOM_SVG.keys())

def icon_svg_single_path_stroke(name: str, props=None, **additional_props):
    div = actions.user.ui_elements("div")
    svg, path = actions.user.ui_elements_svg(["svg", "path"])

    div_props, svg_props = parse_icon_properties(props, **additional_props)

    paths = ICON_SVG_PATH_ONLY[name] if isinstance(ICON_SVG_PATH_ONLY[name], list) else [ICON_SVG_PATH_ONLY[name]]

    return div(**div_props)[
        svg(**svg_props)[
            *[path(d=d) for d in paths]
        ]
    ]

def icon(name: str, props=None, **additional_props):
    default_props = {
        "name": name,
        **(props or {})
    }

    if name not in VALID_ICON_NAMES:
        raise ValueError(f"Invalid icon name: {name}. Valid icon names are: \n{list(ICON_SVG_PATH_ONLY.keys())}")

    validate_combined_props(default_props, additional_props, ELEMENT_ENUM_TYPE["icon"])

    if name in ICON_SVG_PATH_ONLY:
        return icon_svg_single_path_stroke(name, props, **additional_props)
    if name in ICON_CUSTOM_SVG:
        return ICON_CUSTOM_SVG[name](props, **additional_props)