from talon import actions, registry

def format_user_list(user_list):
    try:
        talon_list = registry.lists[f"user.{user_list}"][0]
    except KeyError:
        return (["No list found"], ["No list found"])
    return (talon_list.keys(), talon_list.values())

user_lists = [
    "arrow_key",
    "code_formatter",
    "cursorless_scope_type",
    "cursorless_simple_action",
    "edit_action",
    "edit_modifier",
    "emoji",
    "emoticon",
    "function_key",
    "kaomoji",
    "keypad_key",
    "letter",
    "modifier_key",
    "mouse_click",
    "number_key",
    "phrase_ender",
    "prose_formatter",
    "punctuation",
    "reformatter",
    "special_key",
    "symbol_key",
    "system_paths",
    "vocabulary",
    "website",
    "window_snap_positions",
    "word_formatter",
]

def dashboard_ui():
    window, screen, div, text = actions.user.ui_elements(["window", "screen", "div", "text"])
    button, state, icon = actions.user.ui_elements(["button", "state", "icon"])

    user_list, set_user_list = state.use("user_list", user_lists[0])
    keys, values = format_user_list(user_list)

    def sidebar():
        return div(border_right=1, overflow_y="scroll", padding=8)[
            *[button(
                name,
                on_click=lambda e, name=name: set_user_list(name),
                padding=16,
                padding_top=8,
                padding_bottom=8,
                border_radius=4,
            ) for name in user_lists]
        ]

    def body():
        return div(flex_direction="row", id="body", padding=16, gap=8, overflow_y="scroll", width="100%")[
            div()[
                *[text(key, font_size=14) for key in keys]
            ],
            div()[
                *[text(value, font_size=14) for value in values]
            ]
        ]

    return screen(justify_content="center", align_items="center")[
        window(title="Dashboard", min_width=1000, max_height=1000,flex_direction="row")[
            sidebar(),
            body()
        ]
    ]

def show_dashboard_ui():
    actions.user.ui_elements_show(dashboard_ui)

def hide_dashboard_ui():
    actions.user.ui_elements_hide(dashboard_ui)