from talon import actions
from .alignment import alignment_ui
from .cheatsheet import cheatsheet_ui
from .dashboard import dashboard_ui
from .inputs import inputs_ui
from .game_keys import game_keys_ui
from .tabs import tabs_ui
from .todo_list import todo_list_ui

button_action = {
    "alignment": lambda: actions.user.ui_elements_show(alignment_ui),
    "cheatsheet": lambda: actions.user.ui_elements_show(cheatsheet_ui),
    "dashboard": lambda: actions.user.ui_elements_show(dashboard_ui),
    "inputs": lambda: actions.user.ui_elements_show(inputs_ui),
    "game_keys": lambda: actions.user.ui_elements_show(game_keys_ui),
    "tabs": lambda: actions.user.ui_elements_show(tabs_ui),
    "todo_list": lambda: actions.user.ui_elements_show(todo_list_ui),
}

def examples_ui():
    div, text, screen, button, state = actions.user.ui_elements(["div", "text", "screen", "button", "state"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="272727", border_radius=16, border_width=1, width=200)[
            div(flex_direction='column', padding=16, border_bottom=1, border_color="555555")[
                text("Examples", font_size=24, margin_top=8),
                text("talon-ui-elements", font_size=14, color="FFCC00"),
            ],
            div()[
                *[button(name, on_click=action, padding=16, background_color="272727") for name, action in button_action.items()],
                button("Close", on_click=lambda: actions.user.ui_elements_hide_all(), color="de5474", font_weight="bold", padding=16, margin_bottom=16, background_color="272727", highlight_color="de547433"),
            ],
        ]
    ]