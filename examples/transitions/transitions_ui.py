from talon import actions


def transitions_ui():
    elements = ["div", "text", "button", "screen", "state", "style"]
    div, text, button, screen, state, style = actions.user.ui_elements(elements)

    expanded, set_expanded = state.use("expanded", False)
    faded, set_faded = state.use("faded", False)
    color_shifted, set_color_shifted = state.use("color_shifted", False)
    bounced, set_bounced = state.use("bounced", False)

    style({
        ".sidebar_btn": {
            "padding": 12,
            "padding_left": 20,
            "padding_right": 20,
            "border_radius": 6,
            "border_width": 1,
            "border_color": "#444444",
            "color": "#FFFFFF",
            "font_size": 14,
            "transition": {
                "background_color": 150,
                "border_color": 150,
                "color": 150,
            },
        },
        ".sidebar_btn_active": {
            "padding": 12,
            "padding_left": 20,
            "padding_right": 20,
            "border_radius": 6,
            "border_width": 1,
            "border_color": "#FFCC00",
            "background_color": "#3D3200",
            "color": "#FFCC00",
            "font_size": 14,
            "transition": {
                "background_color": 150,
                "border_color": 150,
                "color": 150,
            },
        },
    })

    def toggle_all():
        val = not (expanded or faded or color_shifted or bounced)
        set_expanded(val)
        set_faded(val)
        set_color_shifted(val)
        set_bounced(val)

    def reset():
        set_expanded(False)
        set_faded(False)
        set_color_shifted(False)
        set_bounced(False)

    all_active = expanded and faded and color_shifted and bounced

    return screen(justify_content="center", align_items="center")[
        div(
            draggable=True,
            background_color="#1E1E1E",
            border_radius=12,
            border_width=1,
            border_color="#333333",
            width=700,
            flex_direction="row",
        )[
            # Sidebar
            div(
                padding=16,
                gap=8,
                border_right=1,
                border_color="#333333",
                min_width=160,
            )[
                text("Transitions", font_size=18, font_weight="bold", color="#FFCC00", margin_bottom=8),
                button(
                    "Expand" if not expanded else "Collapse",
                    class_name="sidebar_btn_active" if expanded else "sidebar_btn",
                    on_click=lambda e: set_expanded(not expanded),
                ),
                button(
                    "Fade" if not faded else "Unfade",
                    class_name="sidebar_btn_active" if faded else "sidebar_btn",
                    on_click=lambda e: set_faded(not faded),
                ),
                button(
                    "Color" if not color_shifted else "Uncolor",
                    class_name="sidebar_btn_active" if color_shifted else "sidebar_btn",
                    on_click=lambda e: set_color_shifted(not color_shifted),
                ),
                button(
                    "Bounce" if not bounced else "Unbounce",
                    class_name="sidebar_btn_active" if bounced else "sidebar_btn",
                    on_click=lambda e: set_bounced(not bounced),
                ),
                div(height=8),
                button(
                    "All",
                    class_name="sidebar_btn_active" if all_active else "sidebar_btn",
                    on_click=lambda e: toggle_all(),
                ),
                button(
                    "Reset",
                    class_name="sidebar_btn",
                    on_click=lambda e: reset(),
                ),
            ],
            # Main content area
            div(
                flex=1,
                justify_content="center",
                align_items="center",
                padding=40,
                min_height=350,
            )[
                # Animated box
                div(
                    id="anim_box",
                    width=250 if expanded else 120,
                    height=200 if expanded else 120,
                    background_color="#FFCC00" if color_shifted else "#4488FF",
                    opacity=1.0 if not faded else 0.15,
                    border_radius=24 if bounced else 8,
                    justify_content="center",
                    align_items="center",
                    transition={
                        "width": 400,
                        "height": 400,
                        "opacity": (300, "linear"),
                        "background_color": 500,
                        "border_radius": (500, "ease_out_bounce"),
                    },
                )[
                    text(
                        "Animated",
                        font_size=20 if expanded else 14,
                        font_weight="bold",
                        color="#000000" if color_shifted else "#FFFFFF",
                        transition={
                            "font_size": 300,
                            "color": 500,
                        },
                    ),
                ],
                # Labels showing current state
                div(margin_top=24, gap=4, align_items="center")[
                    text(
                        f"width: {'250' if expanded else '120'}  "
                        f"height: {'200' if expanded else '120'}  "
                        f"opacity: {'1.0' if not faded else '0.15'}",
                        font_size=13,
                        color="#888888",
                    ),
                    text(
                        f"color: {'#FFCC00' if color_shifted else '#4488FF'}  "
                        f"border_radius: {'24' if bounced else '8'}",
                        font_size=13,
                        color="#888888",
                    ),
                ],
            ],
        ]
    ]


def show_transitions():
    actions.user.ui_elements_show(transitions_ui)


def hide_transitions():
    actions.user.ui_elements_hide(transitions_ui)


def toggle_transitions():
    actions.user.ui_elements_toggle(transitions_ui)
