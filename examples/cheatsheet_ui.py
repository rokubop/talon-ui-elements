from talon import actions

def cheatsheet_ui():
    """
    Commands dynamically set with:
    ```
    actions.user.ui_elements_set_state("commands", [
        "up",
        "down",
        "left",
        "right",
        "jump",
        "shoot",
        "pause",
        "back",
    ])
    ```
    """
    div, screen, text, state = actions.user.ui_elements(['div', 'screen', 'text', 'state'])

    # `state` is not necessary unless you want it to be dynamic
    align = state.get("align", "right")
    commands = state.get("commands", [])
    justify_content = "flex_end" if align == "right" else "flex_start"

    return screen(flex_direction="row", align_items="center", justify_content=justify_content)[
        div(id="cheatsheet", flex_direction="column", opacity=0.7, background_color="333333", padding=16, gap=16)[
            text("Commands", font_weight="bold"),
            *[text(command) for command in commands]
        ]
    ]
