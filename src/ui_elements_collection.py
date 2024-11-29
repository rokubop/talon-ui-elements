from dataclasses import dataclass, fields
from typing import Optional, get_origin, get_args, Any
from talon.screen import Screen
# from .nodes.node_component import NodeComponent
from .nodes.node_container import NodeContainer
from .nodes.node_screen import NodeScreen
from .nodes.node_text import NodeText
from .nodes.node_input_text import NodeInputText
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

@dataclass
class BoxModelSpacing:
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

@dataclass
class Margin(BoxModelSpacing):
    pass

@dataclass
class Padding(BoxModelSpacing):
    pass

@dataclass
class Border(BoxModelSpacing):
    pass

VALID_PROPS = (
    set(UIOptionsDict.__annotations__.keys())
    .union(set(NodeTextOptionsDict.__annotations__.keys()))
    .union(set(NodeInputTextOptionsDict.__annotations__.keys()))
)

def parse_box_model(model_type: BoxModelSpacing, **kwargs) -> BoxModelSpacing:
    model = model_type()
    model_name = model_type.__name__.lower()
    model_name_x = f'{model_name}_x'
    model_name_y = f'{model_name}_y'

    if "border_width" in kwargs:
        model.top = model.right = model.bottom = model.left = kwargs["border_width"]
    elif model_name in kwargs:
        all_sides_value = kwargs[model_name]
        model.top = model.right = model.bottom = model.left = all_sides_value

    if model_name_x in kwargs:
        model.left = model.right = kwargs[model_name_x]
    if model_name_y in kwargs:
        model.top = model.bottom = kwargs[model_name_y]

    for side in ['top', 'right', 'bottom', 'left']:
        side_key = f'{model_name}_{side}'
        if side_key in kwargs:
            setattr(model, side, kwargs[side_key])

    return model

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

    # if updating_root_id:
    #     # try reusing the root instead
    #     options["id"] = updating_root_id

    options["width"] = ref_screen.width
    options["height"] = ref_screen.height

    root = NodeScreen(
        "screen",
        UIOptions(**options)
    )
    # roots_core[root.id] = root
    return root

# def component(func):
#     # TODO: args and kwargs
#     def create_node_component():
#         return NodeComponent(func)
#     return create_node_component

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

def use_effect(callback, state_dependencies: list[str] = []):
    tree = state_manager.get_processing_tree()
    if not tree:
        raise ValueError("""
            use_effect() must be called during render of a tree, such as during ui_elements_show(ui).
            For mounting, you can also optionally use ui_elements_show(ui, on_mount=callback)
        """)

    if not tree.is_mounted:
        state_manager.register_effect(tree, callback, state_dependencies)

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
