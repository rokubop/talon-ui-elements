from talon import actions, clip, cron
from . import theme as t
from .src_utils import hex_color

# Control types for interactive panels
STRING = "string"
INT = "int"
COLOR = "color"
BOOL = "bool"
SELECT = "select"

def _is_valid_color(val):
    if not val:
        return False
    try:
        hex_color(val)
        return True
    except ValueError:
        return False

SMALL_INPUT_STYLE = {
    "background_color": t.BG_RAISED,
    "border_radius": 4,
    "border_width": 1,
    "border_color": t.BORDER,
    "width": 150,
    "font_size": 13,
    "height": 28,
}

def code(code_str: str):
    div, text = actions.user.ui_elements(["div", "text"])
    component = actions.user.ui_elements(["component"])

    return div(
            background_color=t.BG_CODE,
            border_radius=8,
            border_width=1,
            border_color=t.BORDER_SUBTLE,
            padding=24,
            color=t.TEXT_CODE,
            font_size=14,
            position="relative",
        )[
            text(code_str, font_family="monospace"),
            div(position="absolute", right=0, top=0)[
                component(copy_button, props={
                    "code": code_str
                })
            ]
        ]

def copy_button(props):
    button, icon, state = actions.user.ui_elements(["button", "icon", "state"])
    copied, set_copied = state.use_local(False)

    return button(
        on_click=lambda: (
            clip.set_text(props["code"]),
            set_copied(True),
            cron.after("2s", lambda: set_copied(False))
        ),
        padding=8,
        border_radius=8,
        color=t.TEXT_SECONDARY,
    )[
        icon(
            "check" if copied else "copy",
            color="#55E055" if copied else t.TEXT_SECONDARY,
            size=20,
        ),
    ]

def example_with_code(props):
    state, div, text = actions.user.ui_elements(["state", "div", "text"])
    button, component = actions.user.ui_elements(["button", "component"])
    show_code, set_show_code = state.use_local(False)

    return div(gap=8, flex_direction="column")[
        text(props["title"], font_size=18, font_weight="bold", color=t.TEXT),
        div(border_radius=8, border_width=1, border_color=t.BORDER, flex=1, position="relative", margin_top=8)[
            div(padding=16, min_height=100, align_items="center", justify_content="center")[
                props["example"],
            ],
            div(position="absolute", right=0, bottom=0)[
                button(
                    "Hide code" if show_code else "Show code",
                    on_click=lambda: set_show_code(not show_code),
                    padding=8,
                    border_radius=4,
                    border_width=1,
                    background_color=t.BG_RAISED,
                    color=t.TEXT_SECONDARY,
                    font_size=12,
                ),
            ],
        ],
        code(props["code"]) if show_code else None,
    ]

def control_row(label, control):
    div, text = actions.user.ui_elements(["div", "text"])
    return div(flex_direction="row", align_items="center", gap=12, min_height=32)[
        text(label, font_size=13, color=t.TEXT_SECONDARY, min_width=130),
        control,
    ]

def build_controls_state(state, prefix, controls):
    """Create state for each control. Returns dict of {name: (value, setter)}.

    controls is a list of tuples: (name, type, default, options?)
    - ("label", STRING, "Click me")
    - ("padding", INT, "12")
    - ("background_color", COLOR, "")
    - ("disabled", BOOL, False)
    - ("font_weight", SELECT, "normal", ["normal", "bold"])
    """
    result = {}
    for entry in controls:
        name = entry[0]
        default = entry[2]
        val, setter = state.use(f"{prefix}_{name}", default)
        result[name] = (val, setter)
    return result

def build_preview_props(controls_spec, controls_state):
    """Build a props dict from control values, skipping empty/invalid ones."""
    props = {}
    for entry in controls_spec:
        name = entry[0]
        ctrl_type = entry[1]
        val = controls_state[name][0]

        if ctrl_type == BOOL:
            if val:
                props[name] = True
        elif ctrl_type == COLOR:
            if _is_valid_color(val):
                props[name] = val
        elif ctrl_type == INT:
            try:
                props[name] = int(val)
            except (ValueError, TypeError):
                pass
        elif ctrl_type == SELECT:
            if val:
                props[name] = val
        else:  # STRING
            if val:
                props[name] = val
    return props

def build_code_string(element_name, preview_props, id_override=None):
    """Generate a code string from props dict."""
    props_lines = []
    for k, v in preview_props.items():
        if k == "id" and id_override:
            props_lines.append(f'    id="{id_override}"')
        elif isinstance(v, str):
            props_lines.append(f'    {k}="{v}"')
        elif isinstance(v, bool):
            props_lines.append(f'    {k}={v}')
        else:
            props_lines.append(f'    {k}={v}')
    return f"{element_name}(\n" + ",\n".join(props_lines) + ",\n)"

def render_controls_panel(controls_spec, controls_state, prefix):
    """Render the controls sidebar."""
    div, text, input_text, checkbox = actions.user.ui_elements([
        "div", "text", "input_text", "checkbox"
    ])

    rows = []
    for entry in controls_spec:
        name = entry[0]
        ctrl_type = entry[1]
        val, setter = controls_state[name]
        ctrl_id = f"{prefix}_{name}"

        if ctrl_type == BOOL:
            rows.append(control_row(name, checkbox(
                id=ctrl_id,
                checked=val,
                on_change=lambda e, s=setter: s(e.checked),
            )))
        elif ctrl_type == SELECT:
            options = entry[3] if len(entry) > 3 else []
            from talon import actions as a
            button = a.user.ui_elements("button")
            rows.append(control_row(name, div(flex_direction="row", gap=4)[
                *[button(
                    opt,
                    on_click=lambda e, o=opt, s=setter: s(o),
                    background_color=t.BG_ACTIVE if val == opt else t.BG_RAISED,
                    border_radius=4,
                    border_width=1,
                    border_color=t.BORDER if val == opt else t.BORDER_SUBTLE,
                    padding=4,
                    padding_left=8,
                    padding_right=8,
                    font_size=12,
                    color=t.TEXT if val == opt else t.TEXT_MUTED,
                ) for opt in options]
            ]))
        else:
            placeholder = ""
            if ctrl_type == COLOR:
                placeholder = "e.g. FF0000"
            rows.append(control_row(name, input_text(
                id=ctrl_id,
                value=str(val) if val else "",
                placeholder=placeholder,
                on_change=lambda e, s=setter: s(e.value),
                **SMALL_INPUT_STYLE,
            )))

    return div(
        min_width=300,
        border_left=1,
        border_color=t.BORDER,
        padding_left=16,
        gap=6,
        overflow_y="scroll",
    )[
        text("Controls", font_size=14, font_weight="bold", color=t.TEXT, margin_bottom=4),
        *rows,
    ]

def interactive_section(element_name, preview_element, controls_spec, controls_state, prefix, id_override=None):
    """Render a full interactive section: preview + code + controls."""
    div, text = actions.user.ui_elements(["div", "text"])

    preview_props = build_preview_props(controls_spec, controls_state)
    if id_override:
        preview_props["id"] = f"{prefix}_preview"
    code_str = build_code_string(element_name, preview_props, id_override=id_override)

    return div(gap=16)[
        text("Interactive", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

        div(flex_direction="row", gap=16)[
            # Left: Preview + code
            div(flex=1, gap=16)[
                div(
                    border_radius=8,
                    border_width=1,
                    border_color=t.BORDER,
                    padding=24,
                    min_height=120,
                    align_items="center",
                    justify_content="center",
                )[
                    preview_element,
                ],
                code(code_str),
            ],

            # Right: Controls
            render_controls_panel(controls_spec, controls_state, prefix),
        ],
    ]
