from talon import actions
from ..common import code, example_with_code
from .. import theme as t
import textwrap


def modal_stories():
    component, div, text, button, modal, state = actions.user.ui_elements([
        "component", "div", "text", "button", "modal", "state"
    ])

    basic_open, set_basic_open = state.use("modal_basic_open", False)
    no_title_open, set_no_title_open = state.use("modal_no_title_open", False)
    no_backdrop_close_open, set_no_backdrop_close_open = state.use("modal_locked_open", False)
    sized_open, set_sized_open = state.use("modal_sized_open", False)

    return div(padding=32, gap=24)[
        text("Modal", font_size=22, font_weight="bold", color=t.TEXT),
        text(
            "Full-viewport overlay layer. Auto-scopes hints and clicks to "
            "its subtree while open - background elements are inert. "
            "Esc dismisses unless backdrop_click_close=False.",
            color=t.TEXT_SECONDARY,
        ),
        code(
            textwrap.dedent("""\
                modal = actions.user.ui_elements(['modal'])""")
        ),

        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Basic Modal",
                "example": div(gap=8)[
                    button("Open modal", on_click=lambda: set_basic_open(True)),
                    modal(
                        title="Hello",
                        open=basic_open,
                        on_close=lambda: set_basic_open(False),
                        padding=24,
                        gap=12,
                        min_width=320,
                    )[
                        text("This is a modal."),
                        text("Click outside or the X to close.", color=t.TEXT_SECONDARY),
                    ],
                ],
                "code": textwrap.dedent("""\
                    open, set_open = state.use("open", False)

                    div(gap=8)[
                        button("Open modal", on_click=lambda: set_open(True)),
                        modal(
                            title="Hello",
                            open=open,
                            on_close=lambda: set_open(False),
                            padding=24,
                            gap=12,
                            min_width=320,
                        )[
                            text("This is a modal."),
                            text("Click outside or the X to close."),
                        ],
                    ]""")
            }),

            component(example_with_code, props={
                "title": "No Title Bar",
                "example": div(gap=8)[
                    button("Open without title bar", on_click=lambda: set_no_title_open(True)),
                    modal(
                        open=no_title_open,
                        on_close=lambda: set_no_title_open(False),
                        show_title_bar=False,
                        padding=24,
                        gap=16,
                        min_width=280,
                    )[
                        text("Just content, no header.", font_size=18),
                        button("Dismiss", on_click=lambda: set_no_title_open(False)),
                    ],
                ],
                "code": textwrap.dedent("""\
                    modal(
                        open=open,
                        on_close=lambda: set_open(False),
                        show_title_bar=False,
                        padding=24,
                        gap=16,
                        min_width=280,
                    )[
                        text("Just content, no header.", font_size=18),
                        button("Dismiss", on_click=lambda: set_open(False)),
                    ]""")
            }),

            component(example_with_code, props={
                "title": "Locked Backdrop (must use button)",
                "example": div(gap=8)[
                    button("Open locked", on_click=lambda: set_no_backdrop_close_open(True)),
                    modal(
                        title="Confirm",
                        open=no_backdrop_close_open,
                        on_close=lambda: set_no_backdrop_close_open(False),
                        backdrop_click_close=False,
                        padding=24,
                        gap=16,
                        min_width=320,
                    )[
                        text("Backdrop clicks and Esc are ignored here."),
                        div(flex_direction="row", gap=8, justify_content="flex_end")[
                            button("Cancel", on_click=lambda: set_no_backdrop_close_open(False)),
                            button("Confirm", on_click=lambda: set_no_backdrop_close_open(False)),
                        ],
                    ],
                ],
                "code": textwrap.dedent("""\
                    modal(
                        title="Confirm",
                        open=open,
                        on_close=lambda: set_open(False),
                        backdrop_click_close=False,
                        padding=24,
                        gap=16,
                        min_width=320,
                    )[
                        text("Backdrop clicks and Esc are ignored here."),
                        div(flex_direction="row", gap=8, justify_content="flex_end")[
                            button("Cancel", on_click=lambda: set_open(False)),
                            button("Confirm", on_click=lambda: set_open(False)),
                        ],
                    ]""")
            }),

            component(example_with_code, props={
                "title": "Sized Panel",
                "example": div(gap=8)[
                    button("Open sized", on_click=lambda: set_sized_open(True)),
                    modal(
                        title="Big Modal",
                        open=sized_open,
                        on_close=lambda: set_sized_open(False),
                        width=520,
                        height=320,
                        padding=24,
                    )[
                        text("Sizing props (width/height/padding) apply to the centered panel, not the full-viewport wrapper."),
                    ],
                ],
                "code": textwrap.dedent("""\
                    modal(
                        title="Big Modal",
                        open=open,
                        on_close=lambda: set_open(False),
                        width=520,
                        height=320,
                        padding=24,
                    )[
                        text("Sizing props (width/height/padding) "
                             "apply to the centered panel, "
                             "not the full-viewport wrapper."),
                    ]""")
            }),
        ],
    ]
