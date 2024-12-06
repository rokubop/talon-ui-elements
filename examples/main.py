from talon import actions
from .alignment import alignment_ui
from .cheatsheet import cheatsheet_show
from .state_and_refs import state_and_refs_ui
from .dashboard import dashboard_ui
from .inputs import inputs_ui
from .game_keys import game_keys_ui, set_game_keys_actions_state
from .todo_list import todo_list_ui
from .actions import actions_ui

def on_go_back():
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_show(examples_ui)

def go_back_ui():
    div, text, screen, button = actions.user.ui_elements(["div", "text", "screen", "button"])

    return screen()[
        div(margin_left=80, margin_top=100, background_color="272727", border_radius=16, border_width=1)[
            text("talon-ui-elements", font_size=14, padding=16, color="FFCC00"),
            button("Go back", on_click=on_go_back, padding=16, background_color="272727", ),
            button("Exit", on_click=lambda: actions.user.ui_elements_hide_all(), padding=16, margin_bottom=8, background_color="272727"),
        ]
    ]

def show_example(ui1, ui2=None, ui3=None):
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_show(ui1)
    if ui2:
        actions.user.ui_elements_show(ui2)
    if ui3:
        actions.user.ui_elements_show(ui3)
    actions.user.ui_elements_show(go_back_ui)

def show_game_keys():
    actions.user.ui_elements_hide_all()
    set_game_keys_actions_state()
    actions.user.ui_elements_show(game_keys_ui)
    actions.user.ui_elements_show(actions_ui)
    actions.user.ui_elements_show(go_back_ui)

button_action = {
    "Alignment": lambda: show_example(alignment_ui),
    "Cheatsheet": lambda: (actions.user.ui_elements_hide_all(), cheatsheet_show(), actions.user.ui_elements_show(go_back_ui)),
    "Dashboard": lambda: show_example(dashboard_ui),
    "Game keys": show_game_keys,
    "Input Prompt": lambda: show_example(inputs_ui),
    "State vs Ref": lambda: show_example(state_and_refs_ui),
    "Todo List": lambda: show_example(todo_list_ui),
}

def examples_ui():
    div, text, screen, button = actions.user.ui_elements(["div", "text", "screen", "button"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="272727", border_radius=16, border_width=1, width=200)[
            div(flex_direction='column', padding=16)[
                text("Examples", font_size=24, margin_top=8),
                text("talon-ui-elements", font_size=14, color="FFCC00"),
            ],
            div()[
                *[button(name, on_click=action, padding=16, background_color="272727") for name, action in button_action.items()],
                button("Exit", on_click=lambda: actions.user.ui_elements_hide_all(), color="de5474", font_weight="bold", padding=16, margin_bottom=16, background_color="272727", highlight_color="de547433"),
            ],
        ]
    ]