from talon import actions
from ..common import example_with_code, code
import textwrap

def checkbox_stories():
    component, div, text, checkbox, icon, input_text = actions.user.ui_elements([
        "component", "div", "text", "checkbox", "icon", "input_text"
    ])

    return div(padding=32, gap=24)[
        text("Checkbox", font_size=22, font_weight="bold", color="#F1F1F1"),
        code(
            textwrap.dedent("""\
                checkbox = actions.user.ui_elements(['checkbox'])"""
            )
        ),

        div(gap=16)[
            text("Stories", font_size=18, font_weight="bold", color="#F1F1F1", border_bottom=1, padding_bottom=12,border_color="#333333"),
            component(example_with_code, props={
                "title": "Default Checkbox",
                "example": checkbox(),
                "code": textwrap.dedent("""\
                    checkbox()"""
                )
            }),
            component(example_with_code, props={
                "title": "With label",
                "example": div(
                    flex_direction="row",
                    align_items="center",
                    gap=8,
                )[
                    checkbox(id="a"),
                    text("Label", for_id="a")
                ],
                "code": textwrap.dedent("""\
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(id="a"),
                        text("Label", for_id="a")
                    ]"""
                )
            }),
            component(example_with_code, props={
                "title": "Disabled",
                "example": div(
                    flex_direction="row",
                    align_items="center",
                    gap=8,
                )[
                    checkbox(id="b", disabled=True),
                    text("Label", for_id="b")
                ],
                "code": textwrap.dedent("""\
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(id="b", disabled=True),
                        text("Label", for_id="b")
                    ]"""
                )
            }),
        ],
    ]
