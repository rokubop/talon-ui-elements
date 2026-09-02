from talon import actions, clip, cron
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import NodeCodeProperties, validate_combined_props
from .node_code import NodeCode
from .component import Component

CODE_ONLY_PROPS = {
    "language", "theme", "diff", "selectable", "selection_color",
    "line_numbers", "line_number_start",
    "font_family", "font_size", "font_style", "font_weight",
    "text_align", "white_space", "color", "stroke_width", "stroke_color",
    "gap",
}

OVERFLOW_PROPS = {"overflow", "overflow_x", "overflow_y"}

PADDING_PROPS = {
    "padding", "padding_top", "padding_bottom",
    "padding_left", "padding_right", "padding_x", "padding_y",
}


def code_copy_impl(props):
    div, button, icon, state = actions.user.ui_elements(["div", "button", "icon", "state"])
    copied, set_copied = state.use_local("code_copied", False)

    text_str = props.pop("_text", "")

    code_props = {}
    container_props = {}
    overflow_props = {}
    padding_props = {}
    for k, v in props.items():
        if k in ("copyable", "for_id", "type"):
            continue
        elif k in CODE_ONLY_PROPS:
            code_props[k] = v
        elif k in OVERFLOW_PROPS:
            overflow_props[k] = v
        elif k in PADDING_PROPS:
            padding_props[k] = v
        else:
            container_props[k] = v

    def on_copy(e):
        clip.set_text(text_str)
        set_copied(True)
        cron.after("2s", lambda: set_copied(False))

    # Build the leaf NodeCode directly to bypass the public code() factory --
    # its defaults (copyable=True, overflow_x=auto) would re-enter this path
    # and infinite-recurse.
    code_content = NodeCode(text_str, NodeCodeProperties(**code_props))
    if overflow_props:
        code_content = div(**padding_props, **overflow_props)[code_content]
    else:
        container_props.update(padding_props)

    return div(position="relative", **container_props)[
        code_content,
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


def code_scroll_impl(props):
    """Wrap a non-copyable NodeCode in a scrollable div. NodeCode is a
    leaf text node and doesn't honor overflow on itself, so when the
    consumer sets overflow but disables the copy button, we still need
    a container around it for the scroll/clip to land on."""
    div = actions.user.ui_elements("div")

    text_str = props.pop("_text", "")

    code_props = {}
    wrap_props = {}
    for k, v in props.items():
        if k in ("copyable", "for_id", "type"):
            continue
        elif k in CODE_ONLY_PROPS:
            code_props[k] = v
        else:
            wrap_props[k] = v

    return div(**wrap_props)[
        NodeCode(text_str, NodeCodeProperties(**code_props)),
    ]


def code(text_str: str = "", props=None, **additional_props):
    if isinstance(text_str, str):
        text_str = text_str.replace("\r\n", "\n")
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["code"])
    # Match the NodeCodeProperties dataclass default: dataclass defaults
    # don't propagate through the validate_combined_props dict, so without
    # this the copyable-path (with wrapping scroll div) is never entered
    # unless the consumer passes copyable=True explicitly.
    properties.setdefault("copyable", True)
    # Code defaults to white_space="nowrap" -- without overflow_x, long
    # lines visibly escape the container. "auto" scrolls only when needed.
    # Not when the text can wrap: a scroll container never constrains its
    # child's width, so white_space="normal" would scroll instead of wrap.
    if "overflow_x" not in properties and "overflow" not in properties \
            and properties.get("white_space", "nowrap") == "nowrap":
        properties["overflow_x"] = "auto"

    if properties.get("copyable"):
        component_props = {k: v for k, v in properties.items()}
        component_props["_text"] = text_str
        return Component(code_copy_impl, props=component_props)

    # copyable=False but overflow is set: still wrap so the scroll/clip
    # has a container to attach to. NodeCode itself is a leaf.
    if any(k in properties for k in OVERFLOW_PROPS):
        component_props = {k: v for k, v in properties.items()}
        component_props["_text"] = text_str
        return Component(code_scroll_impl, props=component_props)

    code_properties = NodeCodeProperties(**properties)
    return NodeCode(text_str, code_properties)
