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
    "opacity": 0.5,
}

def key(key_name, text_content, width=30):
    div, text = actions.user.ui_elements(["div", "text"])

    return div(key_css, id=key_name, width=width, background_color="333333")[
        text(text_content)
    ]

def blank_key():
    div, text = actions.user.ui_elements(["div", "text"])

    return div(key_css)[text(" ")]

def game_keys_ui():
    screen, div = actions.user.ui_elements(["screen", "div"])

    return screen(justify_content="flex_end", highlight_color="FFFFFF55")[
        div(flex_direction="row", margin_bottom=20, margin_left=20, opacity=0.1)[
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