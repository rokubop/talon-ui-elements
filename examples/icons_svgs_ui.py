from talon import actions

def icons_svgs_ui():
    div, text, screen, icon, button = actions.user.ui_elements(["div", "text", "screen", "icon", "button"])

    def icon_with_text(name):
        return div(flex_direction="column", width=100, align_items="center")[
            button()[
                icon(name)
            ],
            text(name, font_size=12)
        ]

    return screen(justify_content="center", align_items="center")[
        div(background_color="272727", border_radius=8, border_width=1)[
            div(flex_direction='row', justify_content="space_between", padding=16, border_bottom=1, border_color="555555")[
                text("Icons", font_size=24),
                text("talon-ui-elements", font_size=24, color="FFCC00"),
            ],
            div(flex_direction="column", gap=24, padding=16)[
                div(flex_direction="row")[
                    icon_with_text("menu"),
                    icon_with_text("close"),
                    icon_with_text("home"),
                    icon_with_text("edit"),
                    icon_with_text("plus"),
                ],
                div(flex_direction="row")[
                    icon_with_text("chevron_down"),
                    icon_with_text("chevron_left"),
                    icon_with_text("chevron_right"),
                    icon_with_text("chevron_up"),
                    icon_with_text("settings"),
                ],
                div(flex_direction="row")[
                    icon_with_text("arrow_down"),
                    icon_with_text("arrow_left"),
                    icon_with_text("arrow_right"),
                    icon_with_text("arrow_up"),
                    icon_with_text("play"),
                ]
            ]
        ]
    ]