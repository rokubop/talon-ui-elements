from talon import actions
from .elements.button import button_stories
from .elements.link import link_stories
from .elements.table import table_stories
from .elements.checkbox import checkbox_stories
from .elements.input_text import input_text_stories
from .placeholder_stories import placeholder_stories
from . import theme as t

elements = [
    "active_window",
    "button",
    "checkbox",
    "component",
    "div",
    "effect",
    "icon",
    "input_text",
    "link",
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
    "button": button_stories,
    # Placeholders for other elements
    "active_window": lambda: placeholder_stories("active_window"),
    "checkbox": checkbox_stories,
    "component": lambda: placeholder_stories("component"),
    "div": lambda: placeholder_stories("div"),
    "effect": lambda: placeholder_stories("effect"),
    "icon": lambda: placeholder_stories("icon"),
    "input_text": input_text_stories,
    "link": link_stories,
    "ref": lambda: placeholder_stories("ref"),
    "screen": lambda: placeholder_stories("screen"),
    "state": lambda: placeholder_stories("state"),
    "table": table_stories,
    "td": table_stories,
    "text": lambda: placeholder_stories("text"),
    "th": table_stories,
    "tr": table_stories,
    "window": lambda: placeholder_stories("window"),
}

def sidebar():
    div, text, icon, button = actions.user.ui_elements(["div", "text", "icon", "button"])
    state = actions.user.ui_elements(["state"])

    page, set_page = state.use("page", "button")

    return div(
        min_width=180,
        background_color=t.BG,
        color=t.TEXT,
        border_right=1,
        border_color=t.BORDER,
        height="100%",
        overflow_y="scroll",
    )[
        button(flex_direction="row", border_bottom=1, border_color=t.BORDER, padding=12, gap=8)[
            icon("chevron_down", size=18, color=t.TEXT_MUTED),
            text("Elements", font_weight="bold", font_size=16, color=t.TEXT),
        ],
        div(padding=8, gap=4, flex_direction="column")[
            *[button(
                text=element,
                background_color=t.BG_ACTIVE if page == element else None,
                on_click=lambda e, page=element: set_page(page),
                color=t.TEXT_SECONDARY,
                border_radius=6,
                padding=12,
                padding_top=8,
                padding_bottom=8,
                highlight_color=t.HIGHLIGHT,
                font_size=14) for element in elements]
        ],
    ]

def main_content():
    div, text = actions.user.ui_elements(["div", "text"])
    state = actions.user.ui_elements(["state"])

    page = state.get("page")

    page_fn = storybook_pages.get(page, lambda: div(padding=32)[text(f"No story for {page}", color=t.TEXT_MUTED)])
    return div(height="100%", overflow_y="scroll", width="100%")[
        page_fn()
    ]

def storybook_ui():
    screen, window, div, component = actions.user.ui_elements(["screen", "window", "div", "component"])

    return screen(align_items="center", justify_content="center")[
        window(title="UI Elements Storybook", width=1200, height=800, background_color=t.BG)[
            div(flex_direction="row", height="100%")[
                component(sidebar),
                component(main_content)
            ]
        ]
    ]

def show_storybook():
    actions.user.ui_elements_show(storybook_ui)

def hide_storybook():
    actions.user.ui_elements_hide(storybook_ui)

def toggle_storybook():
    actions.user.ui_elements_toggle(storybook_ui)
