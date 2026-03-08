from talon import actions
from ..common import (
    code, example_with_code, interactive_section,
    build_controls_state, build_preview_props,
    STRING, INT, COLOR, BOOL,
)
from .. import theme as t
import textwrap

CONTROLS = [
    ("placeholder", STRING, "Select..."),
    ("width", INT, "240"),
    ("border_radius", INT, "4"),
    ("border_width", INT, "0"),
    ("border_color", COLOR, ""),
    ("background_color", COLOR, ""),
    ("color", COLOR, ""),
    ("placeholder_color", COLOR, ""),
]

PREVIEW_OPTIONS = ["Small", "Medium", "Large"]

def select_stories():
    component, div, text, select, state = actions.user.ui_elements([
        "component", "div", "text", "select", "state"
    ])

    cs = build_controls_state(state, "sel", CONTROLS)
    preview_props = build_preview_props(CONTROLS, cs)
    preview_props["id"] = "sel_preview"
    preview_props["options"] = PREVIEW_OPTIONS

    selected, set_selected = state.use("sel_preview_value", "")
    if selected:
        preview_props["value"] = selected
    preview_props["on_change"] = lambda e: set_selected(e.value)

    return div(padding=32, gap=24)[
        text("Select", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                select = actions.user.ui_elements(['select'])""")
        ),

        interactive_section(
            element_name="select",
            preview_element=select(**preview_props),
            controls_spec=CONTROLS,
            controls_state=cs,
            prefix="sel",
            id_override="my_select",
        ),

        # Examples
        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component(example_with_code, props={
                "title": "String Options",
                "example": _string_options_example(div, select, text, state),
                "code": textwrap.dedent("""\
                    value, set_value = state.use("size", "Medium")

                    select(
                        id="size",
                        options=["Small", "Medium", "Large"],
                        value=value,
                        on_change=lambda e: set_value(e.value),
                    )"""),
            }),

            component(example_with_code, props={
                "title": "Dict Options (label/value)",
                "example": _dict_options_example(div, select, text, state),
                "code": textwrap.dedent("""\
                    value, set_value = state.use("color", "#FF0000")

                    select(
                        id="color",
                        options=[
                            {"label": "Red", "value": "#FF0000"},
                            {"label": "Green", "value": "#00FF00"},
                            {"label": "Blue", "value": "#0000FF"},
                        ],
                        value=value,
                        on_change=lambda e: set_value(e.value),
                    )"""),
            }),

            component(example_with_code, props={
                "title": "With Placeholder",
                "example": _placeholder_example(div, select, text, state),
                "code": textwrap.dedent("""\
                    select(
                        id="fruit",
                        options=["Apple", "Banana", "Cherry"],
                        placeholder="Pick a fruit...",
                        on_change=lambda e: set_value(e.value),
                    )"""),
            }),

            component(example_with_code, props={
                "title": "Styled Select",
                "example": _styled_example(div, select, text, state),
                "code": textwrap.dedent("""\
                    select(
                        id="styled",
                        options=["Option A", "Option B", "Option C"],
                        background_color="#1A1A2E",
                        color="#E94560",
                        border_radius=8,
                        border_width=1,
                        border_color="#E94560",
                        width=260,
                    )"""),
            }),

            component(example_with_code, props={
                "title": "With on_change Callback",
                "example": _onchange_example(div, select, text, state),
                "code": textwrap.dedent("""\
                    def handle_change(e):
                        print(e.value)           # Selected value
                        print(e.previous_value)  # Previous value
                        print(e.id)              # Element id

                    value, set_value = state.use("priority", "medium")

                    select(
                        id="priority",
                        options=["low", "medium", "high", "critical"],
                        value=value,
                        on_change=lambda e: (
                            set_value(e.value),
                            print(f"Changed to: {e.value}"),
                        ),
                    )"""),
            }),
        ],
    ]


def _string_options_example(div, select, text, state):
    value, set_value = state.use("ex_size", "Medium")
    return div(gap=8)[
        select(
            id="ex_size",
            options=["Small", "Medium", "Large"],
            value=value,
            on_change=lambda e: set_value(e.value),
        ),
        text(f"Selected: {value}", font_size=13, color=t.TEXT_SECONDARY),
    ]


def _dict_options_example(div, select, text, state):
    value, set_value = state.use("ex_color", "#FF0000")
    return div(gap=8)[
        select(
            id="ex_color",
            options=[
                {"label": "Red", "value": "#FF0000"},
                {"label": "Green", "value": "#00FF00"},
                {"label": "Blue", "value": "#0000FF"},
            ],
            value=value,
            on_change=lambda e: set_value(e.value),
        ),
        text(f"Selected: {value}", font_size=13, color=t.TEXT_SECONDARY),
    ]


def _placeholder_example(div, select, text, state):
    value, set_value = state.use("ex_fruit", "")
    return div(gap=8)[
        select(
            id="ex_fruit",
            options=["Apple", "Banana", "Cherry", "Date", "Elderberry"],
            value=value,
            placeholder="Pick a fruit...",
            on_change=lambda e: set_value(e.value),
        ),
        text(f"Selected: {value or '(none)'}", font_size=13, color=t.TEXT_SECONDARY),
    ]


def _styled_example(div, select, text, state):
    value, set_value = state.use("ex_styled_sel", "")
    return select(
        id="ex_styled_sel",
        options=["Option A", "Option B", "Option C"],
        value=value,
        background_color="#1A1A2E",
        color="#E94560",
        border_radius=8,
        border_width=1,
        border_color="#E94560",
        width=260,
        on_change=lambda e: set_value(e.value),
    )


def _onchange_example(div, select, text, state):
    value, set_value = state.use("ex_priority", "medium")
    return div(gap=8)[
        select(
            id="ex_priority",
            options=["low", "medium", "high", "critical"],
            value=value,
            on_change=lambda e: (
                set_value(e.value),
                print(f"Changed to: {e.value}"),
            ),
        ),
        text(f"Priority: {value}", font_size=13, color=t.TEXT_SECONDARY),
    ]
