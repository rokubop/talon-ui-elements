from talon import actions

button_style = {
    "font_size": 20,
    "padding": 16,
    "padding_left": 32,
    "padding_right": 32,
    "margin_top": 32,
    "border_radius": 4,
    "background_color": "3B71CA",
}

def counter_ui():
    div, text, screen, button, use_state = actions.user.ui_elements(["div", "text", "screen", "button", "use_state"])

    count, set_count = use_state("count", 0)

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=32, border_radius=16, border_width=1, border_color="3B71CA")[
            div(flex_direction="row")[
                text("Count: ", font_size=24),
                text(count, font_size=24)
            ],
            button("Increment", button_style, on_click=lambda: set_count(count + 1)),
        ]
    ]

def show_counter_ui():
    actions.user.ui_elements_show(counter_ui)

def hide_counter_ui():
    actions.user.ui_elements_hide(counter_ui)