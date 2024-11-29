from talon import actions

YELLOW = "FFCC00"
WHITE = "CCCCCC"

text = 0

def code(text_str):
    text = actions.user.ui_elements(["text"])

    return text(text_str, color=YELLOW)

def updating_content_ui():
    div, text, screen, state, button = actions.user.ui_elements(["div", "text", "screen", "state", "button"])

    # use a ref to interact directly with an elementwp - faster, no need to re-render the entire layout
    # text_ref.set_text(value) is same as actions.user.ui_elements_set_text(id, value)
    # text_ref.set(property, value) is same as actions.user.ui_elements_set(id, property, value)
    # text_ref = ref("text_with_id")

    # use a state to re-render the entire layout. states are global, even across different UIs.
    # can also use state.get("text_state") and state.set("text_state", value)
    text_state, set_text_state = state.use("text_state", 0)

    # use_effect(lambda: print("time", [text_state]))

    return screen(justify_content="center", align_items="center")[
        div(background_color="222222", padding=32, border_radius=8, border_width=1, border_color="555555")[
            div(flex_direction="row", gap=32)[
                div()[
                    div(flex_direction='row', justify_content="space_between", padding_bottom=16, margin_bottom=16, border_bottom=1, border_color="555555")[
                        text("Updating content", font_size=32),
                        text("talon-ui-elements", font_size=32, color=YELLOW),
                    ],
                    div(flex_direction="row", gap=16, margin_top=32, width=800)[
                        div(flex=1, background_color="333333", padding=16, border_radius=8, border_width=1, border_color="555555")[
                            div(flex_direction="row", margin_bottom=16)[
                                code("actions.user.ui_elements_set_state"),
                                text(" /"),
                                code("use_state"),
                            ],
                            text("Rerenders the entire layout. Slow render."),
                            text(text_state, font_size=32, margin=16),
                            button("Increment", on_click=lambda: set_text_state(text_state + 1)),
                        ],
                        div(flex=1, background_color="333333", padding=16, border_radius=8, border_width=1, border_color="555555")[
                            code("actions.user.ui_elements_set_text"),
                            text("Direct mutation. Fast render."),
                            text("0", id="text_with_id", font_size=32, margin=16),
                            # button("Increment", on_click=lambda: text_ref.set_text(int(text_ref.text) + 1)),
                                # actions.user.ui_elements_set_text("text_with_id", lambda t: str(int(t) + 1))),
                        ],
                    ]
                ]
            ]
        ]
    ]