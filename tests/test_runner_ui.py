from talon import actions, Module, cron
from .test_helpers import run_tests

mod = Module()

button_style = {
    "padding": 8,
    "padding_left": 12,
    "padding_right": 12,
    "flex_direction": "row",
    "font_size": 14,
    "border_width": 1,
    "border_color": "111111",
    "background_color": "333333",
    "border_radius": 8,
    "align_items": "center",
    "justify_content": "center",
    "gap": 8,
    "margin": 16,
    "margin_bottom": 0,
}

def play_button():
    div, text, icon, button, state = actions.user.ui_elements(["div", "text", "icon", "button", "state"])
    play, set_play = state.use("play", False)
    play_bg_color = "161616"

    def on_play():
        cron.after("10ms", run_tests)

    if play:
        return button(button_style)[
            text("Running..."),
        ]
    else:
        return button(button_style, on_click=on_play, autofocus=True)[
            icon("play", fill=play_bg_color, size=14, stroke_width=6),
            text("Run tests"),
        ]

def runner_ui():
    screen, window, div, state = actions.user.ui_elements(["screen", "window", "div", "state"])
    log = state.get("log", [])

    return screen(justify_content="center", align_items="center")[
        window(title="ui_elements test runner", min_width=400, min_height=300)[
            play_button(),
            div(margin=16, padding=8, gap=8, background_color="111111", border_radius=4, min_height=250)[
                *log,
            ]
        ]
    ]

def show_test_runner():
    actions.user.ui_elements_show(runner_ui)

def hide_test_runner():
    actions.user.ui_elements_hide(runner_ui)

def toggle_test_runner():
    actions.user.ui_elements_toggle(runner_ui)