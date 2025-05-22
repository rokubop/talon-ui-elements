from talon import actions
from ..common import example_with_code, code
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
        text("Table", font_size=22, font_weight="bold", color="#F1F1F1"),
        code(
            textwrap.dedent("""\
                table, th, tr, td = actions.user.ui_elements(['table', 'th', 'tr', 'td'])"""
            )
        ),

        div(gap=16)[
            text("Stories", font_size=18, font_weight="bold", color="#F1F1F1", border_bottom=1, padding_bottom=12,border_color="#333333"),
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
            # component(example_with_code, props={
            #     "title": "Colspan",
            #     "example": component(colspan_table),
            #     "code": textwrap.dedent("""\
            #         def colspan_table():
            #             table, th, tr, td, style = actions.user.ui_elements([
            #                 'table', 'th', 'tr', 'td', 'style'
            #             ])

            #             style({
            #                 "td": {
            #                     "padding": 8,
            #                 },
            #                 "th": {
            #                     "padding": 8,
            #                 }
            #             }),

            #             return table()[
            #                 tr()[
            #                     th()[text("Header 1")],
            #                     th()[text("Header 2")],
            #                     th()[text("Header 3")],
            #                 ],
            #                 tr()[
            #                     td()[text("Row 1, Cell 1")],
            #                     td(colspan=2)[text("Row 1, Cell 2 & 3")],
            #                 ],
            #                 tr()[
            #                     td()[text("Row 2, Cell 1")],
            #                     td()[text("Row 2, Cell 2")],
            #                     td()[text("Row 2, Cell 3")],
            #                 ],
            #             ]

            #         # Use component to encapsulate the style
            #         component(colspan_table)"""
            #     )
            # }),
        ],
    ]
