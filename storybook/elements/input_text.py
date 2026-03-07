from talon import actions
from ..common import example_with_code, code
import textwrap

def input_text_stories():
    component, div, text, input_text, ref = actions.user.ui_elements([
        "component", "div", "text", "input_text", "ref"
    ])

    return div(padding=32, gap=24)[
        text("Input Text", font_size=22, font_weight="bold", color="#F1F1F1"),
        code(
            textwrap.dedent("""\
                input_text = actions.user.ui_elements(['input_text'])"""
            )
        ),

        div(gap=16)[
            text("Stories", font_size=18, font_weight="bold", color="#F1F1F1", border_bottom=1, padding_bottom=12, border_color="#333333"),

            component(example_with_code, props={
                "title": "Default Input",
                "example": input_text(id="story_default"),
                "code": textwrap.dedent("""\
                    input_text(id="my_input")"""
                )
            }),

            component(example_with_code, props={
                "title": "With Placeholder",
                "example": input_text(
                    id="story_placeholder",
                    placeholder="Search...",
                ),
                "code": textwrap.dedent("""\
                    input_text(
                        id="my_input",
                        placeholder="Search...",
                    )"""
                )
            }),

            component(example_with_code, props={
                "title": "Custom Placeholder Color",
                "example": input_text(
                    id="story_placeholder_color",
                    placeholder="Type here...",
                    placeholder_color="FF888888",
                ),
                "code": textwrap.dedent("""\
                    input_text(
                        id="my_input",
                        placeholder="Type here...",
                        placeholder_color="FF888888",
                    )"""
                )
            }),

            component(example_with_code, props={
                "title": "Custom Cursor Color",
                "example": input_text(
                    id="story_cursor_color",
                    placeholder="Orange cursor",
                    cursor_color="FF8800",
                ),
                "code": textwrap.dedent("""\
                    input_text(
                        id="my_input",
                        placeholder="Orange cursor",
                        cursor_color="FF8800",
                    )"""
                )
            }),

            component(example_with_code, props={
                "title": "Custom Selection Color",
                "example": input_text(
                    id="story_selection_color",
                    placeholder="Select text to see",
                    selection_color="FF440088",
                ),
                "code": textwrap.dedent("""\
                    input_text(
                        id="my_input",
                        placeholder="Select text to see",
                        selection_color="FF440088",
                    )"""
                )
            }),

            component(example_with_code, props={
                "title": "Styled Input",
                "example": input_text(
                    id="story_styled",
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
                    )"""
                )
            }),

            component(example_with_code, props={
                "title": "With Initial Value",
                "example": input_text(
                    id="story_value",
                    value="Hello world",
                ),
                "code": textwrap.dedent("""\
                    input_text(
                        id="my_input",
                        value="Hello world",
                    )"""
                )
            }),

            component(example_with_code, props={
                "title": "Autofocus",
                "example": input_text(
                    id="story_autofocus",
                    placeholder="I'm focused on load",
                    autofocus=True,
                ),
                "code": textwrap.dedent("""\
                    input_text(
                        id="my_input",
                        placeholder="I'm focused on load",
                        autofocus=True,
                    )"""
                )
            }),
        ],
    ]
