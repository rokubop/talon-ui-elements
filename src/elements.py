from dataclasses import fields
from typing import Optional, List, Dict, get_origin, get_args, Any
from talon.screen import Screen
from .interfaces import Effect
from .nodes.node_container import NodeContainer
from .nodes.node_screen import NodeScreen
from .nodes.node_text import NodeText
from .nodes.node_input_text import NodeInputText
from .entity_manager import entity_manager
from .state_manager import state_manager
from .options import (
    UIOptions,
    NodeTextOptions,
    UIProps,
    UIOptionsDict,
    NodeTextOptionsDict,
    NodeInputTextOptions,
    NodeInputTextOptionsDict,
)
from .utils import get_screen

VALID_PROPS = (
    set(UIOptionsDict.__annotations__.keys())
    .union(set(NodeTextOptionsDict.__annotations__.keys()))
    .union(set(NodeInputTextOptionsDict.__annotations__.keys()))
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

roots_core = None
updating_root_id = None

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
    # global roots_core, updating_root_id
    props = None
    if len(args) == 1 and isinstance(args[0], dict):
        props = args[0]
    elif len(args) == 1:
        props = { "screen": args[0] }
    elif len(args) > 1:
        props = args[1]
        props["screen"] = args[0]

    ref_screen: Screen = get_screen(props.get("screen") if props else None)

    options = get_props(props, additional_props)

    options["width"] = ref_screen.width
    options["height"] = ref_screen.height

    root = NodeScreen(
        "screen",
        UIOptions(**options)
    )
    return root

# def component(func):
#     # TODO: args and kwargs
#     def create_node_component():
#         return NodeComponent(func)
#     return create_node_component

class State:
    def get(self, key: str, initial_state: Any = None):
        return get_state(key, initial_state)

    def use(self, key: str, initial_state: Any = None):
        return use_state(key, initial_state)

    def set(self, key: str, value: Any):
        return set_state(key, value)

class Ref:
    def __init__(self, id: str):
        self.id = id
        self.element_type = None

    def get_node(self):
        return entity_manager.get_node(self.id)

    @property
    def text(self):
        return state_manager.get_text_mutation(self.id)

    @property
    def value(self):
        return state_manager.get_input_value(self.id)

    def set_text(self, new_value: Any):
        state_manager.set_text_mutation(self.id, new_value)

    def set(self, prop: str, new_value: Any):
        if prop == "text":
            return self.set_text(new_value)

        raise ValueError(f"ref set does not support '{prop}' for element type '{self.element_type}'")

    def get(self, prop: str):
        if not self.element_type:
            node = self.get_node()
            self.element_type = node.element_type

        if prop == "text":
            if self.element_type == "text":
                return self.text
        if prop == "value":
            if self.element_type == "input_text":
                return self.value

        if node := self.get_node():
            return node.options.get(prop)

        raise ValueError(f"ref get does not support '{prop}' for element type '{self.element_type}'")

    def highlight(self, color=None):
        state_manager.highlight(self.id, color)

    def unhighlight(self):
        state_manager.unhighlight(self.id)

    def highlight_briefly(self, color=None):
        state_manager.highlight_briefly(self.id, color)


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

def use_effect(callback, arg1, arg2=None):
    """
    Register callbacks on state change or on mount/unmount.

    Usage #1: `effect(callback, dependencies)`

    Usage #2: `effect(callback, cleanup, dependencies)`

    Dependencies are `str` state keys, or empty `[]` for mount/unmount effects.
    """
    dependencies: list[str] = []
    cleanup = None

    if arg2 is not None:
        cleanup = arg1
        dependencies = arg2
    else:
        dependencies = arg1

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
    options = get_props(props, additional_props)
    box_options = UIOptions(**options)
    return NodeContainer('div', box_options)

def text(text_str: str, props=None, **additional_props):
    options = get_props(props, additional_props)
    text_options = NodeTextOptions(**options)
    return NodeText("text", text_str, text_options)

def button(text_str: str, props=None, **additional_props):
    default_props = {
        "type": "button",
        "color": "FFFFFF",
        "padding": 8,
        "background_color": "444444",
        **(props or {})
    }

    options = get_props(default_props, additional_props)
    text_options = NodeTextOptions(**options)
    return NodeText("button", text_str, text_options)

def input_text(props=None, **additional_props):
    options = get_props(props, additional_props)
    input_options = NodeInputTextOptions(**options)
    if not input_options.id:
        raise ValueError("input_text must have an id prop so that it can be targeted with actions.user.ui_elements_get_value(id)")
    return NodeInputText(input_options)

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

class UIElementsNoChildrenProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"{self.func.__name__} does not support children. Use {self.func.__name__}().")

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

div = UIElementsContainerProxy(div)
text = UIElementsNoChildrenProxy(text)
screen = UIElementsContainerProxy(screen)
button = UIElementsNoChildrenProxy(button)
input_text = UIElementsNoChildrenProxy(input_text)
state = State()
effect = use_effect
ref = Ref

def ui_elements(elements: List[str]) -> tuple[callable]:
    element_mapping: Dict[str, callable] = {
        'button': button,
        'div': div,
        'input_text': input_text,
        'screen': screen,
        'text': text,
        'state': state,
        'ref': ref,
        'effect': effect,
    }
    if not all(element in element_mapping for element in elements):
        raise ValueError(
            f"\nInvalid elements {elements} provided to ui_elements"
            f"\nValid elements are {list(element_mapping.keys())}"
        )
    return tuple(element_mapping[element] for element in elements) if len(elements) > 1 else element_mapping[elements[0]]