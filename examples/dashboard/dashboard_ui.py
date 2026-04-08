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
    div, text, data_table = actions.user.ui_elements(["div", "text", "data_table"])
    state = actions.user.ui_elements(["state"])

    current_user_list = state.get("current_user_list", USER_LIST[0])
    key_vals = get_user_list(current_user_list)

    data = [{"key": k, "value": v} for k, v in key_vals.items()]

    return div(padding=24, gap=8, width="100%", height="100%")[
        text(current_user_list, font_size=20, margin_bottom=12),
        data_table(
            id="dashboard_table",
            columns=[
                {"key": "key", "label": "Key", "sortable": True, "width": 250},
                {"key": "value", "label": "Value", "sortable": True},
            ],
            data=data,
            sort_key="key",
            body_height="100%",
        ),
    ]



def sidebar():
    div, button, state = actions.user.ui_elements(["div", "button", "state"])

    return div(id="sidebar", border_right=1, overflow_y="scroll", height="100%",
                padding=12, resizable="right", min_width=100, max_width=400)[
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