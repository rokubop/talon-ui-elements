from talon import actions
from ..common import example_with_code, code
from .. import theme as t
import textwrap

def default_table():
    table, th, tr, td, text, style = actions.user.ui_elements([
        "table", "th", "tr", "td", "text", "style"
    ])

    style({
        "td": {
            "padding": 8,
        },
        "th": {
            "padding": 8,
        }
    })

    return table()[
        tr()[
            th()[text("Header 1")],
            th()[text("Header 2")],
            th()[text("Header 3")],
        ],
        tr()[
            td()[text("Row 1, Cell 1")],
            td()[text("Row 1, Cell 2")],
            td()[text("Row 1, Cell 3")],
        ],
        tr()[
            td()[text("Row 2, Cell 1")],
            td()[text("Row 2, Cell 2")],
            td()[text("Row 2, Cell 3")],
        ],
    ]

def bordered_table():
    table, th, tr, td, text, style = actions.user.ui_elements([
        "table", "th", "tr", "td", "text", "style"
    ])

    style({
        "td": {
            "border_width": 1,
            "border_color": "#555555",
            "padding": 8,
        },
        "th": {
            "border": 1,
            "border_color": "#555555",
            "padding": 8,
        }
    })

    return table()[
        tr()[
            th()[text("Header 1")],
            th()[text("Header 2")],
            th()[text("Header 3")],
        ],
        tr()[
            td()[text("Row 1, Cell 1")],
            td()[text("Row 1, Cell 2")],
            td()[text("Row 1, Cell 3")],
        ],
        tr()[
            td()[text("Row 2, Cell 1")],
            td()[text("Row 2, Cell 2")],
            td()[text("Row 2, Cell 3")],
        ],
    ]

def flush_table():
    table, th, tr, td, div, text, style = actions.user.ui_elements([
        "table", "th", "tr", "td", "div", "text", "style"
    ])

    style({
        "td": {
            "padding": 8,
            "padding_left": 0,
        },
        "th": {
            "padding": 8,
            "padding_left": 0,
        }
    })

    return div(gap=16, align_items="flex_start")[
        text("Settings", font_size=18, font_weight="bold"),
        text("Configure your preferences below.", font_size=14, color="AAAAAA"),
        table()[
            tr()[
                th()[text("Option")],
                th()[text("Value")],
                th()[text("Description")],
            ],
            tr()[
                td()[text("Theme")],
                td()[text("Dark")],
                td()[text("Color scheme")],
            ],
            tr()[
                td()[text("Font size")],
                td()[text("14px")],
                td()[text("Base text size")],
            ],
        ],
    ]

STRIPE_COLOR = "FFFFFF15"

def striped_table():
    table, th, tr, td, text, style = actions.user.ui_elements([
        "table", "th", "tr", "td", "text", "style"
    ])

    style({
        "td": {
            "padding": 8,
        },
        "th": {
            "padding": 8,
        }
    })

    rows = [
        ("Row 1, Cell 1", "Row 1, Cell 2", "Row 1, Cell 3"),
        ("Row 2, Cell 1", "Row 2, Cell 2", "Row 2, Cell 3"),
        ("Row 3, Cell 1", "Row 3, Cell 2", "Row 3, Cell 3"),
        ("Row 4, Cell 1", "Row 4, Cell 2", "Row 4, Cell 3"),
    ]

    return table()[
        tr()[
            th()[text("Header 1")],
            th()[text("Header 2")],
            th()[text("Header 3")],
        ],
        *[tr(background_color=STRIPE_COLOR if i % 2 == 0 else None)[
            td()[text(r[0])],
            td()[text(r[1])],
            td()[text(r[2])],
        ] for i, r in enumerate(rows)],
    ]

# Shared row data used by both the inline example and the windowed launch
# below, so we're comparing the exact same content in both contexts.
_EMPTY_CELL_ROWS = [
    ("1", ["pop"], ["0.91"]),
    ("2", ["hiss"], ["0.83"]),
    ("3", [], []),               # ← empty pattern + prob
    ("4", ["click"], ["0.77"]),
    ("5", [], []),               # ← empty pattern + prob
    ("6", ["pop", "hiss"], ["0.62", "0.55"]),
]


def _empty_cell_rows_table():
    # Mirror the parrot-tester frames-table styling: padding + border_bottom
    # on every cell. The border_bottom is the line that visually leaks past
    # the window's right edge for empty rows in the original bug report.
    table, th, tr, td, div, text, style = actions.user.ui_elements([
        "table", "th", "tr", "td", "div", "text", "style"
    ])
    style({
        "th": {
            "padding": 10,
            "padding_left": 12,
            "padding_right": 12,
            "align_items": "flex_start",
            "border_bottom": 1,
        },
        "td": {
            "padding": 8,
            "padding_left": 12,
            "padding_right": 12,
            "align_items": "flex_end",
            "border_bottom": 1,
            "justify_content": "center",
        },
    })
    return table(height="100%", overflow_y="scroll", padding=16, padding_top=0)[
        tr()[
            th()[text("Frame")],
            th()[text("Pattern")],
            th()[text("Prob.")],
        ],
        *[tr()[
            td()[text(frame_id)],
            td(align_items="flex_start")[div(gap=10, min_width=60)[
                *[text(p) for p in patterns]
            ]],
            td(align_items="flex_end")[div(gap=10)[
                *[text(p) for p in probs]
            ]],
        ] for frame_id, patterns, probs in _EMPTY_CELL_ROWS],
    ]


def _windowed_empty_cell_table():
    """Same table content, wrapped in a window + min_height/max_height
    container that mirrors the parrot-tester frames-page layout."""
    screen, window, div, component = actions.user.ui_elements([
        "screen", "window", "div", "component"
    ])
    return screen(align_items="center", justify_content="center")[
        window(
            title="Empty-cell table (windowed repro)",
            min_width=1100,
            background_color="1a1a1f",
            border_width=1,
            border_radius=8,
            resizable=True,
        )[
            div(min_height=750, max_height=900)[
                component(_empty_cell_rows_table),
            ],
        ],
    ]


def _launch_windowed_empty_cell_table():
    try:
        actions.user.ui_elements_hide(_windowed_empty_cell_table)
    except Exception:
        pass
    actions.user.ui_elements_show(_windowed_empty_cell_table)


def empty_div_in_cell_table():
    """Inline preview of the same row data used by the windowed launch.
    Adds a button below that opens the table inside a window mirroring
    the parrot-tester layout (min_width=1100, max_height=900) -- the bug
    manifests as the empty rows' border_bottom extending past the column
    width, in some cases growing the containing window past its sizing."""
    div, text, button, component = actions.user.ui_elements([
        "div", "text", "button", "component"
    ])
    return div(gap=12, align_items="flex_start")[
        component(_empty_cell_rows_table),
        button(
            "Launch windowed repro (parrot-tester sizing)",
            on_click=lambda: _launch_windowed_empty_cell_table(),
            font_size=14, padding=10, padding_left=14, padding_right=14,
            border_radius=6, border_width=1,
        ),
        text(
            "Compare the inline table above (no window) with the windowed one "
            "(min_width=1100, content min_height=750/max_height=900). Empty "
            "rows render their border_bottom extending past the populated "
            "column width.",
            font_size=12, color="888",
        ),
    ]


def colspan_table():
    table, th, tr, td, text, style = actions.user.ui_elements([
        "table", "th", "tr", "td", "text", "style"
    ])

    style({
        "td": {
            "padding": 8,
        },
        "th": {
            "padding": 8,
        }
    })

    return table()[
        tr()[
            th()[text("Header 1")],
            th()[text("Header 2")],
            th()[text("Header 3")],
        ],
        tr()[
            td()[text("Row 1, Cell 1")],
            td(colspan=2, background_color="blue")[text("Row 1, Cell 2 & 3")],
        ],
        tr()[
            td()[text("Row 2, Cell 1")],
            td()[text("Row 2, Cell 2")],
            td()[text("Row 2, Cell 3")],
        ],
    ]

def table_stories():
    table, th, tr, td, div, text, component, style = actions.user.ui_elements([
        "table", "th", "tr", "td", "div", "text", "component", "style"
    ])

    return div(padding=32, gap=24)[
        text("Table", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                table, th, tr, td = actions.user.ui_elements(['table', 'th', 'tr', 'td'])"""
            )
        ),

        div(gap=16)[
            text("Stories", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12,border_color=t.BORDER),
            component(example_with_code, props={
                "title": "Default Table",
                "example": component(default_table),
                "code": textwrap.dedent("""\
                    def default_table():
                        table, th, tr, td, style = actions.user.ui_elements([
                            'table', 'th', 'tr', 'td', 'style'
                        ])

                        style({
                            "td": {
                                "padding": 8,
                            },
                            "th": {
                                "padding": 8,
                            }
                        }),

                        return table()[
                            tr()[
                                th()[text("Header 1")],
                                th()[text("Header 2")],
                                th()[text("Header 3")],
                            ],
                            tr()[
                                td()[text("Row 1, Cell 1")],
                                td()[text("Row 1, Cell 2")],
                                td()[text("Row 1, Cell 3")],
                            ],
                            tr()[
                                td()[text("Row 2, Cell 1")],
                                td()[text("Row 2, Cell 2")],
                                td()[text("Row 2, Cell 3")],
                            ],
                        ]
                    )

                    # Use component to encapsulate the style
                    component(default_table)"""
                )
            }),
            component(example_with_code, props={
                "title": "Flush with content",
                "example": component(flush_table),
                "code": textwrap.dedent("""\
                    style({
                        "td": { "padding": 8, "padding_left": 0 },
                        "th": { "padding": 8, "padding_left": 0 },
                    })

                    div(gap=16, align_items="flex_start")[
                        text("Settings", font_size=18, font_weight="bold"),
                        text("Configure your preferences below.", font_size=14),
                        table()[
                            tr()[
                                th()[text("Option")],
                                th()[text("Value")],
                                th()[text("Description")],
                            ],
                            tr()[
                                td()[text("Theme")],
                                td()[text("Dark")],
                                td()[text("Color scheme")],
                            ],
                        ],
                    ]"""
                )
            }),
            component(example_with_code, props={
                "title": "Bordered cells",
                "example": component(bordered_table),
                "code": textwrap.dedent("""\
                    def bordered_table():
                        table, th, tr, td, style = actions.user.ui_elements([
                            'table', 'th', 'tr', 'td', 'style'
                        ])

                        style({
                            "td": {
                                "padding": 8,
                                "border_width": 1,
                                "border_color": "#555555",
                            },
                            "th": {
                                "padding": 8,
                                "border_width": 1,
                                "border_color": "#555555",
                            }
                        }),

                        return table()[
                            tr()[
                                th()[text("Header 1")],
                                th()[text("Header 2")],
                                th()[text("Header 3")],
                            ],
                            tr()[
                                td()[text("Row 1, Cell 1")],
                                td()[text("Row 1, Cell 2")],
                                td()[text("Row 1, Cell 3")],
                            ],
                            tr()[
                                td()[text("Row 2, Cell 1")],
                                td()[text("Row 2, Cell 2")],
                                td()[text("Row 2, Cell 3")],
                            ],
                        ]

                    # Use component to encapsulate the style
                    component(bordered_table)"""
                )
            }),
            component(example_with_code, props={
                "title": "Empty inner div in some cells (suspected layout bug)",
                "example": component(empty_div_in_cell_table),
                "code": textwrap.dedent("""\
                    # Mirrors the parrot tester's frames-table cell pattern.
                    # Each cell wraps its content in an inner div whose
                    # children come from a per-row list. Rows where that
                    # list is empty get an empty inner div -- empty rows'
                    # border_bottom renders extending past the column width.
                    rows = [
                        ("1", ["pop"],          ["0.91"]),
                        ("2", ["hiss"],         ["0.83"]),
                        ("3", [],               []),         # empty row
                        ("4", ["click"],        ["0.77"]),
                        ("5", [],               []),         # empty row
                        ("6", ["pop", "hiss"],  ["0.62", "0.55"]),
                    ]

                    table(height="100%", overflow_y="scroll")[
                        tr()[th()[text("Frame")], th()[text("Pattern")], th()[text("Prob.")]],
                        *[tr()[
                            td()[text(fid)],
                            td()[div(gap=10, min_width=60)[*[text(p) for p in patterns]]],
                            td()[div(gap=10)[*[text(p) for p in probs]]],
                        ] for fid, patterns, probs in rows],
                    ]"""
                )
            }),
            component(example_with_code, props={
                "title": "Striped rows",
                "example": component(striped_table),
                "code": textwrap.dedent("""\
                    rows = [("Cell 1", "Cell 2", "Cell 3"), ...]

                    table()[
                        tr()[
                            th()[text("Header 1")],
                            th()[text("Header 2")],
                            th()[text("Header 3")],
                        ],
                        *[tr(background_color="FFFFFF15" if i % 2 == 0 else None)[
                            td()[text(r[0])],
                            td()[text(r[1])],
                            td()[text(r[2])],
                        ] for i, r in enumerate(rows)],
                    ]"""
                )
            }),
        ],
    ]
