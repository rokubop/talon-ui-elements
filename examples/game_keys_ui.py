from talon import actions

def key(id, display: str):
    div, text = actions.user.ui_elements(["div", "text"])

    return div(class_name="key", id=id)[
        text(display)
    ]

def blank_key():
    div, text = actions.user.ui_elements(["div", "text"])
    return div(class_name="key", opacity=0.6)[text(" ")]

def key_icon(id, icon_name):
    div, icon = actions.user.ui_elements(["div", "icon"])

    return div(class_name="key", id=id)[
        icon(icon_name, fill="FFFFFF", stroke="000000", stroke_width=3, size=30)
    ]

def game_keys_ui():
    screen, div, style = actions.user.ui_elements(["screen", "div", "style"])

    style({
        "text": {
            "stroke_color": "000000",
            "stroke_width": 4
        },
        ".key":  {
            "padding": 8,
            "background_color": "#33333366",
            "flex_direction": "row",
            "justify_content": "center",
            "align_items": "center",
            "margin": 1,
            "width": 60,
            "height": 60,
            "opacity": 0.8,
            "highlight_style": {
                "background_color": "#44BCE799",
            },
        }
    })

    return screen(justify_content="flex_end")[
        div(flex_direction="row", margin_bottom=20, margin_left=20)[
            div()[
                div(flex_direction="row")[
                    blank_key(), key_icon("up", "arrow_up"), blank_key()
                ],
                div(flex_direction="row")[
                    key_icon("left", "arrow_left"), key_icon("down", "arrow_down"), key_icon("right", "arrow_right")
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
