from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements_new(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=16, border_width=1, border_color="red")[
            text("Hello world", color="FFFFFF", font_size=24)
        ]
    ]