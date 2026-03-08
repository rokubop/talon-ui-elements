from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    STRING, INT, COLOR, SELECT,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("text", STRING, "Hello world"),
    ("font_size", INT, "16"),
    ("font_weight", SELECT, "normal", ["normal", "bold"]),
    ("color", COLOR, ""),
    ("text_align", SELECT, "left", ["left", "center", "right"]),
]

def text_stories():
    component, div, text, state = actions.user.ui_elements([
        "component", "div", "text", "state"
    ])

    cs = build_controls_state(state, "txt", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)

    # Extract text content from props
    txt_content = preview_props.pop("text", "Hello world")

    return div(padding=32, gap=24)[
        text("Text", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                text = actions.user.ui_elements(['text'])""")
        ),

        interactive_section(
            element_name="text",
            preview_element=text(txt_content, **preview_props),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="txt",
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Default Text",
                "example": text("Hello world"),
                "code": textwrap.dedent("""\
                    text("Hello world")""")
            }),

            component(example_with_code, props={
                "title": "Styled Text",
                "example": text(
                    "Styled text",
                    font_size=24,
                    font_weight="bold",
                    color="#3689E8",
                ),
                "code": textwrap.dedent("""\
                    text(
                        "Styled text",
                        font_size=24,
                        font_weight="bold",
                        color="#3689E8",
                    )""")
            }),

            component(example_with_code, props={
                "title": "With Label (for_id)",
                "example": text("Links to checkbox via for_id", color=t.TEXT_SECONDARY),
                "code": textwrap.dedent("""\
                    checkbox(id="my_checkbox")
                    text("Label", for_id="my_checkbox")""")
            }),
        ],
    ]
