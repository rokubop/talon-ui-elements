from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="#333333", padding=16, border_radius=8, border_width=1)[
            text("Hello world", color="#FFFFFF", font_size=24)
        ]
    ]

def show_hello_world():
    actions.user.ui_elements_show(hello_world_ui)

def hide_hello_world():
    actions.user.ui_elements_hide(hello_world_ui)

def toggle_hello_world():
    actions.user.ui_elements_toggle(hello_world_ui)