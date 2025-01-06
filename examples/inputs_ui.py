from talon import actions

def inputs_ui(props):
    elements = ["div", "text", "screen", "input_text", "button", "ref", "state"]
    div, text, screen, input_text, button, ref, state = actions.user.ui_elements(elements)

    is_valid, set_is_valid = state.use("is_valid", False)
    first_input = ref("first")
    last_input = ref("last")

    def on_submit(e):
        if is_valid:
            print(f"Submitted - First: {first_input.value}, Last: {last_input.value}")
            props["on_submitted"]()

    def on_change(e):
        set_is_valid(bool(first_input.value and last_input.value))

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="333333", padding=24, border_radius=12, border_width=1, gap=16)[
            div(drag_handle=True, border_bottom=1, padding_bottom=16, margin_bottom=8)[
                text("Enter your name", font_size=24),
            ],
            text("First"),
            input_text(id="first", background_color="444444", on_change=on_change),
            text("Last"),
            input_text(id="last", background_color="444444", on_change=on_change),
            div(flex_direction="row", justify_content="flex_end", margin_top=8)[
                button("Submit", on_click=on_submit, background_color="305CDE" if is_valid else "444444", border_radius=8, padding=12, padding_left=24, padding_right=24)
            ]
        ]
    ]