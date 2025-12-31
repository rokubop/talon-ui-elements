from talon import actions
from .game_keys_ui import game_keys_ui, show_game_keys, hide_game_keys
from ..actions.actions_ui import actions_ui, show_actions_ui, hide_actions_ui

sprinting = False

def unhighlight_all_dir():
    global sprinting
    for key in ["up", "down", "left", "right"]:
        actions.user.ui_elements_unhighlight(key)
    sprinting = False

def highlight_dir(dir):
    unhighlight_all_dir()
    actions.user.ui_elements_highlight(dir)

def sprint_toggle():
    global sprinting
    sprinting = not sprinting
    if sprinting:
        actions.user.ui_elements_highlight("shift")
    else:
        actions.user.ui_elements_unhighlight("shift")

def set_game_keys_actions_state():
    actions.user.ui_elements_set_state("actions", [{
        "text": 'Go left',
        "action": lambda: highlight_dir("left")
    }, {
        "text": 'Go right',
        "action": lambda: highlight_dir("right")
    }, {
        "text": 'Go up',
        "action": lambda: highlight_dir("up")
    }, {
        "text": 'Go down',
        "action": lambda: highlight_dir("down")
    }, {
        "text": 'Stop',
        "action": lambda: (unhighlight_all_dir(), actions.user.ui_elements_unhighlight("shift"))
    }, {
        "text": 'Jump',
        "action": lambda: actions.user.ui_elements_highlight_briefly("space")
    }, {
        "text": 'LMB',
        "action": lambda: actions.user.ui_elements_highlight_briefly("lmb")
    }, {
        "text": 'RMB',
        "action": lambda: actions.user.ui_elements_highlight_briefly("rmb")
    }, {
        "text": 'Dash',
        "action": lambda: actions.user.ui_elements_highlight_briefly("q")
    }, {
        "text": 'Heal',
        "action": lambda: actions.user.ui_elements_highlight_briefly("e")
    }, {
        "text": 'Sprint toggle',
        "action": sprint_toggle
    }])

def game_keys_show():
    set_game_keys_actions_state()
    show_game_keys()
    show_actions_ui()