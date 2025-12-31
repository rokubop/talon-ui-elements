# cheatsheet_ui.py
from talon import Module, actions

mod = Module()

def cheatsheet_ui():
    div, text, screen, state = actions.user.ui_elements(["div", "text", "screen", "state"])
    table, tr, td, style = actions.user.ui_elements(["table", "tr", "td", "style"])

    # Get or create state to track which command set to show
    mode = state.get("mode", "basic")

    basic_commands = [
        ("up", "Move forward"),
        ("down", "Move backward"),
        ("left", "Move left"),
        ("right", "Move right"),
        ("jump", "Jump"),
        ("shoot", "Fire weapon"),
        ("pause", "Pause game")
    ]

    advanced_commands = [
        ("sprint", "Run faster"),
        ("crouch", "Duck down"),
        ("reload", "Reload weapon"),
        ("switch weapon", "Change weapon"),
        ("use item", "Use inventory item")
    ]

    # Choose commands based on mode
    commands = basic_commands if mode == "basic" else advanced_commands

    # Apply styles to all td elements and title
    style({
        "td": {
            "padding": 8
        },
        ".title": {
            "color": "#FFCC00",
            "font_weight": "bold",
            "padding_bottom": 8,
            "border_bottom": 1,
            "border_color": "#FFCC00"
        }
    })

    return screen(flex_direction="row", justify_content="flex_end", align_items="center")[
        div(
            draggable=True,
            opacity=0.7,
            background_color="#333333",
            padding=16,
            margin=16,
            border_radius=8,
            gap=8
        )[
            # Title
            text(f"Commands ({mode})", class_name="title"),

            # Table with commands
            table()[
                *[tr()[
                    td(command, color="#FFCC00", padding_right=16),
                    td(description)
                ] for command, description in commands]
            ]
        ]
    ]

@mod.action_class
class Actions:
    def toggle_cheatsheet():
        """Toggle command cheatsheet"""
        actions.user.ui_elements_toggle(cheatsheet_ui)

    def cheatsheet_mode_basic():
        """Set cheatsheet to basic mode"""
        actions.user.ui_elements_set_state("mode", "basic")

    def cheatsheet_mode_advanced():
        """Set cheatsheet to advanced mode"""
        actions.user.ui_elements_set_state("mode", "advanced")