from talon import actions

def on_submit(e):
    first = actions.user.ui_elements_get_input_value("first")
    last = actions.user.ui_elements_get_input_value("last")
    print(f"Submitted - First: {first}, Last: {last}")
    actions.user.ui_elements_hide_all()

def on_change(e):
    print(e)

def inputs_ui():
    div, text, screen, input_text, button, ref = actions.user.ui_elements(["div", "text", "screen", "input_text", "button", "ref"])

    # input_first = ref("first")
    # input_last = ref("last")
    # input_first.get("value")
    # input_last.get("value")

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=24, border_radius=12, border_width=1, gap=16)[
            div(border_bottom=1, padding_bottom=16, margin_bottom=8)[
                text("Enter your name", font_size=24),
            ],
            text("First"),
            input_text(id="first", background_color="444444", on_change=on_change),
            text("Last"),
            input_text(id="last", background_color="444444", on_change=on_change),
            div(flex_direction="row", justify_content="flex_end", margin_top=8)[
                button("Submit", on_click=on_submit, background_color="42A5F5", border_radius=8, padding=12, padding_left=24, padding_right=24)
            ]
        ]
    ]

def show_inputs_ui():
    actions.user.ui_elements_show(inputs_ui)

def hide_inputs_ui():
    actions.user.ui_elements_hide(inputs_ui)