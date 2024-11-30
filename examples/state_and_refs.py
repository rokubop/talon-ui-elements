from talon import actions

YELLOW = "FFCC00"
WHITE = "CCCCCC"

def code(text_str):
    text = actions.user.ui_elements(["text"])
    return text(text_str, color=YELLOW)

def state_ui():
    elements = actions.user.ui_elements(["div", "text", "state", "button"])
    div, text, state, button = elements

    # can use state.get, state.set, state.use
    # or actions.user.ui_elements_set_state
    text_state, set_text_state = state.use("text_state", 0)

    def on_increment():
        set_text_state(text_state + 1)

    return div(background_color="333333", padding=32, border_radius=8, border_width=1, border_color="555555")[
        div(flex_direction='row', justify_content="space_between", padding_bottom=16, margin_bottom=16, border_bottom=1, border_color="555555")[
            text("state", font_size=24),
        ],
        text("Global state (full rerender - slower)"),
        div(align_items="center", margin_top=8)[
            text(text_state, font_size=32, margin=16),
            button("Increment", on_click=on_increment, padding=12, border_radius=4),
        ]
    ]

def ref_ui():
    elements = actions.user.ui_elements(["div", "text", "button", "ref"])
    div, text, button, ref = elements

    # can also use ref.set("text_with_id", "text", 0)
    # or ref.set_text("text_with_id", 0)
    text_ref = ref("text_with_id")

    def on_increment():
        # same as actions.user.ui_elements_set_text
        text_ref.set_text(int(text_ref.text) + 1)

    return div(background_color="333333", padding=32, border_radius=8, border_width=1, border_color="555555")[
        div(flex_direction='row', justify_content="space_between", padding_bottom=16, margin_bottom=16, border_bottom=1, border_color="555555")[
            text("ref", font_size=24),
        ],
        text("ID specific mutation (faster)"),
        div(align_items="center", margin_top=8)[
            text("0", id="text_with_id", font_size=32, margin=16),
            button("Increment", on_click=on_increment, padding=12, border_radius=4),
        ],
    ]

def state_and_refs_ui():
    screen, div, text = actions.user.ui_elements(["screen", "div", "text"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="222222", border_width=1, border_radius=8, padding=32)[
            div(flex_direction='row', width="100%", justify_content="space_between", padding_bottom=16, border_bottom=1, border_color="555555")[
                text("state and refs", font_size=32),
                text("talon-ui-elements", font_size=32, color=YELLOW),
            ],
            div(flex_direction="row", gap=16, margin_top=32)[
                state_ui(),
                ref_ui(),
            ]
        ]
    ]