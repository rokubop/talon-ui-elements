from talon import actions

def inputs_ui(props):
    div, text, screen, input_text = actions.user.ui_elements(["div", "text", "screen", "input_text"])
    button, ref, state, form = actions.user.ui_elements(["button", "ref", "state", "form"])

    is_valid, set_is_valid = state.use("is_valid", False)
    first_ref = ref("first")
    last_ref = ref("last")

    def on_submit(e):
        if is_valid:
            print(f"Submitted - {e.data}")
            props["on_submitted"]()

    def on_change(e):
        set_is_valid(bool(first_ref.value and last_ref.value))

    return screen(justify_content="center", align_items="center")[
        form(on_submit=on_submit, draggable=True, background_color="333333", padding=24, border_radius=12, border_width=1, gap=16)[
            div(drag_handle=True, border_bottom=1, padding_bottom=16, margin_bottom=8)[
                text("Enter your name", font_size=24),
            ],
            text("First"),
            input_text(id="first", autofocus=True, background_color="444444", on_change=on_change),
            text("Last"),
            input_text(id="last", background_color="444444", on_change=on_change),
            div(flex_direction="row", justify_content="flex_end", margin_top=8)[
                button("Submit", type="submit", background_color="305CDE" if is_valid else "444444", border_radius=8, padding=12, padding_left=24, padding_right=24)
            ]
        ]
    ]

def show_inputs(on_submitted=None):
    props = {"on_submitted": on_submitted or hide_inputs}
    actions.user.ui_elements_show(inputs_ui, props=props)

def hide_inputs():
    actions.user.ui_elements_hide(inputs_ui)

def toggle_inputs():
    actions.user.ui_elements_toggle(inputs_ui)
