from talon import actions, clip, cron
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import NodeCodeProperties, validate_combined_props
from .node_code import NodeCode
from .component import Component

CODE_ONLY_PROPS = {
    "language", "theme", "selectable", "selection_color",
    "font_family", "font_size", "font_style", "font_weight",
    "text_align", "white_space", "color", "stroke_width", "stroke_color",
}


def code_copy_impl(props):
    div, button, icon, state = actions.user.ui_elements(["div", "button", "icon", "state"])
    code_el = actions.user.ui_elements("code")
    copied, set_copied = state.use_local("code_copied", False)

    text_str = props.pop("_text", "")

    code_props = {}
    container_props = {}
    for k, v in props.items():
        if k in ("copyable", "id", "for_id", "type"):
            continue
        elif k in CODE_ONLY_PROPS:
            code_props[k] = v
        else:
            container_props[k] = v

    def on_copy(e):
        clip.set_text(text_str)
        set_copied(True)
        cron.after("2s", lambda: set_copied(False))

    return div(position="relative", **container_props)[
        code_el(text_str, **code_props),
        div(position="absolute", right=0, top=0)[
            button(
                on_click=on_copy,
                padding=8,
                border_radius=8,
            )[
                icon(
                    "check" if copied else "copy",
                    color="#55E055" if copied else "888888",
                    size=20,
                ),
            ]
        ]
    ]


def code(text_str: str = "", props=None, **additional_props):
    if isinstance(text_str, str):
        text_str = text_str.replace("\r\n", "\n")
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["code"])

    if properties.get("copyable"):
        component_props = {k: v for k, v in properties.items()}
        component_props["_text"] = text_str
        return Component(code_copy_impl, props=component_props)

    code_properties = NodeCodeProperties(**properties)
    return NodeCode(text_str, code_properties)
