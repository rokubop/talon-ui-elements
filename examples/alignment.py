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

def alignment_ui():
    div, text, screen, button = actions.user.ui_elements_new(["div", "text", "screen", "button"])

    return screen()[
        div(background_color="222222", width=1000, height=500, padding=32, flex_direction="row", align_items="flex_start", gap=32)[
            div()[
                text('flex_direction="row"', margin_bottom=16, color="FFCC00"),
                div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
                    div(padding=8, gap=8, flex_direction="row")[
                        *items(),
                    ],
                ],
            ],
            div()[
                text('flex_direction="column"', margin_bottom=16, color="FFCC00"),
                div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
                    div(padding=8, gap=8, flex_direction="column")[
                        *items()
                    ],
                ],
            ],
        ]
    ]