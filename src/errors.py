from talon import actions
from .utils import get_version
from .entry import render_ui

def title(renderer):
    return f"talon-ui-elements error when trying to show {renderer.__qualname__}"

def message(current_version, min_version):
    return (
        f"Your current version of talon-ui-elements is ({current_version}) ",
        f"but the minimum required version is ({min_version}). ",
        "Please update to the latest version to use this feature.",
    )

def show_error_if_not_compatible(renderer, min_version) -> None:
    is_incompatible = False
    current_version = get_version()

    if current_version < min_version:
        is_incompatible = True
        renderer_name = renderer.__qualname__
        title_message = title(renderer)
        error_message = message(current_version, min_version)
        print(f"Error: {title_message}\n{error_message}")
        if current_version >= "0.9.0":
            render_ui(generic_error_ui, props={
                "renderer_name": renderer_name,
                "current_version": current_version,
                "min_version": min_version,
            })

    return is_incompatible

def error_icon(**kwargs):
    div, svg, circle, path = actions.user.ui_elements(["div", "svg", "circle", "path"])
    return div(**kwargs)[
        svg(size=30)[
            circle(cx=12, cy=12, r=10, fill="#bd2f3e"),
            path(d="M12 8v4m0 4h.01", stroke="#FFFFFF", stroke_width=2, stroke_linecap="round")
        ]
    ]

def generic_error_ui(props) -> None:
    renderer_name = props.get("renderer_name")
    current_version = props.get("current_version")
    min_version = props.get("min_version")

    screen, window, div, text, link, style, button, icon = actions.user.ui_elements([
        "screen", "window", "div", "text", "link", "style", "button", "icon"
    ])

    style({
        "text": {
            "color": "#272727",
        },
    })

    return screen(justify_content="center", align_items="center")[
        window(
            title="Error",
            background_color="#e6e6e6",
            border_radius=8,
            show_minimize=False,
            title_bar_style={
                "background_color": "#cacaca",
                "color": "#272727",
            },
            focus_outline_color="#272727",
        )[
            div(flex_direction="column", padding=16)[
                div(flex_direction="row")[
                    error_icon(margin_right=16),
                    div(gap=8)[
                        div(flex_direction="row", align_items="center", margin_top=8, margin_bottom=12)[
                            text(f"Error when trying to show {renderer_name}", font_size=18, font_weight="bold"),
                        ],
                        text(f"Your current version of talon-ui-elements is {current_version}"),
                        text(f"The minimum required version is {min_version}", margin_bottom=16),
                        text("Please update to the latest version to use this feature.", margin_bottom=16),
                        div(flex_direction="row", align_items="center")[
                            text("Get latest version: "),
                            link(
                                color="#0058b5",
                                background_color="#e6e6e6",
                                url="https://github.com/rokubop/talon-ui-elements",
                                flex_direction="row", align_items="center"
                            )[
                                text("talon-ui-elements GitHub", color="#0058b5", margin_right=4),
                                icon("external_link", color="#0058b5", size=16),
                            ],
                        ],
                        div(flex_direction="row", justify_content="flex_end", margin_top=16)[
                            button(
                                "Close",
                                on_click=actions.user.ui_elements_hide_all,
                                autofocus=True,
                                padding=10,
                                padding_left=24,
                                padding_right=24,
                                color="#272727",
                                background_color="#e6e6e6",
                                border_color="#707070",
                                border_width=1,
                                border_radius=4,
                            )
                        ],
                    ]
                ]
            ]
        ]
    ]
