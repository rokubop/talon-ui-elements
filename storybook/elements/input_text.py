from talon import actions
from ..common import code, example_with_code
from .. import theme as t
import textwrap

def _is_valid_color(val):
    if not val:
        return False
    from ...src.utils import hex_color
    try:
        hex_color(val)
        return True
    except ValueError:
        return False

def control_row(label, control):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(flex_direction="row", align_items="center", gap=12, min_height=32)[
        text(label, font_size=13, color=t.TEXT_SECONDARY, min_width=130),
        control,
    ]

def input_text_stories():
    component, div, text, input_text, checkbox, state, button = actions.user.ui_elements([
        "component", "div", "text", "input_text", "checkbox", "state", "button"
    ])

    # Controls state
    placeholder, set_placeholder = state.use("it_placeholder", "Search...")
    value, set_value = state.use("it_value", "")
    bg_color, set_bg_color = state.use("it_bg_color", "")
    text_color, set_text_color = state.use("it_text_color", "")
    p_color, set_p_color = state.use("it_p_color", "")
    sel_color, set_sel_color = state.use("it_sel_color", "")
    cur_color, set_cur_color = state.use("it_cur_color", "")
    radius, set_radius = state.use("it_radius", "4")
    width, set_width = state.use("it_width", "300")
    border_w, set_border_w = state.use("it_border_w", "0")
    border_c, set_border_c = state.use("it_border_c", "")
    autofocus, set_autofocus = state.use("it_autofocus", False)

    def safe_int(val, default=0):
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    # Build props dict for preview, only include non-empty values
    preview_props = {"id": "it_preview"}
    if placeholder:
        preview_props["placeholder"] = placeholder
    if value:
        preview_props["value"] = value
    if _is_valid_color(bg_color):
        preview_props["background_color"] = bg_color
    if _is_valid_color(text_color):
        preview_props["color"] = text_color
    if _is_valid_color(p_color):
        preview_props["placeholder_color"] = p_color
    if _is_valid_color(sel_color):
        preview_props["selection_color"] = sel_color
    if _is_valid_color(cur_color):
        preview_props["cursor_color"] = cur_color
    if radius:
        preview_props["border_radius"] = safe_int(radius)
    if width:
        preview_props["width"] = safe_int(width, 300)
    if border_w:
        preview_props["border_width"] = safe_int(border_w)
    if _is_valid_color(border_c):
        preview_props["border_color"] = border_c
    if autofocus:
        preview_props["autofocus"] = True

    # Build code string from current props
    props_lines = []
    for k, v in preview_props.items():
        if k == "id":
            props_lines.append(f'    id="my_input"')
        elif isinstance(v, str):
            props_lines.append(f'    {k}="{v}"')
        elif isinstance(v, bool):
            props_lines.append(f'    {k}={v}')
        else:
            props_lines.append(f'    {k}={v}')
    code_str = "input_text(\n" + ",\n".join(props_lines) + ",\n)"

    small_input_style = {
        "background_color": t.BG_ACTIVE,
        "border_radius": 4,
        "border_width": 1,
        "border_color": t.BORDER_SUBTLE,
        "width": 150,
        "font_size": 13,
        "height": 28,
    }

    return div(padding=32, gap=24)[
        text("Input Text", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                input_text = actions.user.ui_elements(['input_text'])"""
            )
        ),

        text("Interactive", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

        div(flex_direction="row", gap=16)[
            # Left: Preview + code
            div(flex=1, gap=16)[
                # Preview
                div(
                    border_radius=8,
                    border_width=1,
                    border_color=t.BORDER,
                    padding=24,
                    min_height=120,
                    align_items="center",
                    justify_content="center",
                )[
                    input_text(**preview_props),
                ],

                # Generated code
                code(code_str),
            ],

            # Right: Controls sidebar
            div(
                min_width=300,
                border_left=1,
                border_color=t.BORDER,
                padding_left=16,
                gap=6,
                overflow_y="scroll",
            )[
                text("Controls", font_size=14, font_weight="bold", color=t.TEXT, margin_bottom=4),

                control_row("placeholder", input_text(
                    id="ctrl_placeholder", value=placeholder,
                    on_change=lambda e: set_placeholder(e.value),
                    **small_input_style,
                )),
                control_row("value", input_text(
                    id="ctrl_value", value=value,
                    on_change=lambda e: set_value(e.value),
                    **small_input_style,
                )),
                control_row("width", input_text(
                    id="ctrl_width", value=width,
                    on_change=lambda e: set_width(e.value),
                    **small_input_style,
                )),
                control_row("border_radius", input_text(
                    id="ctrl_radius", value=radius,
                    on_change=lambda e: set_radius(e.value),
                    **small_input_style,
                )),
                control_row("border_width", input_text(
                    id="ctrl_border_w", value=border_w,
                    on_change=lambda e: set_border_w(e.value),
                    **small_input_style,
                )),
                control_row("border_color", input_text(
                    id="ctrl_border_c", value=border_c,
                    placeholder="e.g. FF0000",
                    on_change=lambda e: set_border_c(e.value),
                    **small_input_style,
                )),
                control_row("background_color", input_text(
                    id="ctrl_bg", value=bg_color,
                    placeholder="e.g. 222222",
                    on_change=lambda e: set_bg_color(e.value),
                    **small_input_style,
                )),
                control_row("color", input_text(
                    id="ctrl_color", value=text_color,
                    placeholder="e.g. FF0000",
                    on_change=lambda e: set_text_color(e.value),
                    **small_input_style,
                )),
                control_row("placeholder_color", input_text(
                    id="ctrl_p_color", value=p_color,
                    placeholder="e.g. FFFFFF55",
                    on_change=lambda e: set_p_color(e.value),
                    **small_input_style,
                )),
                control_row("selection_color", input_text(
                    id="ctrl_sel_color", value=sel_color,
                    placeholder="e.g. 4488FF88",
                    on_change=lambda e: set_sel_color(e.value),
                    **small_input_style,
                )),
                control_row("cursor_color", input_text(
                    id="ctrl_cur_color", value=cur_color,
                    placeholder="e.g. FF8800",
                    on_change=lambda e: set_cur_color(e.value),
                    **small_input_style,
                )),
                control_row("autofocus", checkbox(
                    id="ctrl_autofocus",
                    checked=autofocus,
                    on_change=lambda e: set_autofocus(e.checked),
                )),
            ],
        ],

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
