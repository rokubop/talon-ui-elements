from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="#2AFF23", padding=2, border_radius=32, border_width=1)[
            div(background_color="#FF0000", padding=12)[
                text("Hello world", color="#FFFFFF", font_size=24)
            ]
        ]
    ]