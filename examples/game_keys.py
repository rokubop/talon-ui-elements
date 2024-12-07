from talon import actions, app

key_css = {
    "padding": 8,
    "background_color": "333333",
    "flex_direction": "row",
    "justify_content": "center",
    "align_items": "center",
    "margin": 1,
    "width": 60,
    "height": 60,
    "opacity": 0.8,
}

def get_additional_props(text_content):
    if app.platform == "mac" and text_content in ["↑", "↓", "←", "→"]:
        return {"font_family": "symbol"}
    return {}

def key(key_name, text_content):
    div, text = actions.user.ui_elements(["div", "text"])

    extra_props = get_additional_props(text_content)

    return div(key_css, id=key_name, background_color="333333")[
        text(text_content, extra_props)
    ]

def blank_key():
    div, text = actions.user.ui_elements(["div", "text"])
    return div(key_css, opacity=0.6)[text(" ")]

def game_keys_ui():
    screen, div = actions.user.ui_elements(["screen", "div"])

    return screen(justify_content="flex_end", highlight_color="FFFFFF55")[
        div(flex_direction="row", margin_bottom=20, margin_left=20)[
            div(flex_direction="column")[
                div(flex_direction="row")[
                    blank_key(), key("up", "↑"), blank_key()
                ],
                div(flex_direction="row")[
                    key("left", "←"), key("down", "↓"), key("right", "→")
                ]
            ],
            div()[
                div(flex_direction="row")[
                    key("space", "jump"),
                    key("lmb", "LMB"),
                    key("rmb", "RMB"),
                ],
                div(flex_direction="row")[
                    key("q", "dash"),
                    key("e", "heal"),
                    key("shift", "sprint"),
                ]
            ],
        ],
    ]

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
