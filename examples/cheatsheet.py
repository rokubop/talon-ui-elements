from talon import actions
from .actions import actions_ui

def on_mount():
    print("hello mount")

def on_unmount():
    print("hello unmount")

def cheatsheet_ui():
    div, screen, text, state, effect = actions.user.ui_elements(['div', 'screen', 'text', 'state', 'effect'])

    align = state.get("align", "right")
    commands = state.get("commands", [])
    background_color = state.get("background_color", "456456")

    effect(on_mount, on_unmount, [])

    if align == "right":
        justify_content = "flex_end"
    else:
        justify_content = "flex_start"

    return screen(flex_direction="row", align_items="center", justify_content=justify_content)[
        div(flex_direction="row", opacity=0.7, background_color=background_color, padding=16, gap=16)[
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
        "text": 'actions.user.ui_elements_set_state("background_color", "456456")',
        "action": lambda: actions.user.ui_elements_set_state("background_color", "456456")
    }, {
        "text": 'actions.user.ui_elements_set_state("background_color", "333333")',
        "action": lambda: actions.user.ui_elements_set_state("background_color", "333333")
    }, {
        "text": 'actions.user.ui_elements_set_state("commands", commands_1)',
        "action": cheatsheet_set_command_set_1
    }, {
        "text": 'actions.user.ui_elements_set_state("commands", commands_2)',
        "action": cheatsheet_set_command_set_2
    }, {
        "text": 'actions.user.ui_elements_set_state("align", "left")',
        "action": cheatsheet_align_left
    }, {
        "text": 'actions.user.ui_elements_set_state("align", "right")',
        "action": cheatsheet_align_right
    }])
    actions.user.ui_elements_show(actions_ui)