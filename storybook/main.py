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

    return div(min_width=150)[
        div(flex_direction="row", border=1, padding=12, gap=8)[
            icon("chevron_down", size=16),
            text("Elements"),
        ],
        div(padding=12)[
            *[button(e) for e in elements]
        ],
        # div(flex_direction="row", border=1, padding=12, gap=8)[
        #     icon("chevron_down", size=16),
        #     text("Properties"),
        # ],
        # div(flex_direction="row", border=1, padding=12, gap=8)[
        #     icon("chevron_down", size=16),
        #     text("Examples"),
        # ]
    ]

def main_content():
    div, text = actions.user.ui_elements(["div", "text"])

    return div(padding=16, min_width=500)[
        text("Main Content"),
    ]

def storybook_ui():
    screen, window, div, component = actions.user.ui_elements(["screen", "window", "div", "component"])

    return screen(align_items="center", justify_content="center")[
        window()[
            div(flex_direction="row")[
                component(sidebar),
                component(main_content)
            ]
        ]
    ]
