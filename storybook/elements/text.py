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
    ("font_style", SELECT, "normal", ["normal", "italic"]),
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
                "title": "Italic Text",
                "example": text(
                    "Italic text",
                    font_style="italic",
                    color="#AAAAAA",
                ),
                "code": textwrap.dedent("""\
                    text(
                        "Italic text",
                        font_style="italic",
                    )""")
            }),

            component(example_with_code, props={
                "title": "Multiline Text",
                "example": text(
                    "Line one\nLine two\nLine three",
                    color=t.TEXT,
                ),
                "code": textwrap.dedent("""\
                    text("Line one\\nLine two\\nLine three")""")
            }),

            component(example_with_code, props={
                "title": "Word Wrap (fixed width)",
                "example": text(
                    "This is a longer sentence that should automatically wrap when it exceeds the container width.",
                    color=t.TEXT,
                    width=250,
                ),
                "code": textwrap.dedent("""\
                    text(
                        "This is a longer sentence that should "
                        "automatically wrap...",
                        width=250,
                    )""")
            }),

            component(example_with_code, props={
                "title": "Code Block",
                "example": div(
                    background_color=t.BG_CODE,
                    border_radius=8,
                    padding=16,
                )[
                    text(
                        "def hello():\n    print('world')\n    return True",
                        font_family="monospace",
                        font_size=14,
                        color=t.TEXT_CODE,
                    ),
                ],
                "code": textwrap.dedent("""\
                    text(
                        "def hello():\\n    print('world')",
                        font_family="monospace",
                    )""")
            }),

            component(example_with_code, props={
                "title": "Selectable Text (drag to select, Ctrl+C to copy)",
                "example": text(
                    "Try selecting this text by clicking and dragging. "
                    "Press Ctrl+C to copy the selection.",
                    color=t.TEXT,
                    selectable=True,
                    width=350,
                ),
                "code": textwrap.dedent("""\
                    text(
                        "Try selecting this text...",
                        selectable=True,
                        width=350,
                    )""")
            }),

            component(example_with_code, props={
                "title": "Selectable Code Block",
                "example": div(
                    background_color=t.BG_CODE,
                    border_radius=8,
                    padding=16,
                )[
                    text(
                        'name = "world"\nprint(f"hello {name}")\n# output: hello world',
                        font_family="monospace",
                        font_size=14,
                        color=t.TEXT_CODE,
                        selectable=True,
                    ),
                ],
                "code": textwrap.dedent("""\
                    text(
                        'name = "world"\\nprint(f"hello {name}")',
                        font_family="monospace",
                        selectable=True,
                    )""")
            }),

            component(example_with_code, props={
                "title": "Inline bold (row of text elements)",
                "example": div(flex_direction="row")[
                    text("Press "),
                    text("enter", font_weight="bold"),
                    text(" to submit"),
                ],
                "code": textwrap.dedent("""\
                    div(flex_direction="row")[
                        text("Press "),
                        text("enter", font_weight="bold"),
                        text(" to submit"),
                    ]""")
            }),

            component(example_with_code, props={
                "title": "text_align",
                "example": div(gap=8, width=300)[
                    text("Left (default)", color=t.TEXT),
                    text("Center", text_align="center", color=t.TEXT),
                    text("Right", text_align="right", color=t.TEXT),
                ],
                "code": textwrap.dedent("""\
                    div(width=300)[
                        text("Left (default)"),
                        text("Center", text_align="center"),
                        text("Right", text_align="right"),
                    ]""")
            }),

            component(example_with_code, props={
                "title": "Custom Line Gap",
                "example": text(
                    "Tight spacing\nBetween these\nThree lines",
                    color=t.TEXT,
                    gap=4,
                ),
                "code": textwrap.dedent("""\
                    text(
                        "Tight spacing\\nBetween these\\nThree lines",
                        gap=4,
                    )""")
            }),

            component(example_with_code, props={
                "title": "Word Wrap (auto)",
                "example": div(width=300, background_color=t.BG_CODE, border_radius=8, padding=16)[
                    text(
                        "This text has no explicit width but will automatically wrap to fit within its parent container boundaries, just like in a web browser.",
                        color=t.TEXT,
                    ),
                ],
                "code": textwrap.dedent("""\
                    div(width=300, padding=16)[
                        text(
                            "This text has no explicit width "
                            "but will automatically wrap...",
                        ),
                    ]""")
            }),

            component(example_with_code, props={
                "title": "No Wrap (white_space)",
                "example": div(width=300, background_color=t.BG_CODE, border_radius=8, padding=16, overflow_x="scroll")[
                    text(
                        "This text will not wrap because white_space is set to nowrap. It overflows instead.",
                        color=t.TEXT,
                        white_space="nowrap",
                    ),
                ],
                "code": textwrap.dedent("""\
                    div(width=300, overflow_x="scroll")[
                        text(
                            "This text will not wrap...",
                            white_space="nowrap",
                        ),
                    ]""")
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
