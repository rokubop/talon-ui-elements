from talon import actions

elements = [
    "active_window",
    "button",
    "checkbox",
    "component",
    "div",
    "effect",
    "icon",
    "input_text",
    "ref",
    "screen",
    "state",
    "table",
    "td",
    "text",
    "th",
    "tr",
    "window"
]

def sidebar():
    div, text, icon, button = actions.user.ui_elements(["div", "text", "icon", "button"])
    state = actions.user.ui_elements(["state"])

    page, set_page = state.use("page", "button")

    return div(
        min_width=180,
        background_color="#181A20",
        color="#F1F1F1",
        # height="100vh",
        border_right=1,
        border_color="#23242A",
        # box_shadow="2px 0 8px #0008"
    )[
        button(flex_direction="row", border_bottom=1, border_color="#23242A", padding=12, gap=8)[
            icon("chevron_down", size=18, color="#A0A0A0"),
            text("Elements", font_weight="bold", font_size=16, color="#F1F1F1"),
        ],
        div(padding=8, gap=4, flex_direction="column")[
            *[button(
                text=element,
                background_color="#23242A" if page == element else None,
                on_click=lambda e, page=element: set_page(page),
                color="#F1F1F1",
                border_radius=6,
                padding=12,
                padding_top=8,
                padding_bottom=8,
                highlight_color="#31323A33",
                font_size=14) for element in elements]
        ],
    ]

def main_content():
    div, text = actions.user.ui_elements(["div", "text"])
    state = actions.user.ui_elements(["state"])

    page = state.get("page")

    return div(
        padding=32,
        min_width=500,
        # background_color="#23242A",
        color="#F1F1F1",
        # border_radius=12,
        margin=16,
        # box_shadow="0 2px 16px #0006"
    )[
        text(page, font_size=20, font_weight="bold", color="#F1F1F1"),
    ]

def storybook_ui():
    screen, window, div, component = actions.user.ui_elements(["screen", "window", "div", "component"])

    return screen(
        # background_color="#15161A",
        align_items="center",
        justify_content="center",
        # min_height="100vh"
    )[
        window()[
            div(flex_direction="row", background_color="#181A20")[
                component(sidebar),
                component(main_content)
            ]
        ]
    ]
