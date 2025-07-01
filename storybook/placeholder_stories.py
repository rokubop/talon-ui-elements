from talon import actions

def placeholder_stories(name):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(padding=32)[
        text(f"{name} story coming soon", color="#888888")
    ]
