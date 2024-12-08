from talon import actions, registry

def format_user_list(user_list):
    talon_list = registry.lists[user_list][0]
    return (talon_list.keys(), talon_list.values())

user_lists = [
    "user.letter",
    "user.symbol_key",
    "user.formatters",
    "user.modifier_key",
]

def dashboard_ui():
    div, text, screen, button, state = actions.user.ui_elements(["div", "text", "screen", "button", "state"])

    user_list, set_user_list = state.use("user_list", user_lists[0])

    (keys, values) = format_user_list(user_list)

    def on_click(list_name):
        # wraps the click handler to avoid closure issues in the loop
        return lambda e: set_user_list(list_name)

    return screen(justify_content="center", align_items="center")[
        div(background_color="272727", border_radius=8, width=900, min_height=400, border_width=1)[
            div(flex_direction='row', justify_content="space_between", padding=16, border_bottom=1, border_color="555555")[
                text("Dashboard", font_size=24),
                text("talon-ui-elements", font_size=24, color="FFCC00"),
            ],
            div(flex_direction="row", height="100%")[
                div(width=150, border_right=1)[
                    *[button(name, on_click=on_click(name), padding=16, padding_top=8, padding_bottom=8) for name in user_lists]
                ],
                div(flex_direction="row", padding=16, gap=8)[
                    div()[
                        *[text(key, font_size=14) for key in keys]
                    ],
                    div()[
                        *[text(value, font_size=14) for value in values]
                    ]
                ]
            ],
        ]
    ]

def show_dashboard_ui():
    actions.user.ui_elements_show(dashboard_ui)

def hide_dashboard_ui():
    actions.user.ui_elements_hide(dashboard_ui)