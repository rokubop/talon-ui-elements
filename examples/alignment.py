from talon import actions

YELLOW = "FFCC00"
LIGHT_BLUE = "87CEEB"
WHITE = "CCCCCC"

def items():
    div, text = actions.user.ui_elements(["div", "text"])

    return [
        div(border_width=1, border_color=WHITE, padding=8)[
            text("Hello")
        ],
        div(border_width=1, border_color=WHITE, padding=8)[
            text("to")
        ],
        div(border_width=1, border_color=WHITE, padding=8)[
            text("the")
        ],
        div(border_width=1, border_color=WHITE, padding=8)[
            text("world")
        ],
    ]

def items_first_flex():
    div, text = actions.user.ui_elements(["div", "text"])

    return [
        div(border_width=1, border_color=WHITE, padding=8, flex=1)[
            text("Hello")
        ],
        div(border_width=1, border_color=WHITE, padding=8)[
            text("to")
        ],
        div(border_width=1, border_color=WHITE, padding=8)[
            text("the")
        ],
        div(border_width=1, border_color=WHITE, padding=8)[
            text("world")
        ],
    ]

def items_all_flex():
    div, text = actions.user.ui_elements(["div", "text"])

    return [
        div(border_width=1, border_color=WHITE, padding=8, flex=1)[
            text("Hello")
        ],
        div(border_width=1, border_color=WHITE, padding=8, flex=1)[
            text("to")
        ],
        div(border_width=1, border_color=WHITE, padding=8, flex=1)[
            text("the")
        ],
        div(border_width=1, border_color=WHITE, padding=8, flex=1)[
            text("world")
        ],
    ]

def example_ui(number: int, title, content):
    div, text = actions.user.ui_elements(["div", "text"])

    return div()[
        div(flex_direction="row", align_items="center", margin_bottom=16)[
            text(f"{number}. "),
            title,
        ],
        div(background_color="333333", width=360, height=180, border_radius=4, border_width=1, border_color=WHITE)[
            content
        ],
    ]

def example1_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row")[
        text('flex_direction=', color=WHITE),
        text('"column"', color=YELLOW),
        text(', align_items=', color=WHITE),
        text('"stretch"', color=YELLOW),
    ]

    return example_ui(1, title, content=div(padding=8, gap=8)[
        *items(),
    ])

def example2_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row")[
        text('flex_direction=', color=WHITE),
        text('"row"', color=YELLOW),
        text(', height=', color=WHITE),
        text('"100%"', color=YELLOW),
    ]

    return example_ui(2, title, content=div(padding=8, gap=8, flex_direction="row", height="100%")[
        *items(),
    ])

def example3_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row")[
        text('justify_content=', color=WHITE),
        text('"space_between"', color=YELLOW),
    ]

    return example_ui(3, title, content=div(padding=8, gap=8, flex_direction="row", height="100%", justify_content="space_between")[
        *items(),
    ])

def example4_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row")[
        text('flex_direction=', color=WHITE),
        text('"row"', color=YELLOW),
        text(', align_items=', color=WHITE),
        text('"flex_start"', color=YELLOW),
    ]

    return example_ui(4, title, content=div(padding=8, gap=8, flex_direction="row", align_items="flex_start")[
        *items(),
    ])

def example5_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row")[
        text('align_items=', color=WHITE),
        text('"center"', color=YELLOW),
        text(', justify_content=', color=WHITE),
        text('"center"', color=YELLOW),
    ]

    return example_ui(5, title, content=div(padding=8, gap=8, height="100%", flex_direction="row", align_items="center", justify_content="center")[
        *items(),
    ])

def example6_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row")[
        text('flex_direction=', color=WHITE),
        text('"column"', color=YELLOW),
        text(', align_items=', color=WHITE),
        text('"flex_end"', color=YELLOW),
    ]

    return example_ui(6, title, content=div(padding=8, gap=8, flex_direction="column", align_items="flex_end")[
        *items(),
    ])

def example7_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row")[
        text('justify_content=', color=WHITE),
        text('"center"', color=YELLOW),
        text(', height=', color=WHITE),
        text('"100%"', color=YELLOW),
    ]

    return example_ui(7, title, content=div(padding=8, gap=8, flex_direction="row", justify_content="center", height="100%")[
        *items(),
    ])

def example8_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row", align_items="center")[
        div(flex_direction="row")[
            text('flex=', color=WHITE),
            text('1', color=YELLOW),
        ],
        text(' on first child', color=WHITE),
    ]

    return example_ui(8, title, content=div(padding=8, gap=8, flex_direction="row")[
        *items_first_flex(),
    ])

def example9_ui():
    div, text = actions.user.ui_elements(["div", "text"])

    title = div(flex_direction="row", align_items="center")[
        div(flex_direction="row")[
            text('flex=', color=WHITE),
            text('1', color=YELLOW),
        ],
        text(' on every child', color=WHITE),
    ]

    return example_ui(9, title, content=div(padding=8, gap=8, flex_direction="row")[
        *items_all_flex(),
    ])

def alignment_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="222222", padding=32, border_radius=8, border_width=1, border_color="555555")[
            div(flex_direction="row", gap=32)[
                div(padding=16, background_color=YELLOW, justify_content="space_between")[
                    text('A', color="000000"),
                    text('Z', color="000000"),
                ],
                div()[
                    div(flex_direction='row', justify_content="space_between", padding_bottom=16, margin_bottom=16, border_bottom=1, border_color="555555")[
                        text("Alignment", font_size=32),
                        text("talon-ui-elements", font_size=32, color=YELLOW),
                    ],
                    text("(default)", color=LIGHT_BLUE, margin_left=24, margin_bottom=-8, margin_top=16),
                    div(padding=24, flex_direction="row", gap=24)[
                        example1_ui(),
                        example2_ui(),
                        example3_ui(),
                    ],
                    div(padding=24, flex_direction="row", gap=24)[
                        example4_ui(),
                        example5_ui(),
                        example6_ui(),
                    ],
                    div(padding=24, flex_direction="row", gap=24)[
                        example7_ui(),
                        example8_ui(),
                        example9_ui(),
                    ],
                ]
            ]
        ]
    ]

def show_alignment_ui():
    actions.user.ui_elements_show(alignment_ui)

def hide_alignment_ui():
    actions.user.ui_elements_hide(alignment_ui)