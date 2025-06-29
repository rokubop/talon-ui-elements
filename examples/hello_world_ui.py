from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])
    state, button, icon = actions.user.ui_elements(["state", "button", "icon"])

    color, set_color = state.use("color", "#000000")

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="333333", padding=16, border_radius=8, border_width=1)[
            button("Change Color", on_click=lambda: set_color("#FF0000" if color == "#000000" else "#000000")),
            *[icon("close", color=color) for _ in range(30)]
        ]
    ]