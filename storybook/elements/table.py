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
