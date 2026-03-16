from talon import actions
from . import theme as t

def placeholder_stories(name):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(padding=32)[
        text(f"{name} story coming soon", color=t.TEXT_MUTED)
    ]
