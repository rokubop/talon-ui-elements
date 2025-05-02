from typing import List, Dict, Any, Union
from .constants import ELEMENT_ENUM_TYPE
from .core.state_manager import state_manager
from .nodes.component import Component
from .nodes.node_container import NodeContainer
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
from .nodes.node_text import NodeText
from .nodes.node_button import NodeButton
from .nodes.node_window import NodeWindow
from .properties import (
    NodeInputTextProperties,
    NodeRootProperties,
    NodeDivProperties,
    NodeTextProperties,
    NodeSvgProperties,
    NodeSvgPathProperties,
    NodeSvgRectProperties,
    NodeSvgCircleProperties,
    NodeSvgPolylineProperties,
    NodeSvgPolygonProperties,
    NodeSvgLineProperties,
    NodeWindowProperties,
    validate_combined_props
)
from .icons import icon
from .interfaces import Effect
from .ref import Ref

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
        return set_state(key, value)

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
    _, set_value = state_manager.set_state_value(key, value)
    return set_value

def use_effect_without_tree(callback, arg2, arg3=None):
    dependencies: list[str] = []
    cleanup = None

    if arg3 is not None:
        cleanup = arg2
        dependencies = arg3
    else:
        dependencies = arg2

    effect = Effect(
        name=callback.__name__,
        callback=callback,
        cleanup=cleanup,
        dependencies=dependencies,
        tree=None
    )
    state_manager.register_effect(effect)

def use_effect(callback, arg2, arg3=None):
    """
    Register callbacks on state change or on mount/unmount.

    Usage #1: `effect(callback, dependencies)`

    Usage #2: `effect(callback, cleanup, dependencies)`

    Dependencies are `str` state keys, or empty `[]` for mount/unmount effects.
    """
    dependencies: list[str] = []
    cleanup = None

    if arg3 is not None:
        cleanup = arg2
        dependencies = arg3
    else:
        dependencies = arg2

    tree = state_manager.get_processing_tree()

    if not tree:
        raise ValueError("""
            effect(callback, [cleanup], dependencies) must be called during render of a tree, such as during ui_elements_show(ui).
            You can also optionally use register on_mount and on_unmount effects directly with ui_elements_show(ui, on_mount=callback, on_unmount=callback)
        """)

    if not tree.is_mounted:
        effect = Effect(
            name=callback.__name__,
            callback=callback,
            cleanup=cleanup,
            dependencies=dependencies,
            tree=tree
        )
        state_manager.register_effect(effect)

def div(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["div"])
    div_properties = NodeDivProperties(**properties)
    return NodeContainer(ELEMENT_ENUM_TYPE["div"], div_properties)

def text(text_str: str = "", props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["text"])
    text_properties = NodeTextProperties(**properties)
    return NodeText(ELEMENT_ENUM_TYPE["text"], text_str, text_properties)

def button(*args, text=None, **additional_props):
    if args and isinstance(args[0], str):
        text = args[0]
        args = args[1:]

    props = args[0] if args and isinstance(args[0], dict) else {}

    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["button"])

    if text:
        properties["type"] = "button"
        text_properties = NodeTextProperties(**{
            "padding": 8,
            **properties
        })
        return NodeText(ELEMENT_ENUM_TYPE["button"], text, text_properties)

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
    window_properties = NodeWindowProperties(**{
        "draggable": True,
        "background_color": "222222",
        "drop_shadow": (0, 20, 25, 25, "000000CC"),
        "border_radius": 4,
        "border_width": 1,
        **properties
    })
    return NodeWindow(window_properties)

class UIElementsContainerProxy:
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

active_window = UIElementsContainerProxy(active_window)
button = UIElementsLeafProxy(button)
div = UIElementsContainerProxy(div)
effect = use_effect
icon = UIElementsLeafProxy(icon)
input_text = UIElementsInputTextProxy(input_text)
ref = Ref
screen = UIElementsContainerProxy(screen)
state = State()
text = UIElementsLeafProxy(text)
window = UIElementsWindowProxy(window)

element_collection: Dict[str, callable] = {
    'active_window': active_window,
    'button': button,
    'component': Component,
    'div': div,
    'icon': icon,
    'input_text': input_text,
    'screen': screen,
    'text': text,
    'state': state,
    'ref': ref,
    'effect': effect,
    'window': window
}

element_collection_full = {
    **element_collection
}

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

def ui_elements(*elements: Union[str, List[str]]) -> tuple[callable]:
    if len(elements) == 1 and isinstance(elements[0], (list, tuple)):
        elements = elements[0]

    if not elements:
        return element_collection_full

    if type(elements) == str:
        elements = [elements]

    if any(element in element_svg_collection_full for element in elements):
        raise ValueError(
            f"\nInvalid elements `{elements}` provided to ui_elements"
            f"\nSVG elements must use `ui_elements_svg` instead of `ui_elements`"
        )

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