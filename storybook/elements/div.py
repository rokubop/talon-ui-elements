from talon import actions
from ..common import code, example_with_code
from .. import theme as t
import textwrap


def _box(label, bg="3689E8", width=60, height=40):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(
        background_color=bg,
        border_radius=4,
        padding=8,
        min_width=width,
        min_height=height,
        align_items="center",
        justify_content="center",
    )[
        text(label, font_size=12, color="FFFFFF"),
    ]


def div_stories():
    component, div, text = actions.user.ui_elements([
        "component", "div", "text"
    ])

    return div(padding=32, gap=24)[
        text("Div", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                div = actions.user.ui_elements(['div'])""")
        ),

        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            # flex_direction
            component(example_with_code, props={
                "title": "flex_direction",
                "example": div(gap=16)[
                    div(gap=8)[
                        text("column (default)", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="column", gap=8, padding=12, border_width=1, border_color=t.BORDER, border_radius=8)[
                            _box("1"),
                            _box("2"),
                            _box("3"),
                        ],
                    ],
                    div(gap=8)[
                        text("row", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", gap=8, padding=12, border_width=1, border_color=t.BORDER, border_radius=8)[
                            _box("1"),
                            _box("2"),
                            _box("3"),
                        ],
                    ],
                ],
                "code": textwrap.dedent("""\
                    div(flex_direction="column", gap=8)[
                        text("A"), text("B"), text("C"),
                    ]

                    div(flex_direction="row", gap=8)[
                        text("A"), text("B"), text("C"),
                    ]"""),
            }),

            # justify_content
            component(example_with_code, props={
                "title": "justify_content (row)",
                "example": div(gap=8)[
                    *[div(gap=4)[
                        text(jc, font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", justify_content=jc, gap=8, padding=12,
                            border_width=1, border_color=t.BORDER, border_radius=8, min_width=300)[
                            _box("1", width=40),
                            _box("2", width=40),
                            _box("3", width=40),
                        ],
                    ] for jc in ["flex_start", "center", "flex_end", "space_between"]],
                ],
                "code": textwrap.dedent("""\
                    div(flex_direction="row", justify_content="flex_start")[...]
                    div(flex_direction="row", justify_content="center")[...]
                    div(flex_direction="row", justify_content="flex_end")[...]
                    div(flex_direction="row", justify_content="space_between")[...]"""),
            }),

            # align_items
            component(example_with_code, props={
                "title": "align_items (row)",
                "example": div(flex_direction="row", gap=16)[
                    *[div(gap=4)[
                        text(ai, font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", align_items=ai, gap=8, padding=12,
                            border_width=1, border_color=t.BORDER, border_radius=8, min_height=100)[
                            _box("1", height=20),
                            _box("2", height=40),
                            _box("3", height=30),
                        ],
                    ] for ai in ["flex_start", "center", "flex_end", "stretch"]],
                ],
                "code": textwrap.dedent("""\
                    div(flex_direction="row", align_items="flex_start")[...]
                    div(flex_direction="row", align_items="center")[...]
                    div(flex_direction="row", align_items="flex_end")[...]
                    div(flex_direction="row", align_items="stretch")[...]"""),
            }),

            # gap
            component(example_with_code, props={
                "title": "gap",
                "example": div(flex_direction="row", gap=24)[
                    *[div(gap=4)[
                        text(f"gap={g}", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", gap=g, padding=12,
                            border_width=1, border_color=t.BORDER, border_radius=8)[
                            _box("1", width=40),
                            _box("2", width=40),
                            _box("3", width=40),
                        ],
                    ] for g in [0, 8, 16, 32]],
                ],
                "code": textwrap.dedent("""\
                    div(flex_direction="row", gap=0)[...]
                    div(flex_direction="row", gap=8)[...]
                    div(flex_direction="row", gap=16)[...]"""),
            }),

            # flex
            component(example_with_code, props={
                "title": "flex",
                "example": div(gap=8)[
                    div(gap=4)[
                        text("flex=1, flex=1", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", gap=8, padding=12,
                            border_width=1, border_color=t.BORDER, border_radius=8, width=400)[
                            div(
                                background_color="3689E8", border_radius=4, padding=8,
                                min_height=40, align_items="center", justify_content="center", flex=1,
                            )[text("flex=1", font_size=12, color="FFFFFF")],
                            div(
                                background_color="E24A70", border_radius=4, padding=8,
                                min_height=40, align_items="center", justify_content="center", flex=1,
                            )[text("flex=1", font_size=12, color="FFFFFF")],
                        ],
                    ],
                    div(gap=4)[
                        text("flex=1, flex=2", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", gap=8, padding=12,
                            border_width=1, border_color=t.BORDER, border_radius=8, width=400)[
                            div(
                                background_color="3689E8", border_radius=4, padding=8,
                                min_height=40, align_items="center", justify_content="center", flex=1,
                            )[text("flex=1", font_size=12, color="FFFFFF")],
                            div(
                                background_color="E24A70", border_radius=4, padding=8,
                                min_height=40, align_items="center", justify_content="center", flex=2,
                            )[text("flex=2", font_size=12, color="FFFFFF")],
                        ],
                    ],
                ],
                "code": textwrap.dedent("""\
                    div(flex_direction="row", width=400)[
                        div(flex=1, ...)[...],
                        div(flex=2, ...)[...],
                    ]"""),
            }),

            # padding and margin
            component(example_with_code, props={
                "title": "padding & margin",
                "example": div(flex_direction="row", gap=24)[
                    div(gap=4)[
                        text("padding=20", font_size=12, color=t.TEXT_MUTED),
                        div(background_color=t.BG_RAISED, border_radius=8, border_width=1, border_color=t.BORDER)[
                            div(padding=20, background_color="3689E855", border_radius=4)[
                                text("content", font_size=12, color="FFFFFF"),
                            ],
                        ],
                    ],
                    div(gap=4)[
                        text("margin=20", font_size=12, color=t.TEXT_MUTED),
                        div(background_color=t.BG_RAISED, border_radius=8, border_width=1, border_color=t.BORDER)[
                            div(margin=20, background_color="E24A7055", border_radius=4)[
                                text("content", font_size=12, color="FFFFFF"),
                            ],
                        ],
                    ],
                    div(gap=4)[
                        text("both", font_size=12, color=t.TEXT_MUTED),
                        div(background_color=t.BG_RAISED, border_radius=8, border_width=1, border_color=t.BORDER)[
                            div(margin=20, padding=20, background_color="22AA6655", border_radius=4)[
                                text("content", font_size=12, color="FFFFFF"),
                            ],
                        ],
                    ],
                ],
                "code": textwrap.dedent("""\
                    # padding: space inside (pushes content inward)
                    div(padding=20)[text("content")]

                    # margin: space outside (pushes element away from siblings)
                    div(margin=20)[text("content")]"""),
            }),

            # flex_wrap
            component(example_with_code, props={
                "title": "flex_wrap",
                "example": div(gap=8)[
                    text("flex_wrap=\"wrap\"", font_size=12, color=t.TEXT_MUTED),
                    div(
                        flex_direction="row", flex_wrap="wrap", gap=8, padding=12,
                        border_width=1, border_color=t.BORDER, border_radius=8, width=280,
                    )[
                        *[_box(f"{i+1}", bg=["3689E8", "E24A70", "22AA66", "9B59B6", "E67E22", "1ABC9C"][i % 6], width=60, height=40)
                          for i in range(9)],
                    ],
                ],
                "code": textwrap.dedent("""\
                    div(flex_direction="row", flex_wrap="wrap",
                        gap=8, width=280)[
                        div(...)[text("1")],
                        div(...)[text("2")],
                        # ...items wrap to next line
                    ]"""),
            }),

            # overflow scroll
            component(example_with_code, props={
                "title": "overflow_y=\"scroll\"",
                "example": div(
                    height=120, overflow_y="scroll", padding=8, gap=8,
                    border_width=1, border_color=t.BORDER, border_radius=8, width=200,
                )[
                    *[_box(f"Item {i+1}", bg="3689E8" if i % 2 == 0 else "E24A70", width=160) for i in range(8)],
                ],
                "code": textwrap.dedent("""\
                    div(height=120, overflow_y="scroll", gap=8)[
                        text("Item 1"),
                        text("Item 2"),
                        # ...more items
                    ]"""),
            }),

            # margin auto
            component(example_with_code, props={
                "title": "margin: \"auto\"",
                "example": div(gap=16)[
                    div(gap=4)[
                        text("margin=\"auto\" (center both axes in column)", font_size=12, color=t.TEXT_MUTED),
                        div(padding=12, border_width=1, border_color=t.BORDER, border_radius=8, width=300, height=100)[
                            div(margin="auto")[
                                _box("A", width=50, height=30, bg="3689E8"),
                            ],
                        ],
                    ],
                    div(gap=4)[
                        text("margin_left=\"auto\" (push right)", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", padding=12, border_width=1, border_color=t.BORDER, border_radius=8, width=300)[
                            _box("A", width=50, bg="3689E8"),
                            div(margin_left="auto")[
                                _box("B", width=50, bg="E24A70"),
                            ],
                        ],
                    ],
                    div(gap=4)[
                        text("margin_x=\"auto\" (center horizontally in row)", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", padding=12, border_width=1, border_color=t.BORDER, border_radius=8, width=300)[
                            div(margin_x="auto")[
                                _box("A", width=50, bg="22AA66"),
                            ],
                        ],
                    ],
                    div(gap=4)[
                        text("space-between via auto margins", font_size=12, color=t.TEXT_MUTED),
                        div(flex_direction="row", padding=12, border_width=1, border_color=t.BORDER, border_radius=8, width=300)[
                            _box("A", width=50, bg="3689E8"),
                            div(margin_left="auto", margin_right="auto")[
                                _box("B", width=50, bg="E24A70"),
                            ],
                            _box("C", width=50, bg="22AA66"),
                        ],
                    ],
                ],
                "code": textwrap.dedent("""\
                    # Center on both axes (column is default)
                    div(width=300, height=100)[
                        div(margin="auto")[text("centered")]
                    ]

                    # Push element to the right
                    div(flex_direction="row", width=300)[
                        text("A"),
                        div(margin_left="auto")[text("B")]
                    ]

                    # Center horizontally
                    div(flex_direction="row", width=300)[
                        div(margin_x="auto")[text("A")]
                    ]

                    # Space between effect
                    div(flex_direction="row", width=300)[
                        text("A"),
                        div(margin_left="auto", margin_right="auto")[text("B")],
                        text("C"),
                    ]"""),
            }),

            # nesting
            component(example_with_code, props={
                "title": "Nesting",
                "example": div(
                    padding=16, gap=12, background_color=t.BG_RAISED,
                    border_radius=8, border_width=1, border_color=t.BORDER,
                )[
                    text("Card Title", font_size=16, font_weight="bold", color=t.TEXT),
                    div(flex_direction="row", gap=8)[
                        div(flex=1, background_color="3689E8", border_radius=4, padding=12,
                            align_items="center", justify_content="center")[
                            text("Left", font_size=12, color="FFFFFF"),
                        ],
                        div(flex=1, gap=8)[
                            div(background_color="E24A70", border_radius=4, padding=8,
                                align_items="center", justify_content="center")[
                                text("Top Right", font_size=12, color="FFFFFF"),
                            ],
                            div(background_color="22AA66", border_radius=4, padding=8,
                                align_items="center", justify_content="center")[
                                text("Bottom Right", font_size=12, color="FFFFFF"),
                            ],
                        ],
                    ],
                ],
                "code": textwrap.dedent("""\
                    div(padding=16, gap=12, background_color="333333")[
                        text("Card Title", font_weight="bold"),
                        div(flex_direction="row", gap=8)[
                            div(flex=1, ...)[text("Left")],
                            div(flex=1, gap=8)[
                                div(...)[text("Top Right")],
                                div(...)[text("Bottom Right")],
                            ],
                        ],
                    ]"""),
            }),
        ],
    ]
