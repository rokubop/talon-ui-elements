from dataclasses import fields
from typing import Optional, List, Dict, get_origin, get_args, Any
from talon.screen import Screen
from .interfaces import Effect
from .nodes.node_container import NodeContainer
from .nodes.node_input_text import NodeInputText
from .nodes.node_screen import NodeScreen
from .nodes.node_text import NodeText
from .properties import (
    NodeInputTextProperties,
    NodeInputTextPropertiesDict,
    NodeScreenProperties,
    NodeScreenPropertiesDict,
    NodeTextProperties,
    NodeTextPropertiesDict,
    Properties,
    PropertiesDict,
    UIProps,
)
from .ref import Ref
from .state_manager import state_manager
from .utils import get_screen

VALID_PROPS = (
    set(PropertiesDict.__annotations__.keys())
    .union(set(NodeTextPropertiesDict.__annotations__.keys()))
    .union(set(NodeInputTextPropertiesDict.__annotations__.keys()))
    .union(set(NodeScreenPropertiesDict.__annotations__.keys()))
)

VALID_PROPS = {f.name for f in fields(UIProps)}
EXPECTED_TYPES = {f.name: f.type for f in fields(UIProps)}
EXPECTED_TYPES["type"] = str

def resolve_type(type_hint):
    if get_origin(type_hint) is Optional:
        return get_args(type_hint)[0]
    return type_hint

def get_props(props, additional_props):
    all_props = None
    if props is None:
        all_props = additional_props
    elif not additional_props:
        all_props = props
    else:
        all_props = {**props, **additional_props}

    invalid_props = set(all_props.keys()) - VALID_PROPS - {'type'}
    if invalid_props:
        valid_props_message = ",\n".join(sorted(VALID_PROPS))
        raise ValueError(
            f"\nInvalid CSS prop: {', '.join(sorted(invalid_props))}\n\n"
            f"Valid CSS props are:\n"
            f"{valid_props_message}"
        )

    type_errors = []
    for key, value in all_props.items():
        expected_type = EXPECTED_TYPES[key]
        if expected_type is callable:
            if not callable(value):
                type_errors.append(f"{key}: expected callable, got {type(value).__name__} {value}")
        elif not isinstance(value, expected_type):
            type_errors.append(f"{key}: expected {expected_type.__name__}, got {type(value).__name__} {value}")

    if type_errors:
        raise ValueError(
            f"\nInvalid CSS prop type:\n" +
            "\n".join(type_errors)
        )

    return all_props

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

    ref_screen: Screen = get_screen(props.get("screen") if props else None)

    properties = get_props(props, additional_props)

    properties["width"] = int(ref_screen.width)
    properties["height"] = int(ref_screen.height)

    root = NodeScreen(
        "screen",
        NodeScreenProperties(**properties)
    )
    return root

class State:
    def get(self, key: str, initial_state: Any = None):
        return get_state(key, initial_state)

    def use(self, key: str, initial_state: Any = None):
        return use_state(key, initial_state)

    def set(self, key: str, value: Any):
        return set_state(key, value)

def use_state(key: str, initial_state: Any = None):
    tree = state_manager.get_processing_tree()
    if not tree:
        raise ValueError("""
            use_state() must be called during render of a tree, such as during ui_elements_show(ui).
            If you want to use state outside of a render, use actions.user.ui_elements_get_state(),
            actions.user.ui_elements_set_state(), actions.user.ui_elements_set_initial_state()
        """)

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
    properties = get_props(props, additional_props)
    box_properties = Properties(**properties)
    return NodeContainer('div', box_properties)

def text(text_str: str, props=None, **additional_props):
    properties = get_props(props, additional_props)
    text_properties = NodeTextProperties(**properties)
    return NodeText("text", text_str, text_properties)

def button(text_str: str, props=None, **additional_props):
    default_props = {
        "type": "button",
        "padding": 8,
        **(props or {})
    }

    properties = get_props(default_props, additional_props)
    text_properties = NodeTextProperties(**properties)
    return NodeText("button", text_str, text_properties)

def input_text(props=None, **additional_props):
    properties = get_props(props, additional_props)
    input_properties = NodeInputTextProperties(**properties)
    if not input_properties.id:
        raise ValueError("input_text must have an id prop so that it can be targeted with actions.user.ui_elements_get_value(id)")
    return NodeInputText(input_properties)

def css_deprecated(props=None, **additional_props):
    return get_props(props, additional_props)

deprecated_elements = {
    # Just use a dictionary instead
    # Wrapping with a class doesn't help with intellisense
    "css": css_deprecated,
}

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

class UIElementsTextProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"{self.func.__name__} does not support children. Use {self.func.__name__}().")

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

div = UIElementsContainerProxy(div)
text = UIElementsTextProxy(text)
screen = UIElementsContainerProxy(screen)
button = UIElementsTextProxy(button)
input_text = UIElementsInputTextProxy(input_text)
state = State()
effect = use_effect
ref = Ref

element_collection: Dict[str, callable] = {
    'button': button,
    'div': div,
    'input_text': input_text,
    'screen': screen,
    'text': text,
    'state': state,
    'ref': ref,
    'effect': effect,
}

element_collection_full = {
    **element_collection,
    **deprecated_elements
}

def ui_elements(elements: List[str]) -> tuple[callable]:
    if not all(element in element_collection_full for element in elements):
        raise ValueError(
            f"\nInvalid elements {elements} provided to ui_elements"
            f"\nValid elements are {list(element_collection.keys())}"
        )

    if len(elements) > 1:
        return tuple(
            element_collection_full[element] for element in elements
        )
    else:
        return element_collection_full[elements[0]]