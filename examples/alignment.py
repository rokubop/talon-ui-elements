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
    div, text, screen = actions.user.ui_elements_new(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(flex_direction="row")[
            # how do i get another div here?
            div(background_color="222222", flex_direction="column", padding=32, border_radius=8, border_width=1, border_color="555555")[
                div(padding=32, flex_direction="row", gap=32)[
                    div()[
                        text('flex_direction="row"', margin_bottom=16, color="FFCC00"),
                        div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
                            div(padding=8, gap=8, flex_direction="row", height="100%")
                            [
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
                ],
                div(padding=32, flex_direction="row", gap=32)[
                    div()[
                        text('flex_direction="row", justify_content="space_between"', margin_bottom=16, color="FFCC00"),
                        div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
                            div(padding=8, gap=8, flex_direction="row", height="100%", justify_content="space_between")
                            [
                                *items(),
                            ],
                        ],
                    ],
                    div()[
                        text('flex_direction="row", align_items="flex_start"', margin_bottom=16, color="FFCC00"),
                        div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
                            div(padding=8, gap=8, flex_direction="row", align_items="flex_start")[
                                *items()
                            ],
                        ],
                    ],
                ],
                div(padding=32, flex_direction="row", gap=32)[
                    div()[
                        text('align_items="center", justify_content="center"', margin_bottom=16, color="FFCC00"),
                        div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
                            div(padding=8, gap=8, flex_direction="row", height="100%", align_items="center", justify_content="center")
                            [
                                *items(),
                            ],
                        ],
                    ],
                    div()[
                        text('flex_direction="row", justify_content="flex_end"', margin_bottom=16, color="FFCC00"),
                        div(background_color="333333", width=400, height=150, border_radius=4, border_width=1, border_color="CCCCCC")[
                            div(padding=8, gap=8, flex_direction="row", justify_content="flex_end")[
                                *items()
                            ],
                        ],
                    ],
                ],
            ]
        ]
    ]