from talon import actions
from ..common import example_with_code, code
import textwrap

def button_stories():
    component, div, text, button, icon, input_text = actions.user.ui_elements([
        "component", "div", "text", "button", "icon", "input_text"
    ])

    return div(padding=32, gap=24)[
        text("Button", font_size=22, font_weight="bold", color="#F1F1F1"),
        code(
            textwrap.dedent("""\
                button = actions.user.ui_elements(['button'])"""
            )
        ),

        div(gap=16)[
            text("Stories", font_size=18, font_weight="bold", color="#F1F1F1", border_bottom=1, padding_bottom=12,border_color="#333333"),

            component(example_with_code, props={
                "title": "Default Button",
                "example": button("Default", on_click=lambda: print("Button clicked!")),
                "code": textwrap.dedent("""\
                    button('Default', on_click=lambda: print("Button clicked!"))"""
                )
            }),

            component(example_with_code, props={
                "title": "With common properties",
                "example": button(
                    "Default",
                    padding=12,
                    border_radius=6,
                    background_color="#3689E8",
                    on_click=lambda: print("Button clicked!"),
                    color="#F1F1F1",
                    highlight_style={
                        "background_color": "#E24A70",
                    }
                ),
                "code": textwrap.dedent("""\
                    button(
                        'Default',
                        padding=12,
                        border_radius=6,
                        on_click=lambda: print("Button clicked!"),
                        background_color='#3689E8',
                        color='#F1F1F1',
                        highlight_style={
                            "background_color": "#E24A70",
                        }
                    )"""
                )
            }),

            component(example_with_code, props={
                "title": "With children (icon + text)",
                "example": button(
                    flex_direction="row",
                    align_items="center",
                    gap=6,
                    padding=12,
                    on_click=lambda: print("Button clicked!"),
                    border_radius=6,
                    border_width=1,
                    border_color="#333333",
                    background_color="#23242A",
                )[
                    icon("plus", size=16, color="#F1F1F1"),
                    text("Icon Button", color="#F1F1F1")
                ],
                "code": textwrap.dedent("""\
                    button(
                        flex_direction='row',
                        align_items='center',
                        gap=6,
                        padding=12,
                        on_click=lambda: print("Button clicked!"),
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

            component(example_with_code, props={
                "title": "Disabled Button",
                "example": button(
                    "Default",
                    padding=12,
                    border_radius=6,
                    on_click=lambda: print("Button clicked!"),
                    background_color="#3689E8",
                    color="#F1F1F1",
                    disabled=False,
                    disabled_style={
                        "background_color": "#555555",
                        "color": "#969696",
                    },
                ),
                "code": textwrap.dedent("""\
                    button(
                        'Default',
                        padding=12,
                        border_radius=6,
                        on_click=lambda: print("Button clicked!"),
                        background_color='#3689E8',
                        color='#F1F1F1',
                        disabled=True,
                        disabled_style={
                            "background_color": "#555555",
                            "color": "#CCCCCC",
                        },
                    )"""
                )
            }),
        ],
    ]
