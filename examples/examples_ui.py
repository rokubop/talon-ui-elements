from talon import actions
from .alignment_ui import alignment_ui
from .cheatsheet_actions import cheatsheet_show
from .dashboard_ui import dashboard_ui
from .game_keys_actions import game_keys_show
from .hello_world_ui import hello_world_ui
from .icons_svgs_ui import icons_svgs_ui
from .inputs_ui import inputs_ui
from .state_vs_refs_ui import state_vs_refs_ui
from .todo_list_ui import todo_list_ui

def go_back():
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_show(examples_ui)

def go_back_ui():
    div, text, screen, button = actions.user.ui_elements(["div", "text", "screen", "button"])

    return screen()[
        div(draggable=True, margin_left=80, margin_top=100, background_color="272727", border_radius=16, border_width=1)[
            text("talon-ui-elements", font_size=14, padding=16, color="FFCC00"),
            button("Go back", on_click=go_back, padding=16, background_color="272727"),
            button("Exit", on_click=actions.user.ui_elements_hide_all, padding=16, margin_bottom=8, background_color="272727"),
        ]
    ]

def show_cheatsheet():
    actions.user.ui_elements_hide_all()
    cheatsheet_show()
    actions.user.ui_elements_show(go_back_ui)

def show_example(ui):
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_show(ui)
    actions.user.ui_elements_show(go_back_ui)

def show_game_keys():
    actions.user.ui_elements_hide_all()
    game_keys_show()
    actions.user.ui_elements_show(go_back_ui)

def show_inputs():
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_show(inputs_ui, props={
        "on_submitted": go_back
    })
    actions.user.ui_elements_show(go_back_ui)

button_action = {
    "Alignment": lambda: show_example(alignment_ui),
    "Cheatsheet": show_cheatsheet,
    "Dashboard": lambda: show_example(dashboard_ui),
    "Game keys": show_game_keys,
    "Hello world": lambda: show_example(hello_world_ui),
    "Icons and SVGs": lambda: show_example(icons_svgs_ui),
    "Input Prompt": show_inputs,
    "State vs Ref": lambda: show_example(state_vs_refs_ui),
    "Todo List": lambda: show_example(todo_list_ui),
}

def examples_ui():
    div, text, screen, button = actions.user.ui_elements(["div", "text", "screen", "button"])

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="272727", border_radius=16, border_width=1, width=200)[
            div(flex_direction='column', padding=16)[
                text("Examples", font_size=24, margin_top=8),
                text("talon-ui-elements", font_size=14, color="FFCC00"),
            ],
            div()[
                *[button(name, on_click=action, padding=16) for name, action in button_action.items()],
                button("Exit", on_click=lambda: actions.user.ui_elements_hide_all(), color="de5474", font_weight="bold", padding=16, margin_bottom=16),
            ],
        ]
    ]

def toggle_elements_examples():
    if not actions.user.ui_elements_get_trees():
        actions.user.ui_elements_show(examples_ui)
    else:
        actions.user.ui_elements_hide_all()