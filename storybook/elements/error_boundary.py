from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    STRING, INT, COLOR,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("label", STRING, "MyView"),
    ("padding", INT, "24"),
    ("border_radius", INT, "0"),
    ("border_width", INT, "0"),
    ("border_color", COLOR, ""),
    ("background_color", COLOR, ""),
    ("title_color", COLOR, ""),
    ("message_color", COLOR, ""),
]


def _ok_view():
    div, text = actions.user.ui_elements(["div", "text"])
    return div(padding=12, gap=8, background_color=t.BG_RAISED, border_radius=4)[
        text("Rendered successfully", color=t.TEXT, font_size=14),
        text("error_boundary is transparent when the renderer succeeds.",
             color=t.TEXT_MUTED, font_size=14),
    ]


def _boom_view():
    raise RuntimeError("intentional error from _boom_view() to show the fallback")


def _toggle_view(props):
    div, text, button, state = actions.user.ui_elements(["div", "text", "button", "state"])
    should_throw, set_should_throw = state.use_local(False)

    if should_throw:
        raise ValueError("toggled into the broken state")

    return div(gap=8)[
        text("Currently rendering fine.", color=t.TEXT, font_size=14),
        button(
            "Break it",
            on_click=lambda e: set_should_throw(True),
            padding=8, border_radius=4, border_width=1,
            background_color=t.BG_RAISED, color=t.TEXT_SECONDARY, font_size=14,
        ),
    ]


def _custom_fallback(exc_kind, exc_msg, tb_str):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(
        padding=16, gap=6, background_color="2a1a00", border_radius=6,
        border_width=1, border_color="cc8800",
    )[
        text("oh no, something broke", color="ffcc66", font_size=16, font_weight="bold"),
        text(f"{exc_kind}: {exc_msg}", color="ffaa66", font_size=13, font_family="monospace"),
    ]


def error_boundary_stories():
    component, div, text, error_boundary, state = actions.user.ui_elements([
        "component", "div", "text", "error_boundary", "state",
    ])

    cs = build_controls_state(state, "eb", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)

    def _frame(child):
        """Box the error_boundary in an explicitly bounded container so
        the error card's flex=1 fill has something to fill, and the
        inner traceback's horizontal scroll has bounded width to scroll
        against. Without this, example_with_code's center-aligned
        wrapper lets the card grow to its natural content width."""
        return div(width=720, height=320)[child]

    return div(padding=32, gap=24)[
        text("error_boundary", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                error_boundary = actions.user.ui_elements(['error_boundary'])""")
        ),

        interactive_section(
            element_name="error_boundary",
            preview_element=_frame(error_boundary(_boom_view, **preview_props)),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="eb",
        ),

        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold",
                 color=t.TEXT, border_bottom=1, padding_bottom=12,
                 border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Renderer raises (default fallback card)",
                "example": _frame(error_boundary(_boom_view)),
                "code": textwrap.dedent("""\
                    def my_view():
                        raise RuntimeError("something went wrong")

                    error_boundary(my_view)"""),
            }),

            component(example_with_code, props={
                "title": "Custom fallback (full visual override)",
                "example": _frame(error_boundary(_boom_view, fallback=_custom_fallback)),
                "code": textwrap.dedent("""\
                    def my_fallback(exc_kind, exc_msg, tb_str):
                        return div(padding=16, background_color="2a1a00")[
                            text("oh no, something broke"),
                            text(f"{exc_kind}: {exc_msg}"),
                        ]

                    error_boundary(my_view, fallback=my_fallback)"""),
            }),

            component(example_with_code, props={
                "title": "Recovers on re-render",
                "example": _frame(error_boundary(_toggle_view)),
                "code": textwrap.dedent("""\
                    def my_view(props):
                        broken, set_broken = state.use_local(False)
                        if broken:
                            raise ValueError("broken")
                        return button("Break it",
                                      on_click=lambda e: set_broken(True))

                    error_boundary(my_view)

                    # Click 'Break it' to throw on next render; the
                    # boundary swaps in the error card. State change
                    # elsewhere re-renders and the boundary tries
                    # again -- so fixes hot-reload cleanly."""),
            }),

            component(example_with_code, props={
                "title": "Renderer succeeds (transparent)",
                "example": error_boundary(_ok_view),
                "code": textwrap.dedent("""\
                    def my_view():
                        return div(padding=12)[text("Rendered successfully")]

                    error_boundary(my_view)"""),
            }),
        ],
    ]
