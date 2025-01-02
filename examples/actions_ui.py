from talon import actions

def actions_ui():
    """
    Display buttons to perform actions on the UI elements for testing.
    Expects state to be set such as:

    ```
    actions.user.ui_elements_set_state("actions", [{
        "text": 'Set background Color: 456456',
        "action": lambda: actions.user.ui_elements_set_state("background_color", "456456")
    }, {
        "text": 'Set background Color: 333333',
        "action": lambda: actions.user.ui_elements_set_state("background_color", "333333")
    }])
    """
    elements = actions.user.ui_elements(["div", "screen", "text", "state", "button"])
    div, screen, text, state, button = elements

    ui_actions = state.get("actions", [])

    return screen(flex_direction="row", align_items="center", justify_content="center")[
        div(draggable=True, flex_direction="column", background_color="333333", min_width=200, border_radius=8, border_width=1, padding_bottom=16)[
            text("Actions", drag_handle=True, font_weight="bold", color="FFCC00", padding=16),
            *[button(action["text"], on_click=action["action"], padding=12, border_radius=4) for action in ui_actions]
        ]
    ]