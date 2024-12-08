from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=8, border_width=1)[
            text("Hello world", font_size=24)
        ]
    ]