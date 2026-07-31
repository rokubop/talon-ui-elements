"""Window storybook. Windows render as standalone OS windows rather than
inline elements, so each story exposes an Open button that drives a
dedicated renderer; close via the window's own X."""

from talon import actions
from ..common import code, example_with_code
from .. import theme as t
import textwrap


# ----- one renderer per story variation -----

def _basic_window():
    screen, window, div, text = actions.user.ui_elements([
        "screen", "window", "div", "text"
    ])
    return screen()[
        window(title="Basic window")[
            div(padding=24, gap=12, min_width=280)[
                text("A plain window with the default chrome.", color=t.TEXT),
            ],
        ],
    ]


def _resizable_window():
    screen, window, div, text = actions.user.ui_elements([
        "screen", "window", "div", "text"
    ])
    return screen(align_items="center", justify_content="center")[
        window(
            title="Resizable",
            resizable=True,
            min_width=320, min_height=200,
            max_width="80%", max_height="80%",
        )[
            div(padding=24, gap=12)[
                text("Drag the bottom-right corner to resize.", color=t.TEXT),
                text("Honors min_width/min_height and max_width/max_height.",
                     color=t.TEXT_SECONDARY),
            ],
        ],
    ]


def _styled_title_bar_window():
    screen, window, div, text = actions.user.ui_elements([
        "screen", "window", "div", "text"
    ])
    return screen(align_items="center", justify_content="center")[
        window(
            title="Styled title bar",
            title_bar_style={
                "background_color": t.BG_RAISED,
                "color": "ffcc66",
                "font_weight": "bold",
            },
            background_color=t.BG,
            border_width=1, border_color=t.BORDER,
            border_radius=8,
        )[
            div(padding=24, gap=12, min_width=320)[
                text("title_bar_style themes just the title row.", color=t.TEXT),
            ],
        ],
    ]


def _icon_window():
    screen, window, div, text, icon = actions.user.ui_elements([
        "screen", "window", "div", "text", "icon"
    ])
    return screen(align_items="center", justify_content="center")[
        window(
            title="Settings",
            icon=icon("settings"),
        )[
            div(padding=24, gap=12, min_width=300)[
                text("Pass an icon element as `icon=` to render it in the title bar.",
                     color=t.TEXT),
                text("The icon is auto-scaled to the title font size.",
                     color=t.TEXT_SECONDARY),
            ],
        ],
    ]


def _launch(fn):
    try:
        actions.user.ui_elements_hide(fn)
    except Exception:
        pass
    actions.user.ui_elements_show(fn)


# ----- storybook page -----

def window_stories():
    component, div, text, button = actions.user.ui_elements([
        "component", "div", "text", "button"
    ])

    btn_kwargs = dict(
        font_size=14, color=t.TEXT,
        background_color=t.BG_ACTIVE,
        border_radius=6,
        border_width=1, border_color=t.BORDER,
        padding=8, padding_left=14, padding_right=14,
    )

    def open_btn(fn, label="Open"):
        return button(label, on_click=lambda: _launch(fn), **btn_kwargs)

    return div(padding=32, gap=24)[
        text("Window", font_size=22, font_weight="bold", color=t.TEXT),
        text(
            "Floating draggable surface with a title bar and minimize/close "
            "controls by default. Rendered via screen → window and shown "
            "with ui_elements_show.",
            color=t.TEXT_SECONDARY,
        ),
        code(
            textwrap.dedent("""\
                screen, window = actions.user.ui_elements(['screen', 'window'])""")
        ),

        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT,
                 border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Basic Window",
                "example": open_btn(_basic_window),
                "code": textwrap.dedent("""\
                    def my_ui():
                        return screen()[
                            window(title="Basic window")[
                                div(padding=24, gap=12)[
                                    text("A plain window with the default chrome."),
                                ],
                            ],
                        ]

                    actions.user.ui_elements_show(my_ui)"""),
            }),

            component(example_with_code, props={
                "title": "Resizable",
                "example": open_btn(_resizable_window),
                "code": textwrap.dedent("""\
                    window(
                        title="Resizable",
                        resizable=True,
                        min_width=320, min_height=200,
                        max_width="80%", max_height="80%",
                    )[
                        div(padding=24)[text("Drag the bottom-right corner.")],
                    ]"""),
            }),

            component(example_with_code, props={
                "title": "Styled Title Bar",
                "example": open_btn(_styled_title_bar_window),
                "code": textwrap.dedent("""\
                    window(
                        title="Styled title bar",
                        title_bar_style={
                            "background_color": "#2E2E36",
                            "color": "ffcc66",
                            "font_weight": "bold",
                        },
                        background_color="#1A1A1F",
                        border_width=1, border_color="#4A4A56",
                        border_radius=8,
                    )[
                        div(padding=24)[text("title_bar_style themes the title row.")],
                    ]"""),
            }),

            component(example_with_code, props={
                "title": "Title Bar Icon",
                "example": open_btn(_icon_window),
                "code": textwrap.dedent("""\
                    screen, window, div, text, icon = actions.user.ui_elements([
                        'screen', 'window', 'div', 'text', 'icon'
                    ])

                    window(
                        title="Settings",
                        icon=icon("settings"),
                    )[
                        div(padding=24)[text("Pass an icon element as icon=.")],
                    ]"""),
            }),
        ],
    ]
