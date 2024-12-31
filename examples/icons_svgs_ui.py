from talon import actions

def icons_svgs_ui():
    elements = ["div", "text", "screen", "icon", "button"]
    svg_elements = ["svg", "path", "rect", "circle", "line", "polygon", "polyline"]
    div, text, screen, icon, button = actions.user.ui_elements(elements)
    svg, path, rect, circle, line, polygon, polyline = actions.user.ui_elements_svg(svg_elements)

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
                text("Icons and svg", font_size=24),
                text("talon-ui-elements", font_size=24, color="FFCC00"),
            ],
            div(flex_direction="column", gap=24, padding=16, border_bottom=1)[
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
                ],
                div(flex_direction="row")[
                    icon_with_text("check"),
                    icon_with_text("plus"),
                    icon_with_text("minus"),
                    icon_with_text("more_horizontal"),
                    icon_with_text("more_vertical"),
                ],
                div(flex_direction="row")[
                    icon_with_text("copy"),
                    icon_with_text("download"),
                    icon_with_text("external_link"),
                    icon_with_text("mic"),
                    icon_with_text("star"),
                ],
            ],
            div(flex_direction="column", gap=24, padding=16, border_bottom=1)[
                div(flex_direction="row")[
                    div(flex_direction="column", width=100, align_items="center")[
                        icon("close"),
                        text("default", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center")[
                        icon("close", stroke_width=1),
                        text("stroke_width", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center")[
                        icon("close", color="FFCC00"),
                        text("color", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center")[
                        icon("close", color="white", background_color="red", border_width=1, border_radius=4, border_color="white", margin_bottom=4),
                        text("border & background", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center")[
                        icon("close", size=16),
                        text("size", font_size=12)
                    ],
                ],
                div(flex_direction="row", gap=32, margin_left=24)[
                    div(flex_direction="row", align_items="center")[
                        icon("check", background_color="228B22", size=16, border_radius=2, margin=4),
                        text("Yes")
                    ],
                    div(flex_direction="row", align_items="center")[
                        icon("close", color="C70039", stroke_width=3, size=24),
                        text("No")
                    ]
                ]
            ],
            div(flex_direction="column", gap=24, padding=16, border_bottom=1)[
                div(flex_direction="row")[
                    # See https://iconsvg.xyz/ for references
                    div(flex_direction="column", width=100, align_items="center", gap=8)[
                        svg()[
                            path(d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48")
                        ],
                        text("svg path", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center", gap=8)[
                        svg()[
                            rect(x=9, y=9, width=6, height=6),
                            circle(cx=12, cy=12, r=10)
                        ],
                        text("svg rect circle", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center", gap=8)[
                        svg()[
                            line(x1=5, y1=12, x2=19, y2=12)
                        ],
                        text("svg line", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center", gap=8)[
                        svg()[
                            polygon(points="5 3 19 12 5 21 5 3")
                        ],
                        text("svg polygon", font_size=12)
                    ],
                    div(flex_direction="column", width=100, align_items="center", gap=8)[
                        svg()[
                            polyline(points="4 7 4 4 20 4 20 7"),
                            line(x1=9, y1=20, x2=15, y2=20),
                            line(x1=12, y1=4, x2=12, y2=20)
                        ],
                        text("svg line polyline", font_size=12)
                    ]
                ],
            ],
        ]
    ]