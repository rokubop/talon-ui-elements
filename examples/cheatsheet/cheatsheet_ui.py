from talon import Module, actions

mod = Module()

def cheatsheet_ui():
    div, text, screen, state = actions.user.ui_elements(["div", "text", "screen", "state"])
    table, tr, td, style = actions.user.ui_elements(["table", "tr", "td", "style"])

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

    commands = basic_commands if mode == "basic" else advanced_commands

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
            text(f"Commands ({mode})", class_name="title"),
            table()[
                *[tr()[
                    td(command, color="#FFCC00", padding_right=16),
                    td(description)
                ] for command, description in commands]
            ]
        ]
    ]

def show_cheatsheet():
    actions.user.ui_elements_show(cheatsheet_ui)

def toggle_cheatsheet():
    actions.user.ui_elements_toggle(cheatsheet_ui)

def cheatsheet_mode_basic():
    actions.user.ui_elements_set_state("mode", "basic")

def cheatsheet_mode_advanced():
    actions.user.ui_elements_set_state("mode", "advanced")
