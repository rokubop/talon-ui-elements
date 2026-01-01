from talon import Module, actions

mod = Module()

def game_keys_ui():
    screen, div, text, style = actions.user.ui_elements(["screen", "div", "text", "style"])

    style({
        ".key": {
            "padding": 8,
            "background_color": "#333333",
            "margin": 1,
            "width": 60,
            "height": 60,
            "justify_content": "center",
            "align_items": "center",
            "highlight_style": {
                "background_color": "#44BCE7",
            }
        }
    })

    return screen(justify_content="flex_end")[
        div(flex_direction="row", margin=20)[
            # Arrow keys section
            div()[
                div(flex_direction="row")[
                    div(class_name="key")[text(" ")],
                    div(class_name="key", id="up")[text("up")],
                    div(class_name="key")[text(" ")]
                ],
                div(flex_direction="row")[
                    div(class_name="key", id="left")[text("left")],
                    div(class_name="key", id="down")[text("down")],
                    div(class_name="key", id="right")[text("right")]
                ]
            ],
            # Action keys section
            div()[
                div(flex_direction="row")[
                    div(class_name="key", id="space")[text("jump")],
                    div(class_name="key", id="lmb")[text("LMB")],
                    div(class_name="key", id="rmb")[text("RMB")],
                ],
                div(flex_direction="row")[
                    div(class_name="key", id="q")[text("dash")],
                    div(class_name="key", id="e")[text("heal")],
                    div(class_name="key", id="shift")[text("sprint")],
                ]
            ]
        ]
    ]

@mod.action_class
class Actions:
    def toggle_game_keys():
        """Toggle game key overlay"""
        actions.user.ui_elements_toggle(game_keys_ui)