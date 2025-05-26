from talon import actions

def modal_example():
    screen, window, div, button, text, modal, state = actions.user.ui_elements([
        "screen", "window", "div", "button", "text", "modal", "state"
    ])

    show_modal, set_show_modal = state.use("show_modal", False)

    def open_modal():
        set_show_modal(True)

    def close_modal():
        set_show_modal(False)

    return screen()[
        window(title="Modal Example")[
            div(padding=16)[
                button("Open Modal", on_click=open_modal, padding=12),
            ],
            modal(
                title="Hello Modal",
                open=show_modal,
                on_close=close_modal,
                draggable=True,
                width=400,
                padding=16,
            )[
                div(flex_direction="column", gap=16, padding=16)[
                    text("This is a modal dialog", font_size=18),
                    text("You can add content here."),
                    div(flex_direction="row", justify_content="flex_end", gap=8)[
                        button("Cancel", on_click=close_modal, padding=8),
                        button("OK", on_click=close_modal, padding=8),
                    ]
                ]
            ]
        ]
    ]