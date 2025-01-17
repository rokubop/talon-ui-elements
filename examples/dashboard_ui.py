from talon import actions, registry

def format_user_list(user_list):
    try:
        talon_list = registry.lists[user_list][0]
    except KeyError:
        return (["No list found"], ["No list found"])
    return (talon_list.keys(), talon_list.values())

user_lists = [
    "user.letter",
    "user.symbol_key",
    "user.code_formatter",
    "user.modifier_key",
    "user.reformatter",
]

def dashboard_ui():
    elements = ["div", "text", "screen", "button", "state", "ref", "icon"]
    div, text, screen, button, state, ref, icon = actions.user.ui_elements(elements)

    user_list, set_user_list = state.use("user_list", user_lists[0])
    body_ref = ref("body")

    keys, values = format_user_list(user_list)

    def get_on_click(list_name):
        # wraps the click handler to avoid closure issues in the loop
        return lambda e: (
            set_user_list(list_name),
            body_ref.scroll_to(0, 0)
        )

    def header():
        return div(flex_direction='row', justify_content='space_between', border_bottom=1, border_color="555555")[
            text("Dashboard", font_size=24, padding=16),
            button(on_click=actions.user.ui_elements_hide_all)[
                icon("close", size=20, padding=6),
            ],
        ]

    def sidebar():
        return div(border_right=1, overflow_y="scroll")[
            *[button(name, on_click=get_on_click(name), padding=16, padding_top=8, padding_bottom=8) for name in user_lists]
        ]

    def body():
        return div(flex_direction="row", id="body", padding=16, gap=8, overflow_y="scroll", width="100%")[
            div(id="keys")[*[text(key, font_size=14) for key in keys]],
            div(id="values")[*[text(value, font_size=14) for value in values]]
        ]

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="272727", border_radius=8, width=900, min_height=400, max_height=500, border_width=1)[
            header(),
            div(flex_direction="row", height="100%")[
                sidebar(),
                body()
            ],
        ]
    ]

def show_dashboard_ui():
    actions.user.ui_elements_show(dashboard_ui)

def hide_dashboard_ui():
    actions.user.ui_elements_hide(dashboard_ui)