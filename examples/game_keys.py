from talon import actions

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

def key(key_name, text_content, width=30):
    div, text = actions.user.ui_elements(["div", "text"])

    return div(key_css, id=key_name, width=width, background_color="333333")[
        text(text_content)
    ]

def blank_key():
    div, text = actions.user.ui_elements(["div", "text"])

    return div(key_css, opacity=0.5)[text(" ")]

def game_keys_ui():
    screen, div = actions.user.ui_elements(["screen", "div"])

    return screen(justify_content="flex_end", highlight_color="FFFFFF55")[
        div(flex_direction="row", margin_bottom=20, margin_left=20)[
            div(flex_direction="column")[
                div(flex_direction="row")[
                    blank_key(), key("up", "↑", 60), blank_key()
                ],
                div(flex_direction="row")[
                    key("left", "←", 60), key("down", "↓", 60), key("right", "→", 60)
                ]
            ],
            div()[
                div(flex_direction="row")[
                    key("c", "jump", 60),
                    key("p", "jump 2", 60),
                    key("foot_left", "foot1: grab", 60),
                ],
                div(flex_direction="row")[
                    key("x", "dash", 60),
                    key("t", "demo", 60),
                    key("foot_center", "foot2: move", 60)
                ]
            ],
        ],
    ]

def unhighlight_all_dir():
    for key in ["up", "down", "left", "right"]:
        actions.user.ui_elements_unhighlight(key)

def highlight_dir(dir):
    unhighlight_all_dir()
    actions.user.ui_elements_highlight(dir)

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
        "action": lambda: unhighlight_all_dir()
    }, {
        "text": 'Jump',
        "action": lambda: actions.user.ui_elements_highlight_briefly("c")
    }, {
        "text": 'Jump 2',
        "action": lambda: actions.user.ui_elements_highlight_briefly("p")
    }, {
        "text": 'Foot 1',
        "action": lambda: actions.user.ui_elements_highlight_briefly("foot_left")
    }, {
        "text": 'Dash',
        "action": lambda: actions.user.ui_elements_highlight_briefly("x")
    }, {
        "text": 'Demo',
        "action": lambda: actions.user.ui_elements_highlight_briefly("t")
    }, {
        "text": 'Foot 2',
        "action": lambda: actions.user.ui_elements_highlight_briefly("foot_center")
    }])