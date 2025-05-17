from talon import actions
from .elements.button import button_storybook
from .placeholder_storybook import placeholder_storybook

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

storybook_pages = {
    "button": button_storybook,
    # Placeholders for other elements
    "active_window": lambda: placeholder_storybook("active_window"),
    "checkbox": lambda: placeholder_storybook("checkbox"),
    "component": lambda: placeholder_storybook("component"),
    "div": lambda: placeholder_storybook("div"),
    "effect": lambda: placeholder_storybook("effect"),
    "icon": lambda: placeholder_storybook("icon"),
    "input_text": lambda: placeholder_storybook("input_text"),
    "ref": lambda: placeholder_storybook("ref"),
    "screen": lambda: placeholder_storybook("screen"),
    "state": lambda: placeholder_storybook("state"),
    "table": lambda: placeholder_storybook("table"),
    "td": lambda: placeholder_storybook("td"),
    "text": lambda: placeholder_storybook("text"),
    "th": lambda: placeholder_storybook("th"),
    "tr": lambda: placeholder_storybook("tr"),
    "window": lambda: placeholder_storybook("window"),
}

def sidebar():
    div, text, icon, button = actions.user.ui_elements(["div", "text", "icon", "button"])
    state = actions.user.ui_elements(["state"])

    page, set_page = state.use("page", "button")

    return div(
        min_width=180,
        background_color="#181A20",
        color="#F1F1F1",
        border_right=1,
        border_color="#23242A",
        height="100%",
        overflow_y="scroll",
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

    page_fn = storybook_pages.get(page, lambda: div(padding=32)[text(f"No story for {page}", color="#888888")])
    return div(height="100%", overflow_y="scroll")[
        page_fn()
    ]

def storybook_ui():
    screen, window, div, component = actions.user.ui_elements(["screen", "window", "div", "component"])

    return screen(
        # background_color="#15161A",
        align_items="center",
        justify_content="center",
        # min_height="100vh"
    )[
        window(title="UI Elements Storybook", width=1200, height=800, background_color="#181A20")[
            div(flex_direction="row", height="100%")[
                component(sidebar),
                component(main_content)
            ]
        ]
    ]
