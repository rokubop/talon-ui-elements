from talon import actions
from .actions_ui import actions_ui
from .cheatsheet_ui import cheatsheet_ui

def cheatsheet_show():
    cheatsheet_set_commands_1()
    cheatsheet_actions()
    actions.user.ui_elements_show(cheatsheet_ui)

def cheatsheet_hide():
    actions.user.ui_elements_hide(cheatsheet_ui)

def cheatsheet_set_commands_1():
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

def cheatsheet_set_commands_2():
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
        "text": 'actions.user.ui_elements_set_property("cheatsheet", "background_color", "1434A499")',
        "action": lambda: actions.user.ui_elements_set_property("cheatsheet", "background_color", "1434A499")
    }, {
        "text": 'actions.user.ui_elements_set_property("cheatsheet", "background_color", "33333399")',
        "action": lambda: actions.user.ui_elements_set_property("cheatsheet", "background_color", "33333399")
    }, {
        "text": 'actions.user.ui_elements_set_state("commands", commands_2)',
        "action": cheatsheet_set_commands_2
    }, {
        "text": 'actions.user.ui_elements_set_state("commands", commands_1)',
        "action": cheatsheet_set_commands_1
    }, {
        "text": 'actions.user.ui_elements_set_state("align", "left")',
        "action": cheatsheet_align_left
    }, {
        "text": 'actions.user.ui_elements_set_state("align", "right")',
        "action": cheatsheet_align_right
    }])
    actions.user.ui_elements_show(actions_ui)