from talon import actions

def button_storybook():
    div, text, button, icon, input_text = actions.user.ui_elements([
        "div", "text", "button", "icon", "input_text"
    ])

    return div(padding=32, gap=24)[
        text("Button", font_size=22, font_weight="bold", color="#F1F1F1"),
        text("A button triggers an action or event. Below are some variations and usage examples.", color="#B0B0B0", font_size=15),

        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color="#F1F1F1"),
            div(gap=12, flex_direction="row")[
                button("Default", padding=12, border_radius=6, background_color="#23242A", color="#F1F1F1"),
                button("Primary", padding=12, border_radius=6, background_color="#3B82F6", color="#FFFFFF"),
                button("Success", padding=12, border_radius=6, background_color="#22C55E", color="#FFFFFF"),
                button(
                    icon("chevron_right", size=16, color="#F1F1F1"),
                    "Icon Button",
                    flex_direction="row",
                    gap=6,
                    padding=12,
                    border_radius=6,
                    background_color="#23242A",
                    color="#F1F1F1"
                ),
                # button("Disabled", padding=12, border_radius=6, background_color="#23242A", color="#888", disabled=True),
            ],
        ],

        div(gap=8)[
            text("Code Example", font_size=18, font_weight="bold", color="#F1F1F1"),
            div(background_color="#181A20", border_radius=8, padding=16, font_family="monospace", color="#A0A0A0", font_size=14)[
                text(
                    'button("Primary", padding=12, border_radius=6, background_color="#3B82F6", color="#FFFFFF")',
                )
            ]
        ],

        div(gap=8)[
            text("Interactive Example", font_size=18, font_weight="bold", color="#F1F1F1"),
            div(gap=8)[
                text("Try clicking the button below:"),
                button("Click me!", padding=12, border_radius=6, background_color="#F59E42", color="#181A20", on_click=lambda e: actions.user.notify("Button clicked!")),
            ]
        ]
    ]
