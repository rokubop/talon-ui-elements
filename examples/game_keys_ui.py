from talon import actions, app

key_style = {
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

def get_additional_props(display: str):
    """Mac shows squares for these if we use the default font"""
    if app.platform == "mac" and display in ["↑", "↓", "←", "→"]:
        return {"font_family": "symbol"}
    return {}

def key(id, display: str):
    div, text = actions.user.ui_elements(["div", "text"])

    extra_props = get_additional_props(display)

    return div(key_style, id=id)[
        text(display, extra_props)
    ]

def blank_key():
    div, text = actions.user.ui_elements(["div", "text"])
    return div(key_style, opacity=0.6)[text(" ")]

def game_keys_ui():
    """
    Keys (just a div with text) should have an id and a display value.
    Anything with an id is able to be targeted by ui_elements_highlight,
    ui_elements_unhighlight, ui_elements_highlight_briefly
    """
    screen, div = actions.user.ui_elements(["screen", "div"])

    return screen(justify_content="flex_end")[
        div(flex_direction="row", margin_bottom=20, margin_left=20)[
            div()[
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
