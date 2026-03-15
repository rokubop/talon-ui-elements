from talon import actions

def show_app_layout():
    actions.user.ui_elements_show(app_layout_ui)

def app_layout_ui():
    screen, div, text = actions.user.ui_elements(
        ["screen", "div", "text"]
    )

    long_content = "\n".join([f"line {i}: some_var = do_something(arg1, arg2, arg3)" for i in range(200)])

    return screen(justify_content="center", align_items="center")[
        div(
            width="90%",
            height=900,
            background_color="#1f2435",
            flex_direction="column",
        )[
            # Main row
            div(flex_direction="row", flex=1, overflow="hidden")[
                # Col 1: Fixed sidebar
                div(width=420, flex_shrink=0, padding=32, gap=6, overflow_y="auto",
                    background_color="#1f2435")[
                    text("FIELD 1", font_size=14, color="#8892aa"),
                    div(background_color="#2c3348", padding=10, width="100%")[
                        text("some value", color="#e4e8f0"),
                    ],
                    text("FIELD 2", font_size=14, color="#8892aa", margin_top=18),
                    div(background_color="#2c3348", padding=10, width="100%")[
                        text("another value", color="#e4e8f0"),
                    ],
                    text("LIST", font_size=14, color="#8892aa", margin_top=20),
                    div(background_color="#252b3e", flex=1, overflow_y="auto", padding=4)[
                        text("Item 1", font_size=15, color="#e4e8f0"),
                        text("Item 2", font_size=15, color="#e4e8f0"),
                        text("Item 3", font_size=15, color="#e4e8f0"),
                    ],
                ],
                # Col 2: Middle panel
                div(width="25%", background_color="#1a1e2a", padding=24, gap=4,
                    border_left_width=1, border_color="#333a50")[
                    text("FILES", font_size=14, color="#8892aa"),
                    text("file_a.py", font_size=16, color="#4da6ff"),
                    text("file_b.py", font_size=16, color="#4da6ff"),
                    text("file_c.py", font_size=16, color="#4da6ff"),
                ],
                # Col 3: Preview (flex fill, long content)
                div(flex=1, min_width=0, background_color="#1a1e2a", padding=24,
                    overflow_x="auto", overflow_y="auto")[
                    text("file_a.py", font_size=14, color="#6db3ff", font_weight="bold"),
                    div(background_color="#252b3e", padding=16, flex=1, overflow_x="auto",
                        overflow_y="auto")[
                        text(long_content, font_size=14, font_family="monospace",
                             color="#e4e8f0", white_space="pre"),
                    ],
                ],
            ],
            # Bottom bar
            div(padding=20, background_color="#1a1e2a", border_top_width=1,
                border_color="#333a50")[
                text("Bottom Bar", color="#8892aa"),
            ],
        ]
    ]
