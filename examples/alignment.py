from talon import actions

def items():
    div, text = actions.user.ui_elements_new(["div", "text"])

    return [
        div(border_width=1, border_color="CCCCCC", padding=8)[
            text("Hello")
        ],
        div(border_width=1, border_color="CCCCCC", padding=8)[
            text("to")
        ],
        div(border_width=1, border_color="CCCCCC", padding=8)[
            text("the")
        ],
        div(border_width=1, border_color="CCCCCC", padding=8)[
            text("world")
        ],
    ]

def items_flex():
    div, text = actions.user.ui_elements_new(["div", "text"])

    return [
        div(border_width=1, border_color="CCCCCC", padding=8, flex=1)[
            text("Hello")
        ],
        div(border_width=1, border_color="CCCCCC", padding=8, flex=1)[
            text("to")
        ],
        div(border_width=1, border_color="CCCCCC", padding=8, flex=2)[
            text("the")
        ],
        div(border_width=1, border_color="CCCCCC", padding=8, flex=1)[
            text("world")
        ],
    ]

def example_ui(title: str, content):
    div, text = actions.user.ui_elements_new(["div", "text"])

    return div()[
        text(title, margin_bottom=16, color="FFCC00"),
        div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
            content
        ],
    ]

def example1_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui("flex_direction='row'", content=div(padding=8, gap=8, flex_direction="row", height="100%")[
        *items(),
    ])

def example2_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui("flex_direction='column'", content=div(padding=8, gap=8, flex_direction="column")[
        *items(),
    ])

def example3_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui('flex_direction="row", justify_content="space_between"', content=div(padding=8, gap=8, flex_direction="row", height="100%", justify_content="space_between")[
        *items(),
    ])

def example4_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui('flex_direction="row", align_items="flex_start"', content=div(padding=8, gap=8, flex_direction="row", align_items="flex_start")[
        *items(),
    ])

def example5_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui('align_items="center", justify_content="center"', content=div(padding=8, gap=8, flex_direction="row", height="100%", align_items="center", justify_content="center")[
        *items(),
    ])

def example6_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui('flex_direction="row", justify_content="flex_end"', content=div(padding=8, gap=8, flex_direction="row", justify_content="flex_end")[
        *items(),
    ])

def example7_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui('justify_content="center"', content=div(padding=8, gap=8, flex_direction="row", justify_content="center", height="100%")[
        *items(),
    ])

def example8_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui('justify_content="center"', content=div(padding=8, gap=8, flex_direction="row", justify_content="center")[
        *items(),
    ])

def example9_ui():
    div = actions.user.ui_elements_new(["div"])

    return example_ui('flex=1 on children', content=div(padding=8, gap=8, flex_direction="row")[
        *items_flex(),
    ])

def alignment_ui():
    div, text, screen = actions.user.ui_elements_new(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="222222", padding=32, border_radius=8, border_width=1, border_color="555555")[
            # how do i get another div here?
            div(flex_direction="row", gap=32)[
                div(height="100%", padding=16, background_color="FFCC00")[
                    text('height="100%"', color="000000"),
                ],
                div(background_color="121212")[
                    div(flex_direction='row', justify_content="space_between", width="100%", background_color="FF000033", margin_bottom=16)[
                        text("Alignment", font_size=32),
                        text("ui-elements", font_size=32, color="FFCC00"),
                    ],
                    div(padding=32, flex_direction="row", gap=32)[
                        example1_ui(),
                        example2_ui(),
                        example3_ui(),
                    ],
                    div(padding=32, flex_direction="row", gap=32)[
                        example4_ui(),
                        example5_ui(),
                        example6_ui(),
                    ],
                    div(padding=32, flex_direction="row", gap=32)[
                        example7_ui(),
                        example8_ui(),
                        example9_ui(),
                    ],
                ]
            ]
        ]
    ]

# def alignment_ui():
#     div, text, screen = actions.user.ui_elements_new(["div", "text", "screen"])

#     return screen(justify_content="center", align_items="center")[
#         div(background_color="222222")[
#             # how do i get another div here?
#             text("Alignment", font_size=32),
#             div()[
#                 div(width=500, background_color="FF000044", height=200)
#             ]
#         ]
#     ]