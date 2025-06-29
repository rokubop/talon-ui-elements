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
from ..storybook.main import storybook_ui
from ..src.dev_tools import DevTools
from ..tests.test_runner_ui import runner_ui
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

def show_cheatsheet():
    actions.user.ui_elements_hide_all()
    cheatsheet_show()
    actions.user.ui_elements_show(go_back_ui)

def show_example(ui):
    actions.user.ui_elements_hide_all()
    actions.user.ui_elements_show(go_back_ui)
    actions.user.ui_elements_show(ui)

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

button_col1_actions = {
    "Hello world": lambda: show_example(hello_world_ui),
    "Alignment": lambda: show_example(alignment_ui),
    "Cheatsheet": show_cheatsheet,
    "Dashboard": lambda: show_example(dashboard_ui),
    "Game keys": show_game_keys,
}
button_col2_actions = {
    "Icons and SVGs": lambda: show_example(icons_svgs_ui),
    "Input Prompt": show_inputs,
    "State vs Ref": lambda: show_example(state_vs_refs_ui),
    "Todo List": lambda: show_example(todo_list_ui),
}
tools = {
    "Storybook": lambda: show_example(storybook_ui),
    "Test Runner": lambda: show_example(runner_ui),
    "Dev Tools": lambda: actions.user.ui_elements_show(DevTools),
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