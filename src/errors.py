from talon import actions, settings
from .constants import DEFAULT_ERROR_COLOR, DEFAULT_ERROR_LINK_COLOR
from .entry import render_ui

_pynput_warning_shown = False

def tuple_to_string(t) -> str:
    return ".".join(map(str, t))

def title(renderer):
    return f"talon-ui-elements error when trying to show {renderer.__qualname__}"

def message(current_version, min_version):
    return (
        f"Your current version of talon-ui-elements is ({current_version}) "
        f"but the minimum required version is ({min_version}). "
        "Please update to the latest version to use this feature. "
        "https://github.com/rokubop/talon-ui-elements"
    )

def fake_ui():
    screen, div = actions.user.ui_elements(["screen", "div"])
    return screen(justify_content="center", align_items="center")[
        div(),
    ]

def simulate_error():
    show_error_if_not_compatible(
        fake_ui,
        actions.user.ui_elements_version(),
        force=True
    )

def show_error_if_not_compatible(renderer, min_version, force=False) -> None:
    is_incompatible = False

    current_version_tuple = actions.user.ui_elements_version()
    current_version_str = tuple_to_string(current_version_tuple)
    min_version_tuple = tuple(map(int, min_version.split('.'))) if isinstance(min_version, str) else min_version
    min_version_str = tuple_to_string(min_version_tuple)

    if current_version_tuple < min_version_tuple or force:
        is_incompatible = True
        renderer_name = renderer.__qualname__
        title_message = title(renderer)
        error_message = message(current_version_str, min_version_str)
        print(f"Error: {title_message}\n{error_message}")
        if current_version_tuple >= (0, 9, 0):
            render_ui(generic_error_ui, props={
                "renderer_name": renderer_name,
                "current_version": current_version_str,
                "min_version": min_version_str,
            })

    return is_incompatible

def show_error_if_pynput_missing(renderer) -> bool:
    """If `user.ui_elements_mouse_use_pynput` is on but pynput isn't installed
    in Talon's Python env, show a one-time error UI explaining the situation
    and return True. Subsequent launches in the same session fall back
    silently to the native canvas.register() path."""
    global _pynput_warning_shown
    if _pynput_warning_shown:
        return False
    if not settings.get("user.ui_elements_mouse_use_pynput"):
        return False
    try:
        import pynput  # noqa: F401
        return False
    except ImportError:
        pass

    _pynput_warning_shown = True
    renderer_name = renderer.__qualname__
    print(
        f"talon-ui-elements: cannot show \"{renderer_name}\" with "
        "user.ui_elements_mouse_use_pynput enabled because the 'pynput' "
        "package is not installed in Talon's Python environment. Either "
        "install pynput or disable the setting."
    )
    if actions.user.ui_elements_version() >= (0, 9, 0):
        render_ui(pynput_missing_error_ui, props={"renderer_name": renderer_name})
    return True

def pynput_missing_error_ui(props) -> None:
    renderer_name = props.get("renderer_name")

    screen, window, div, text, link, button, icon = actions.user.ui_elements([
        "screen", "window", "div", "text", "link", "button", "icon"
    ])

    return screen(justify_content="center", align_items="center")[
        window(
            title="Error",
            border_radius=8,
            show_minimize=False,
        )[
            div(flex_direction="column", padding=16)[
                div(flex_direction="row")[
                    error_icon(margin_right=16),
                    div(gap=8)[
                        div(flex_direction="row", align_items="center", margin_top=8, margin_bottom=24)[
                            text(f"Cannot show \"{renderer_name}\"", font_size=18),
                        ],
                        text("The setting user.ui_elements_mouse_use_pynput is enabled,", margin_bottom=4),
                        text("but the 'pynput' package is not installed in Talon's Python", margin_bottom=4),
                        text("environment.", margin_bottom=16),
                        text("To fix, either:", margin_bottom=8),
                        text("  - Install pynput in Talon's bundled Python (`pip install pynput`)", margin_bottom=4),
                        text("  - Or disable user.ui_elements_mouse_use_pynput in your settings", margin_bottom=16),
                        div(flex_direction="row", justify_content="flex_end", margin_top=16)[
                            button(
                                "Close",
                                on_click=actions.user.ui_elements_hide_all,
                                autofocus=True,
                                padding=10,
                                padding_left=24,
                                padding_right=24,
                                border_width=1,
                                border_radius=4,
                            )
                        ],
                    ]
                ]
            ]
        ]
    ]

def error_icon(**kwargs):
    div, svg, circle, path = actions.user.ui_elements(["div", "svg", "circle", "path"])
    return div(**kwargs)[
        svg(size=30)[
            circle(cx=12, cy=12, r=10, fill=DEFAULT_ERROR_COLOR),
            path(d="M12 8v4m0 4h.01", stroke="#FFFFFF", stroke_width=2, stroke_linecap="round")
        ]
    ]

def generic_error_ui(props) -> None:
    renderer_name = props.get("renderer_name")
    current_version = props.get("current_version")
    min_version = props.get("min_version")

    screen, window, div, text, link, button, icon = actions.user.ui_elements([
        "screen", "window", "div", "text", "link", "button", "icon"
    ])

    return screen(justify_content="center", align_items="center")[
        window(
            title="Error",
            border_radius=8,
            show_minimize=False,
        )[
            div(flex_direction="column", padding=16)[
                div(flex_direction="row")[
                    error_icon(margin_right=16),
                    div(gap=8)[
                        div(flex_direction="row", align_items="center", margin_top=8, margin_bottom=24)[
                            text(f"Error when trying to show \"{renderer_name}\"", font_size=18),
                        ],
                        text(f"Your current version of talon-ui-elements is {current_version}"),
                        text(f"The minimum required version to view this is {min_version}", margin_bottom=16),
                        text(f"Please update to the latest version to use \"{renderer_name}\"", margin_bottom=16),
                        div(flex_direction="row", align_items="center")[
                            text("Get latest version: "),
                            link(
                                color=DEFAULT_ERROR_LINK_COLOR,
                                url="https://github.com/rokubop/talon-ui-elements",
                                flex_direction="row", align_items="center"
                            )[
                                text("talon-ui-elements GitHub", margin_right=4),
                                icon("external_link", color=DEFAULT_ERROR_LINK_COLOR, size=16),
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
                                border_width=1,
                                border_radius=4,
                            )
                        ],
                    ]
                ]
            ]
        ]
    ]
