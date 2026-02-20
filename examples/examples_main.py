from talon import actions
from .alignment.alignment_ui import show_alignment
from .cheatsheet.cheatsheet_ui import show_cheatsheet, cheatsheet_mode_basic, cheatsheet_mode_advanced
from .dashboard.dashboard_ui import show_dashboard
from .game_keys.game_keys_actions import game_keys_show
from .hello_world.hello_world_ui import show_hello_world
from .actions.actions_ui import show_actions_ui
from .icons_svgs.icons_svgs_ui import show_icons_svgs
from .inputs.inputs_ui import show_inputs
from .state_vs_refs.state_vs_refs_ui import show_state_vs_refs
from .todo_list.todo_list_ui import show_todo_list
from .transitions.transitions_ui import show_transitions
from ..storybook.main import show_storybook
from ..src.dev_tools import DevTools
from ..tests.test_runner_ui import show_test_runner
from ..src.errors import simulate_error

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

def show_example(show_func):
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_show(go_back_ui)
    show_func()

def show_cheatsheet_example():
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_set_state("actions", [{
        "text": 'Basic Mode',
        "action": cheatsheet_mode_basic
    }, {
        "text": 'Advanced Mode',
        "action": cheatsheet_mode_advanced
    }])
    show_cheatsheet()
    show_actions_ui()
    actions.user.ui_elements_show(go_back_ui)

def show_game_keys_example():
    actions.user.ui_elements_hide_all()
    game_keys_show()
    actions.user.ui_elements_show(go_back_ui)

def show_inputs_example():
    actions.user.ui_elements_hide_all()
    show_inputs(on_submitted=go_back)
    actions.user.ui_elements_show(go_back_ui)

button_col1_actions = {
    "Hello world": lambda: show_example(show_hello_world),
    "Alignment": lambda: show_example(show_alignment),
    "Cheatsheet": show_cheatsheet_example,
    "Dashboard": lambda: show_example(show_dashboard),
    "Game keys": show_game_keys_example,
}
button_col2_actions = {
    "Icons and SVGs": lambda: show_example(show_icons_svgs),
    "Input Prompt": show_inputs_example,
    "State vs Ref": lambda: show_example(show_state_vs_refs),
    "Todo List": lambda: show_example(show_todo_list),
    "Transitions": lambda: show_example(show_transitions),
}
tools = {
    "Storybook": lambda: show_example(show_storybook),
    "Test Runner": lambda: show_example(show_test_runner),
    "Dev Tools": lambda: actions.user.ui_elements_toggle(DevTools),
    "Simulate Error": lambda: (
        actions.user.ui_elements_hide_all(),
        simulate_error(),
        actions.user.ui_elements_show(go_back_ui)
    )
}

def examples_ui():
    window, div, style = actions.user.ui_elements(["window", "div", "style"])
    text, screen, button = actions.user.ui_elements(["text", "screen", "button"])

    style({
        ".item": {
            "border_width": 1,
            "border_color": "#333333",
            "border_radius": 4,
            "color": "#FFFFFF",
            "padding": 16,
            "highlight_style": {
                "background_color": "#333333",
                "color": "#FFCC00",
            },
        }
    })

    return screen(justify_content="center", align_items="center")[
        window(
            title="UI Elements",
            min_width=200,
            show_minimize=False,
            title_bar_style={
                "border_bottom": 1,
                "border_color": "#FFCC00",
            },
        )[
            div(flex_direction="row", border_bottom=1)[
                div(border_right=1)[
                    text("Examples", font_size=18, font_weight="bold", padding=16, padding_bottom=0),
                    div(flex_direction="row", gap=16, padding=16)[
                        div(gap=8)[
                            *[button(name, class_name="item", on_click=action) for name, action in button_col1_actions.items()],
                        ],
                        div(gap=8)[
                            *[button(name, class_name="item", on_click=action) for name, action in button_col2_actions.items()],
                        ],
                    ],
                ],
                div()[
                    text("Tools", font_size=18, font_weight="bold", padding=16, padding_bottom=0),
                    div(flex_direction="row", gap=16, padding=16)[
                        div(gap=8)[
                            *[button(name, class_name="item", on_click=action) for name, action in tools.items()],
                        ],
                    ],
                ],
            ],
            div(flex_direction="row", justify_content="flex_end", align_items="center")[
                button(
                    "Exit",
                    on_click=actions.user.ui_elements_hide_all,
                    color="#FFCC00",
                    font_weight="bold",
                    border_radius=6,
                    padding_left=20,
                    padding_right=20,
                    padding_top=8,
                    padding_bottom=8,
                    margin_right=16,
                    margin_top=8,
                    margin_bottom=8,
                ),
            ]
        ]
    ]

def toggle_elements_examples():
    if not actions.user.ui_elements_get_trees():
        actions.user.ui_elements_show(examples_ui)
    else:
        actions.user.ui_elements_hide_all()