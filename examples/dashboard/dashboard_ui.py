from talon import actions, registry

def get_user_list(current_user_list):
    try:
        return registry.lists[f"user.{current_user_list}"][0]
    except KeyError:
        return { "No list found": "No values available" }

USER_LIST = [
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


def body():
    div, text, style = actions.user.ui_elements(["div", "text", "style"])
    table, tr, td = actions.user.ui_elements(["table", "tr", "td"])
    state = actions.user.ui_elements(["state"])

    current_user_list = state.get("current_user_list", USER_LIST[0])
    key_vals = get_user_list(current_user_list)

    style({
        "td": {
            "padding": 8,
        }
    })

    return div(padding=24, gap=8, overflow_y="scroll", width="100%", height="100%")[
        text(current_user_list, font_size=20, margin_bottom=12),
        table()[
            *[tr()[
                td(key),
                td(value)
            ] for key, value in key_vals.items()]
        ],
    ]



def sidebar():
    div, button, state = actions.user.ui_elements(["div", "button", "state"])

    return div(border_right=1, overflow_y="scroll", height="100%", padding=12)[
        *[button(
            name,
            on_click=lambda e, name=name: state.set("current_user_list", name),
            padding=16,
            padding_top=8,
            padding_bottom=8,
            border_radius=4,
        ) for name in USER_LIST]
    ]

def minimized_body():
    return body()

def dashboard_ui():
    """Main UI for dashboard"""
    window, screen = actions.user.ui_elements(["window", "screen"])

    return screen(justify_content="center", align_items="center")[
        window(
            title="Dashboard",
            width=1100,
            min_width=600,
            max_width=1200,
            min_height=400,
            max_height=800,
            height=700,
            flex_direction="row",
            resizable=True,
            minimized_body=minimized_body,
            minimized_style={
                "max_height": 400,
                "min_width": 200,
                "position": "absolute",
                "top": 100,
                "right": 100
            }
        )[
            sidebar(),
            body(),
        ]
    ]

def show_dashboard():
    actions.user.ui_elements_show(dashboard_ui)

def hide_dashboard():
    actions.user.ui_elements_hide(dashboard_ui)

def toggle_dashboard():
    actions.user.ui_elements_toggle(dashboard_ui)