from talon import actions
from .store import store

accent_color = "1bd0f5"

def key_val_state(key, value, level=0):
    div, text = actions.user.ui_elements(["div", "text"])

    if isinstance(value, dict):
        return div(flex_direction="column", gap=8)[
            text("  " * level + str(key), font_size=14, color=accent_color),
            div(flex_direction="column", gap=8)[
                *[key_val_state(k, v, level + 1) for k, v in value.items()]
            ]
        ]
    elif isinstance(value, list):
        return div(flex_direction="column", gap=8)[
            text("  " * level + str(key), font_size=14, color=accent_color),
            div(flex_direction="column", gap=8)[
                *[key_val_state(k, v, level + 1) for k, v in enumerate(value)]
            ]
        ]
    else:
        return div(flex_direction="row", align_items="flex_start", gap=8)[
            text("  " * level + str(key), font_size=14, color=accent_color),
            text(str(value), font_size=14)
        ]

def dev_tools():
    """
    This function is a placeholder for development tools.
    It currently does not perform any operations.
    """
    screen, div, text, icon = actions.user.ui_elements(["screen", "div", "text", "icon"])

    # print("state", store.reactive_state)

    for key, s in store.reactive_state.items():
        print(key, s.value)

    return screen()[
        div(draggable=True, background_color="333333", border_width=1, padding=16)[
            text("Dev Tools", color="FFFFFF", margin_bottom=16),
            div(flex_direction="row", align_items="center", gap=8, margin_bottom=8)[
                icon("chevron_down", size=16, color="FFFFFF"),
                text("State", color="FFFFFF"),
            ],
            div(flex_direction="column", gap=8)[
                *[key_val_state(k, s.value) for k, s in store.reactive_state.items()]
            ],

        ]
    ]