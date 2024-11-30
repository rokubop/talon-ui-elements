from talon import actions

def actions_ui():
    elements = actions.user.ui_elements(["div", "screen", "text", "state", "button"])
    div, screen, text, state, button = elements

    ui_actions = state.get("actions", [])

    return screen(flex_direction="row", align_items="center", justify_content="flex_start")[
        div(flex_direction="column", background_color="333333", padding=16, gap=16)[
            text("Actions", font_weight="bold"),
            *(button(action["text"], on_click=action["action"], padding=12, border_radius=4, font_size=14) for action in ui_actions)
        ]
    ]

def show_actions_ui():
    actions.user.ui_elements_show(actions_ui)