from talon import actions, clip, cron
from typing import Any

def code(code_str: str) -> str:
    div, text = actions.user.ui_elements(["div", "text"])
    component = actions.user.ui_elements(["component"])

    return div(
            background_color="#0E0E10",
            border_radius=8,
            padding=24,
            color="#A0A0A0",
            font_size=14,
            position="relative",
        )[
            text(code_str, font_family="monospace"),
            div(position="absolute", right=0, top=0)[
                component(copy_button, props={
                    "code": code_str
                })
            ]
        ]

def copy_button(props):
    button, icon, state = actions.user.ui_elements(["button", "icon", "state"])
    copied, set_copied = state.use_local(False)

    return button(
        on_click=lambda: (
            clip.set_text(props["code"]),
            set_copied(True),
            cron.after("2s", lambda: set_copied(False))
        ),
        padding=8,
        border_radius=8,
        color="#CCCCCC",
    )[
        icon(
            "check" if copied else "copy",
            color="#55E055" if copied else "#CCCCCC",
            size=20,
        ),
    ]

def example_with_code(props):
    state, div, text = actions.user.ui_elements(["state", "div", "text"])
    button, component = actions.user.ui_elements(["button", "component"])
    show_code, set_show_code = state.use_local(False)

    return div(gap=8, flex_direction="column")[
        text(props["title"], font_size=18, font_weight="bold", color="#F1F1F1"),
        div(border_radius=8, border_width=1, flex=1, position="relative", margin_top=8)[
            div(padding=16, min_height=100, align_items="center", justify_content="center")[
                props["example"],
            ],
            div(position="absolute", right=0, bottom=0)[
                button(
                    "Hide code" if show_code else "Show code",
                    on_click=lambda: set_show_code(not show_code),
                    padding=8,
                    border_radius=4,
                    border_width=1,
                    background_color="#1F1F1F",
                    color="#A0A0A0",
                    font_size=12,
                ),
            ],
        ],
        code(props["code"]) if show_code else None,
    ]