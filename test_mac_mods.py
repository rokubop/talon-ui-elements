"""
Test: what modifier names does Talon report on Mac?
Press Cmd+C, Ctrl+C, Cmd+Enter, Ctrl+Enter, etc. and check the log.
Say "test mac mods" to show, "test mac mods close" to hide.
"""
from talon import Module, actions, app

mod = Module()

def test_ui():
    screen, div, text, input_text = actions.user.ui_elements(
        ["screen", "div", "text", "input_text"]
    )
    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=24, gap=16, border_radius=8)[
            text("Press modifier combos and check Talon log", font_size=16),
            text("Try: Cmd+C, Ctrl+C, Cmd+Enter, Ctrl+Enter, Alt/Option+A", font_size=12, color="999999"),
            input_text(id="test_input", autofocus=True, background_color="444444"),
        ]
    ]

@mod.action_class
class Actions:
    def test_mac_mods_show():
        """Show mac mods test UI"""
        actions.user.ui_elements_show(test_ui)

    def test_mac_mods_hide():
        """Hide mac mods test UI"""
        actions.user.ui_elements_hide(test_ui)
