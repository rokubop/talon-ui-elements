from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    STRING, INT, COLOR, BOOL,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("checked", BOOL, False),
    ("size", INT, "24"),
    ("color", COLOR, ""),
    ("disabled", BOOL, False),
]

def checkbox_stories():
    component, div, text, checkbox, state = actions.user.ui_elements([
        "component", "div", "text", "checkbox", "state"
    ])

    cs = build_controls_state(state, "cb", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)
    preview_props["id"] = "cb_preview"
    preview_props["on_change"] = lambda e: cs["checked"][1](e.checked)

    return div(padding=32, gap=24)[
        text("Checkbox", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                checkbox = actions.user.ui_elements(['checkbox'])""")
        ),

        interactive_section(
            element_name="checkbox",
            preview_element=checkbox(**preview_props),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="cb",
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Default Checkbox",
                "example": checkbox(),
                "code": textwrap.dedent("""\
                    checkbox()""")
            }),

            component(example_with_code, props={
                "title": "With Label",
                "example": div(
                    flex_direction="row",
                    align_items="center",
                    gap=8,
                )[
                    checkbox(id="ex_label"),
                    text("Label", for_id="ex_label")
                ],
                "code": textwrap.dedent("""\
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(id="a"),
                        text("Label", for_id="a")
                    ]""")
            }),

            component(example_with_code, props={
                "title": "Disabled",
                "example": div(
                    flex_direction="row",
                    align_items="center",
                    gap=8,
                )[
                    checkbox(id="ex_disabled", disabled=True),
                    text("Disabled", for_id="ex_disabled")
                ],
                "code": textwrap.dedent("""\
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(id="b", disabled=True),
                        text("Disabled", for_id="b")
                    ]""")
            }),

            component(example_with_code, props={
                "title": "State Management",
                "example": div(gap=12)[
                    div(flex_direction="row", align_items="center", gap=8)[
                        checkbox(
                            id="ex_notifications",
                            on_change=lambda e: print(f"Checked: {e.checked}")
                        ),
                        text("Enable notifications", for_id="ex_notifications")
                    ],
                ],
                "code": textwrap.dedent("""\
                    state = actions.user.ui_elements("state")
                    enabled, set_enabled = state.use("enabled", False)

                    checkbox(
                        id="notifications",
                        checked=enabled,
                        on_change=lambda e: set_enabled(e.checked)
                    )""")
            }),
        ],
    ]
