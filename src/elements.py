from talon import ctrl
from typing import List, Dict, Any, Union
from .constants import ELEMENT_ENUM_TYPE
from .core.state_manager import state_manager
from .effect import use_effect, use_effect_no_tree
from .nodes.component import Component
from .nodes.checkbox import checkbox
from .nodes.link import link
from .nodes.node_container import NodeContainer
from .nodes.node_cursor import NodeCursor
from .nodes.node_input_text import NodeInputText
from .nodes.node_root import NodeRoot
from .nodes.node_svg import (
    NodeSvg,
    NodeSvgPath,
    NodeSvgRect,
    NodeSvgCircle,
    NodeSvgPolyline,
    NodeSvgLine,
)
from .nodes.node_table import NodeTable, NodeTableRow, NodeTableData, NodeTableHeader
from .nodes.node_text import NodeText
from .nodes.node_button import NodeButton
from .nodes.switch import switch
from .nodes.node_window import NodeWindow
from .nodes.node_modal import NodeModal
from .properties import (
    NodeInputTextProperties,
    NodeRootProperties,
    NodeDivProperties,
    NodeCursorProperties,
    NodeTableProperties,
    NodeTableDataProperties,
    NodeTableHeaderProperties,
    NodeTableRowProperties,
    NodeTextProperties,
    NodeSvgProperties,
    NodeSvgPathProperties,
    NodeSvgRectProperties,
    NodeSvgCircleProperties,
    NodeSvgPolylineProperties,
    NodeSvgPolygonProperties,
    NodeSvgLineProperties,
    NodeWindowProperties,
    NodeModalProperties,
    combine_props,
    validate_props,
    validate_combined_props
)
from .icons import icon
from .ref import Ref
from .style import Style

def screen(*args, **additional_props):
    """
    ```py
    # Top left align children:
    screen(justify_content="flex_start", align_items="flex_start")

    # Center align children:
    screen(justify_content="center", align_items="center")

    # Bottom right align children:
    screen(justify_content="flex_end", align_items="flex_end")

    # Specify a screen index:
    screen(1, justify_content="center", align_items="center")

    # Use a dictionary instead:
    screen({"justify_content": "center", "align_items": "center"})
    ```
    """
    props = None
    if len(args) == 1 and isinstance(args[0], dict):
        props = args[0]
    elif len(args) == 1:
        props = { "screen": args[0] }
    elif len(args) > 1:
        props = args[1]
        props["screen"] = args[0]

    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["screen"])

    root = NodeRoot(
        ELEMENT_ENUM_TYPE["screen"],
        NodeRootProperties(**properties)
    )
    return root

def active_window(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["active_window"])

    root = NodeRoot(
        ELEMENT_ENUM_TYPE["active_window"],
        NodeRootProperties(**properties)
    )
    return root

class State:
    def get(self, key: str, initial_state: Any = None):
        tree = state_manager.get_processing_tree()
        components = state_manager.get_processing_components()
        if not tree:
            raise ValueError("""
                state.get() must be called during render, such as during ui_elements_show(ui).
                If you want to use state outside of a render, use actions.user.ui_elements_get_state(),
                actions.user.ui_elements_set_state(), actions.user.ui_elements_set_initial_state()
            """)

        tree.meta_state.associate_state(key, components)
        return get_state(key, initial_state)

    def use(self, key: str, initial_state: Any = None):
        tree = state_manager.get_processing_tree()
        components = state_manager.get_processing_components()
        if not tree:
            raise ValueError("""
                state.use() must be called during render, such as during ui_elements_show(ui).
                If you want to use state outside of a render, use actions.user.ui_elements_get_state(),
                actions.user.ui_elements_set_state(), actions.user.ui_elements_set_initial_state()
            """)

        tree.meta_state.associate_state(key, components)
        return use_state(key, initial_state)

    def set(self, key: str, value: Any):
        set_state(key, value)

    def use_local(self, key: str, initial_state: Any = None):
        tree = state_manager.get_processing_tree()
        components = state_manager.get_processing_components()
        if not components:
            raise ValueError("""
                state.use_local() must be used inside a component.
            """)
        if not tree:
            raise ValueError("""
                state.use_local() must be called during render, such as during ui_elements_show(ui).
                If you want to use state outside of a render, use actions.user.ui_elements_get_state(),
                actions.user.ui_elements_set_state(), actions.user.ui_elements_set_initial_state()
            """)
        last_component = components[-1]
        unique_key = f"{tree.name}_{key}_{last_component.name}_{last_component.id}"
        tree.meta_state.associate_local_state(unique_key, last_component)
        return use_state(unique_key, initial_state)

    def __call__(self, *args, **kwargs):
        raise ValueError("""
            Cannot call state() directly. Instead use one of the following:
            value = state.get("key", optional_initial_value)
            value, set_value = state.use("key", optional_initial_value)
            value, set_value = state.use_local("key", optional_initial_value)
            state.set("key", new_value)
        """)

def use_state(key: str, initial_state: Any = None):
    return state_manager.use_state(key, initial_state)

def get_state(key: str, initial_state: Any = None):
    value, _ = use_state(key, initial_state)
    return value

def set_state(key: str, value: Any):
   state_manager.set_state_value(key, value)

def style(style_dict: dict[str, Any]):
    context = state_manager.get_processing_component() \
        or state_manager.get_processing_tree()
    if context:
        context.style = Style(style_dict)

def div(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["div"])
    div_properties = NodeDivProperties(**properties)
    return NodeContainer(ELEMENT_ENUM_TYPE["div"], div_properties)

def cursor(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["cursor"])

    outer_properties = {
        "position": "absolute",
        "left": 0,
        "top": 0,
    }

    inner_defaults = {
        "position": "absolute",
    }

    user_has_horizontal = any(properties.get(prop) is not None for prop in ["left", "right"])
    if not user_has_horizontal:
        inner_defaults["left"] = 0

    user_has_vertical = any(properties.get(prop) is not None for prop in ["top", "bottom"])
    if not user_has_vertical:
        inner_defaults["top"] = 0

    inner_properties = {
        **inner_defaults,
        **properties,
    }

    return NodeCursor(
        outer_properties=outer_properties,
        inner_properties=inner_properties
    )

def table(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["table"])
    table_properties = NodeTableProperties(**{
        **properties,
        "flex_direction": "row",
    })
    return NodeTable(table_properties)

def tr(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["tr"])
    table_row_properties = NodeTableRowProperties(**properties)
    return NodeTableRow(table_row_properties)

def td(*args, **additional_props):
    text_content = None

    # Check if 'text' was passed as a keyword argument and rename it to avoid conflict
    if 'text' in additional_props:
        text_content = additional_props.pop('text')

    if args and isinstance(args[0], str):
        text_content = args[0]
        args = args[1:]

    props = args[0] if args and isinstance(args[0], dict) else {}

    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["td"])
    table_data_properties = NodeTableDataProperties(**properties)
    td_node = NodeTableData(table_data_properties)

    if text_content:
        text_node = text(text_content)
        td_node.add_child(text_node)

    return td_node

def th(*args, **additional_props):
    text_content = None

    if 'text' in additional_props:
        text_content = additional_props.pop('text')

    if args and isinstance(args[0], str):
        text_content = args[0]
        args = args[1:]

    props = args[0] if args and isinstance(args[0], dict) else {}

    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["th"])
    table_header_properties = NodeTableHeaderProperties(**properties)
    th_node = NodeTableHeader(table_header_properties)

    if text_content:
        text_node = text(text_content)
        th_node.add_child(text_node)

    return th_node

def text(text_str: str = "", props=None, **additional_props):
    if isinstance(text_str, str):
        lines = text_str.replace("\r\n", "\n").split("\n")
        if len(lines) > 1:
            return div()[
                *[text(line, props=props, **additional_props) for line in lines]
            ]
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["text"])
    text_properties = NodeTextProperties(**properties)
    return NodeText(ELEMENT_ENUM_TYPE["text"], text_str, text_properties)

def button(*args, text=None, **additional_props):
    if args and isinstance(args[0], str):
        text = args[0]
        args = args[1:]

    props = args[0] if args and isinstance(args[0], dict) else {}

    all_props = combine_props(props, additional_props)

    properties = validate_props(
        all_props,
        ELEMENT_ENUM_TYPE["button"]
    )

    if text:
        properties["type"] = "button"
        text_properties = NodeTextProperties(**{
            "padding": 8,
            **properties
        })
        return NodeText(ELEMENT_ENUM_TYPE["button"], text, text_properties)

    if all_props.get("element_type", None):
        properties["element_type"] = all_props["element_type"]

    button_properties = NodeTextProperties(**properties)
    return NodeButton(button_properties)

def input_text(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["input_text"])
    input_properties = NodeInputTextProperties(**properties)
    if not input_properties.id:
        raise ValueError("input_text must have an id prop so that it can be targeted with actions.user.ui_elements_get_value(id)")
    return NodeInputText(input_properties)

def window(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["window"])

    window_properties = {}
    body_properties = {}

    for key, value in properties.items():
        if key in [
            "position",
            "top",
            "left",
            "right",
            "bottom",
            "width",
            "min_width",
            "min_height",
            "margin",
            "margin_top",
            "margin_bottom",
            "margin_left",
            "margin_right",
            "max_width",
            "max_height",
            "minimized",
            "minimized_body",
            "minimized_style",
            "height",
            "z_index",
            "background_color",
            "border_radius",
            "border_width",
            "border_color",
            "drop_shadow",
            "on_minimize",
            "on_restore",
            "on_close",
            "title",
            "show_title_bar",
            "show_close",
            "show_minimize",
            "title_bar_style",
        ]:
            window_properties[key] = value
        else:
            body_properties[key] = value

    return NodeWindow(
        window_properties=window_properties,
        body_properties=body_properties,
    )

modal_only_props = {
    "open",
    "on_close",
    "show_title_bar",
    "backdrop",
    "backdrop_color",
    "backdrop_click_close",
    "title",
}

def split_modal_props(props: dict[str, Any]):
    modal_props = {}
    contents_props = {}

    for prop in props:
        # print(f"prop: {prop}")
        if prop in modal_only_props:
            modal_props[prop] = props[prop]
        else:
            contents_props[prop] = props[prop]

    return modal_props, contents_props

def modal(title=None, open=False, on_close=None, draggable=False, show_title_bar=True,
         backdrop=True, backdrop_color="00000080", backdrop_click_close=True, props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["modal"])
    modal_props, contents_props = split_modal_props({
        **properties,
        "title": title,
        "open": open,
        "on_close": on_close,
        "draggable": draggable,
        "show_title_bar": show_title_bar,
        "background_color": "222222",
        "border_width": 1,
        "drop_shadow": (0, 20, 25, 25, "000000CC"),
        "backdrop": backdrop,
        "backdrop_color": backdrop_color,
        "backdrop_click_close": backdrop_click_close
    })
    return NodeModal(
        NodeModalProperties(
            **modal_props,
            width="100%",
            height="100%",
            position="absolute",
            justify_content="center",
            align_items="center"
        ),
        contents_props,
    )

class UIElementsContainerNoTextProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"You must call {self.func.__name__}() before declaring children. Use {self.func.__name__}()[..] instead of {self.func.__name__}[..].")

    def __call__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, str):
                raise ValueError(f"Tried to provide a string argument to a ui_element that doesn't accept it. Use text() if you want to display a string.")

        return self.func(*args, **kwargs)

class UIElementsWindowProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"You must call {self.func.__name__}() before declaring children. Use {self.func.__name__}()[..] instead of {self.func.__name__}[..].")

    def __call__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, str):
                raise ValueError(f"Use property 'title' to set the window title instead of passing a string argument.")

        return self.func(*args, **kwargs)

class UIElementsProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"You must call {self.func.__name__}() before declaring children. Use {self.func.__name__}()[..] instead of {self.func.__name__}[..].")

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

class UIElementsInputTextProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"{self.func.__name__} does not support children. Use {self.func.__name__}().")

    def __call__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, str):
                raise ValueError(f"Cannot provide a string argument to a input_text. To create a label, use text() next to the input_text.")

        return self.func(*args, **kwargs)

class UIElementsLeafProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"{self.func.__name__} does not support children. Use {self.func.__name__}().")

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

use_effect_without_tree = use_effect_no_tree

active_window = UIElementsContainerNoTextProxy(active_window)
button = UIElementsLeafProxy(button)
checkbox = UIElementsLeafProxy(checkbox)
cursor = UIElementsContainerNoTextProxy(cursor)
div = UIElementsContainerNoTextProxy(div)
effect = use_effect
icon = UIElementsLeafProxy(icon)
input_text = UIElementsInputTextProxy(input_text)
modal = UIElementsContainerNoTextProxy(modal)
ref = Ref
screen = UIElementsContainerNoTextProxy(screen)
state = State()
table = UIElementsContainerNoTextProxy(table)
td = UIElementsProxy(td)
text = UIElementsLeafProxy(text)
th = UIElementsProxy(th)
tr = UIElementsProxy(tr)
window = UIElementsWindowProxy(window)

def svg(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg"])
    svg_properties = NodeSvgProperties(**properties)
    return NodeSvg(svg_properties)

def svg_path(props=None, **additional_props):
    if type(props) == str:
        props = { "d": props }
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg_path"])
    path_properties = NodeSvgPathProperties(**properties)
    return NodeSvgPath(path_properties)

def svg_rect(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg_rect"])
    properties = NodeSvgRectProperties(**properties)
    return NodeSvgRect(properties)

def svg_circle(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg_circle"])
    properties = NodeSvgCircleProperties(**properties)
    return NodeSvgCircle(properties)

def svg_polyline(props=None, **additional_props):
    if type(props) == str:
        props = { "points": props }
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg_polyline"])
    properties = NodeSvgPolylineProperties(**properties)
    return NodeSvgPolyline("svg_polyline", properties)

def svg_polygon(props=None, **additional_props):
    if type(props) == str:
        props = { "points": props }
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg_polygon"])
    properties = NodeSvgPolygonProperties(**properties)
    return NodeSvgPolyline("svg_polygon", properties)

def svg_line(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg_line"])
    box_properties = NodeSvgLineProperties(**properties)
    return NodeSvgLine(box_properties)


element_svg_collection_full = {
    "svg": svg,
    "path": svg_path,
    "rect": svg_rect,
    "circle": svg_circle,
    "polyline": svg_polyline,
    "line": svg_line,
    "polygon": svg_polygon,
}


element_collection: Dict[str, callable] = {
    'active_window': active_window,
    'button': button,
    'checkbox': checkbox,
    'component': Component,
    'cursor': cursor,
    'div': div,
    'effect': effect,
    'icon': icon,
    'input_text': input_text,
    'link': link,
    # 'modal': modal, # experimental
    'ref': ref,
    'screen': screen,
    'state': state,
    'style': style,
    'table': table,
    'td': td,
    'text': text,
    'th': th,
    'tr': tr,
    # 'switch': switch, # experimental
    'window': window,
    **element_svg_collection_full,
}

element_collection_full = {
    **element_collection
}

def ui_elements(*elements: Union[str, List[str]]) -> tuple[callable]:
    if len(elements) == 1 and isinstance(elements[0], (list, tuple)):
        elements = elements[0]

    if not elements:
        return element_collection_full

    if type(elements) == str:
        elements = [elements]

    if not all(element in element_collection_full for element in elements):
        raise ValueError(
            f"\nInvalid elements `{elements}` provided to ui_elements"
            f"\nValid elements are {list(element_collection.keys())}"
        )

    if len(elements) > 1:
        return tuple(
            element_collection_full[element] for element in elements
        )
    else:
        return element_collection_full[elements[0]]

def ui_elements_svg(elements: List[str]) -> tuple[callable]:
    if not all(element in element_svg_collection_full for element in elements):
        raise ValueError(
            f"\nInvalid elements {elements} provided to ui_elements_svg"
            f"\nValid svg elements are {list(element_svg_collection_full.keys())}"
        )

    if len(elements) > 1:
        return tuple(
            element_svg_collection_full[element] for element in elements
        )
    else:
        return element_svg_collection_full[elements[0]]