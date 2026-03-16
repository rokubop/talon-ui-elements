from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    STRING, INT, COLOR,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("placeholder", STRING, "Enter text..."),
    ("value", STRING, ""),
    ("font_size", INT, "16"),
    ("rows", INT, "3"),
    ("width", INT, "400"),
    ("padding", INT, ""),
    ("border_radius", INT, "4"),
    ("border_width", INT, "0"),
    ("border_color", COLOR, ""),
    ("background_color", COLOR, ""),
    ("color", COLOR, ""),
    ("placeholder_color", COLOR, ""),
    ("selection_color", COLOR, ""),
    ("cursor_color", COLOR, ""),
]

def textarea_stories():
    component, div, text, textarea, state, button = actions.user.ui_elements([
        "component", "div", "text", "textarea", "state", "button"
    ])

    cs = build_controls_state(state, "ta", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)
    preview_props["id"] = "ta_preview"

    return div(padding=32, gap=24)[
        text("Textarea", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                textarea = actions.user.ui_elements(['textarea'])""")
        ),

        interactive_section(
            element_name="textarea",
            preview_element=textarea(**preview_props),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="ta",
            id_override="my_textarea",
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "With Placeholder",
                "example": textarea(id="ex_ta_placeholder", placeholder="Write your notes here..."),
                "code": textwrap.dedent("""\
                    textarea(id="my_textarea", placeholder="Write your notes here...")"""),
            }),

            component(example_with_code, props={
                "title": "With Rows",
                "example": textarea(id="ex_ta_rows", rows=5, placeholder="5 rows tall"),
                "code": textwrap.dedent("""\
                    textarea(id="my_textarea", rows=5, placeholder="5 rows tall")"""),
            }),

            component(example_with_code, props={
                "title": "With Initial Value",
                "example": textarea(id="ex_ta_value", value="Line one\nLine two\nLine three", rows=4),
                "code": textwrap.dedent("""\
                    textarea(
                        id="my_textarea",
                        value="Line one\\nLine two\\nLine three",
                        rows=4,
                    )"""),
            }),

            component(example_with_code, props={
                "title": "Styled Textarea",
                "example": textarea(
                    id="ex_ta_styled",
                    placeholder="Styled textarea",
                    background_color="#1A1A2E",
                    color="#E94560",
                    border_radius=8,
                    border_width=1,
                    border_color="#E94560",
                    cursor_color="#E94560",
                    selection_color="E9456088",
                    width=400,
                    rows=4,
                ),
                "code": textwrap.dedent("""\
                    textarea(
                        id="my_textarea",
                        placeholder="Styled textarea",
                        background_color="#1A1A2E",
                        color="#E94560",
                        border_radius=8,
                        border_width=1,
                        border_color="#E94560",
                        cursor_color="#E94560",
                        selection_color="E9456088",
                        width=400,
                        rows=4,
                    )"""),
            }),

            component(example_with_code, props={
                "title": "With on_change Callback",
                "example": textarea(
                    id="ex_ta_onchange",
                    placeholder="Type to see events",
                    rows=3,
                    on_change=lambda e: print(f"Value: {e.value}"),
                ),
                "code": textwrap.dedent("""\
                    def handle_change(e):
                        print(e.value)           # Current value
                        print(e.previous_value)  # Previous value
                        print(e.id)              # Element id

                    textarea(
                        id="my_textarea",
                        placeholder="Type to see events",
                        rows=3,
                        on_change=handle_change,
                    )"""),
            }),

            component(example_with_code, props={
                "title": "Reading Value with Ref",
                "example": div(flex_direction="row", gap=8, align_items="flex_start")[
                    textarea(id="ex_ta_ref", placeholder="Type something", rows=3),
                    button("Log Value", on_click=lambda: print(
                        actions.user.ui_elements_get_input_value("ex_ta_ref")
                    ), border_radius=4, padding=8, padding_top=6, padding_bottom=6),
                ],
                "code": textwrap.dedent("""\
                    ref = actions.user.ui_elements("ref")
                    my_ref = ref("my_textarea")

                    textarea(id="my_textarea", placeholder="Type something", rows=3)
                    button("Log Value", on_click=lambda: print(my_ref.value))"""),
            }),
        ],
    ]
