from talon import actions
from .actions import actions_ui

def cheatsheet_ui():
    div, screen, text, state = actions.user.ui_elements(['div', 'screen', 'text', 'state'])

    align = state.get("align", "right")
    commands = state.get("commands", [])
    background_color = state.get("background_color", "04732A")

    if align == "right":
        justify_content = "flex_end"
    else:
        justify_content = "flex_start"

    return screen(flex_direction="row", align_items="center", justify_content=justify_content)[
        div(flex_direction="row", background_color=background_color, padding=16, gap=16)[
            div()[
                text("Commands", font_weight="bold"),
                *(text(command) for command in commands)
            ],
        ]
    ]

def cheatsheet_show():
    cheatsheet_set_command_set_1()
    cheatsheet_actions()
    actions.user.ui_elements_show(cheatsheet_ui)

def cheatsheet_hide():
    actions.user.ui_elements_hide(cheatsheet_ui)

def cheatsheet_set_command_set_1():
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

def cheatsheet_set_command_set_2():
    actions.user.ui_elements_set_state("commands", [
        "up",
        "down",
        "left",
        "right",
        "jump",
        "shoot",
        "pause",
        "back",
        "sprint",
        "reload",
        "grenade",
        "crouch",
        "interact",
        "menu",
    ])

def cheatsheet_set_background_color(color):
    actions.user.ui_elements_set_state("background_color", color)

def cheatsheet_align_left():
    actions.user.ui_elements_set_state("align", "left")

def cheatsheet_align_right():
    actions.user.ui_elements_set_state("align", "right")

def cheatsheet_actions():
    actions.user.ui_elements_set_state("actions", [{
        "text": 'ui_elements_set_state("background_color", "04732A")',
        "action": lambda: actions.user.ui_elements_set_state("background_color", "04732A")
    }, {
        "text": 'ui_elements_set_state("background_color", "000000")',
        "action": lambda: actions.user.ui_elements_set_state("background_color", "000000")
    }, {
        "text": 'ui_elements_set_state("commands", commands_1)',
        "action": cheatsheet_set_command_set_1
    }, {
        "text": 'ui_elements_set_state("commands", commands_2)',
        "action": cheatsheet_set_command_set_2
    }, {
        "text": 'ui_elements_set_state("align", "left")',
        "action": cheatsheet_align_left
    }, {
        "text": 'ui_elements_set_state("align", "right")',
        "action": cheatsheet_align_right
    }])
    actions.user.ui_elements_show(actions_ui)