from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    STRING, INT, COLOR, BOOL,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("placeholder", STRING, "Search..."),
    ("value", STRING, ""),
    ("font_size", INT, "16"),
    ("width", INT, "300"),
    ("padding", INT, ""),
    ("border_radius", INT, "4"),
    ("border_width", INT, "0"),
    ("border_color", COLOR, ""),
    ("background_color", COLOR, ""),
    ("color", COLOR, ""),
    ("placeholder_color", COLOR, ""),
    ("selection_color", COLOR, ""),
    ("cursor_color", COLOR, ""),
    ("autofocus", BOOL, False),
]

def input_text_stories():
    component, div, text, input_text, state, button = actions.user.ui_elements([
        "component", "div", "text", "input_text", "state", "button"
    ])

    cs = build_controls_state(state, "it", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)
    preview_props["id"] = "it_preview"

    return div(padding=32, gap=24)[
        text("Input Text", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                input_text = actions.user.ui_elements(['input_text'])""")
        ),

        interactive_section(
            element_name="input_text",
            preview_element=input_text(**preview_props),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="it",
            id_override="my_input",
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "With Placeholder",
                "example": input_text(id="ex_placeholder", placeholder="Search..."),
                "code": textwrap.dedent("""\
                    input_text(id="my_input", placeholder="Search...")"""),
            }),

            component(example_with_code, props={
                "title": "With Initial Value",
                "example": input_text(id="ex_value", value="Hello world"),
                "code": textwrap.dedent("""\
                    input_text(id="my_input", value="Hello world")"""),
            }),

            component(example_with_code, props={
                "title": "Styled Input",
                "example": input_text(
                    id="ex_styled",
                    placeholder="Styled input",
                    background_color="#1A1A2E",
                    color="#E94560",
                    border_radius=8,
                    border_width=1,
                    border_color="#E94560",
                    cursor_color="#E94560",
                    selection_color="E9456088",
                    width=300,
                ),
                "code": textwrap.dedent("""\
                    input_text(
                        id="my_input",
                        placeholder="Styled input",
                        background_color="#1A1A2E",
                        color="#E94560",
                        border_radius=8,
                        border_width=1,
                        border_color="#E94560",
                        cursor_color="#E94560",
                        selection_color="E9456088",
                        width=300,
                    )"""),
            }),

            component(example_with_code, props={
                "title": "With on_change Callback",
                "example": input_text(
                    id="ex_onchange",
                    placeholder="Type to see events",
                    on_change=lambda e: print(f"Value: {e.value}"),
                ),
                "code": textwrap.dedent("""\
                    def handle_change(e):
                        print(e.value)           # Current value
                        print(e.previous_value)  # Previous value
                        print(e.id)              # Element id

                    input_text(
                        id="my_input",
                        placeholder="Type to see events",
                        on_change=handle_change,
                    )"""),
            }),

            component(example_with_code, props={
                "title": "Reading Value with Ref",
                "example": div(flex_direction="row", gap=8, align_items="center")[
                    input_text(id="ex_ref", placeholder="Type something"),
                    button("Log Value", on_click=lambda: print(
                        actions.user.ui_elements_get_input_value("ex_ref")
                    ), border_radius=4, padding=8, padding_top=6, padding_bottom=6),
                ],
                "code": textwrap.dedent("""\
                    ref = actions.user.ui_elements("ref")
                    my_ref = ref("my_input")

                    input_text(id="my_input", placeholder="Type something")
                    button("Log Value", on_click=lambda: print(my_ref.value))"""),
            }),
        ],
    ]
