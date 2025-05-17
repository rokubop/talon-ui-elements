from talon import actions

def placeholder_storybook(name):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(padding=32)[
        text(f"{name} story coming soon", color="#888888")
    ]
