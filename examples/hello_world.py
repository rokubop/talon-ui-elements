from talon import actions

def hello_world_ui():
    div, text, screen, = actions.user.ui_elements_new(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="white", padding=16, border_radius=16, border_width=1)[
            text("Hello world", color="red", font_size=24)
        ]
    ]