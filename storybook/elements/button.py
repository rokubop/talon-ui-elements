from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    STRING, INT, COLOR, BOOL, SELECT,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("text", STRING, "Click me"),
    ("padding", INT, "12"),
    ("border_radius", INT, "6"),
    ("border_width", INT, "0"),
    ("border_color", COLOR, ""),
    ("background_color", COLOR, ""),
    ("color", COLOR, ""),
    ("font_size", INT, "16"),
    ("font_weight", SELECT, "normal", ["normal", "bold"]),
    ("disabled", BOOL, False),
]

def button_stories():
    component, div, text, button, icon, state = actions.user.ui_elements([
        "component", "div", "text", "button", "icon", "state"
    ])

    cs = build_controls_state(state, "btn", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)

    # Extract text prop for button label
    btn_text = preview_props.pop("text", "Click me")
    preview_props["on_click"] = lambda: print("Button clicked!")

    return div(padding=32, gap=24)[
        text("Button", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                button = actions.user.ui_elements(['button'])""")
        ),

        interactive_section(
            element_name="button",
            preview_element=button(btn_text, **preview_props),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="btn",
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "Default Button",
                "example": button("Default", on_click=lambda: print("Button clicked!")),
                "code": textwrap.dedent("""\
                    button('Default', on_click=lambda: print("Button clicked!"))""")
            }),

            component(example_with_code, props={
                "title": "Styled Button",
                "example": button(
                    "Styled",
                    padding=12,
                    border_radius=6,
                    background_color="#3689E8",
                    on_click=lambda: print("Button clicked!"),
                    color=t.TEXT,
                    highlight_style={
                        "background_color": "#E24A70",
                    }
                ),
                "code": textwrap.dedent("""\
                    button(
                        'Styled',
                        padding=12,
                        border_radius=6,
                        background_color='#3689E8',
                        on_click=lambda: print("Button clicked!"),
                        color='#F1F1F1',
                        highlight_style={
                            "background_color": "#E24A70",
                        }
                    )""")
            }),

            component(example_with_code, props={
                "title": "With Children (icon + text)",
                "example": button(
                    flex_direction="row",
                    align_items="center",
                    gap=6,
                    padding=12,
                    on_click=lambda: print("Button clicked!"),
                    border_radius=6,
                    border_width=1,
                    border_color=t.BORDER,
                    background_color=t.BG_ACTIVE,
                )[
                    icon("plus", size=16, color=t.TEXT),
                    text("Icon Button", color=t.TEXT)
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
                    ]""")
            }),

            component(example_with_code, props={
                "title": "Disabled Button",
                "example": button(
                    "Disabled",
                    padding=12,
                    border_radius=6,
                    on_click=lambda: print("Button clicked!"),
                    background_color="#3689E8",
                    color=t.TEXT,
                    disabled=True,
                    disabled_style={
                        "background_color": "#555555",
                        "color": "#969696",
                    },
                ),
                "code": textwrap.dedent("""\
                    button(
                        'Disabled',
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
                    )""")
            }),
        ],
    ]
