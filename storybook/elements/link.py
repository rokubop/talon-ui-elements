from talon import actions
from ..common import example_with_code, code
import textwrap

def link_stories():
    component, div, text, link, icon, input_text = actions.user.ui_elements([
        "component", "div", "text", "link", "icon", "input_text"
    ])

    return div(padding=32, gap=24)[
        text("Link", font_size=22, font_weight="bold", color="#F1F1F1"),
        code(
            textwrap.dedent("""\
                link = actions.user.ui_elements(['link'])"""
            )
        ),

        div(gap=16)[
            text("Stories", font_size=18, font_weight="bold", color="#F1F1F1", border_bottom=1, padding_bottom=12,border_color="#333333"),
            component(example_with_code, props={
                "title": "Default Link",
                "example": link("Default"),
                "code": textwrap.dedent("""\
                    link('Default')"""
                )
            }),
            component(example_with_code, props={
                "title": "With common properties",
                "example": link(
                    "Default",
                    padding=12,
                    border_radius=6,
                    background_color="#3689E8",
                    color="#F1F1F1",
                ),
                "code": textwrap.dedent("""\
                    link(
                        'Default',
                        padding=12,
                        border_radius=6,
                        background_color='#3689E8',
                        color='#F1F1F1'
                    )"""
                )
            }),
            component(example_with_code, props={
                "title": "With children (icon + text)",
                "example": link(
                    flex_direction="row",
                    align_items="center",
                    gap=6,
                    padding=12,
                    border_radius=6,
                    border_width=1,
                    border_color="#333333",
                    background_color="#23242A",
                )[
                    icon("plus", size=16, color="#F1F1F1"),
                    text("Icon Button", color="#F1F1F1")
                ],
                "code": textwrap.dedent("""\
                    link(
                        flex_direction='row',
                        align_items='center',
                        gap=6,
                        padding=12,
                        border_radius=6,
                        border_width=1,
                        border_color='#333333',
                        background_color='#23242A',
                    )[
                        icon('plus', size=16, color='#F1F1F1'),
                        text('Icon Button', color='#F1F1F1')
                    ]"""
                )
            }),
        ],
    ]
