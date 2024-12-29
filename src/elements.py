from typing import List, Dict, Any
from talon import ui
from talon.screen import Screen
from .constants import ELEMENT_ENUM_TYPE
from .nodes.node_container import NodeContainer
from .nodes.node_input_text import NodeInputText
from .nodes.node_root import NodeRoot
from .nodes.node_svg import NodeSvg, NodeSvgPath
from .nodes.node_text import NodeText
from .nodes.node_button import NodeButton
from .properties import (
    NodeInputTextProperties,
    NodeRootProperties,
    NodeTextProperties,
    NodeSvgProperties,
    NodeSvgPathProperties,
    Properties,
    validate_combined_props
)
from .interfaces import Effect
from .ref import Ref
from .state_manager import state_manager
from .utils import get_screen

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

    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["screen"])

    properties["boundary_rect"] = ref_screen.rect
    properties["width"] = int(ref_screen.width)
    properties["height"] = int(ref_screen.height)

    root = NodeRoot(
        ELEMENT_ENUM_TYPE["screen"],
        NodeRootProperties(**properties)
    )
    return root

def active_window(props=None, **additional_props):
    active_window = ui.active_window()

    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["active_window"])

    properties["boundary_rect"] = active_window.rect
    properties["width"] = int(active_window.rect.width)
    properties["height"] = int(active_window.rect.height)

    root = NodeRoot(
        ELEMENT_ENUM_TYPE["active_window"],
        NodeRootProperties(**properties)
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
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["div"])
    box_properties = Properties(**properties)
    return NodeContainer(ELEMENT_ENUM_TYPE["div"], box_properties)

def text(text_str: str, props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["text"])
    text_properties = NodeTextProperties(**properties)
    return NodeText(ELEMENT_ENUM_TYPE["text"], text_str, text_properties)

def button(*args, text=None, **additional_props):
    if args and isinstance(args[0], str):
        text = args[0]
        args = args[1:]

    props = args[0] if args and isinstance(args[0], dict) else {}

    default_props = {
        "padding": 8,
        **(props or {})
    }

    properties = validate_combined_props(default_props, additional_props, ELEMENT_ENUM_TYPE["button"])

    if text:
        properties["type"] = "button"
        text_properties = NodeTextProperties(**properties)
        return NodeText(ELEMENT_ENUM_TYPE["button"], text, text_properties)

    button_properties = NodeTextProperties(**properties)
    return NodeButton(button_properties)

ICON_SVG_SINGLE_PATH_STROKE = {
    "chevron_down": "M 6 9 L 12 15 L 18 9",
    "chevron_left": "M 15 6 L 9 12 L 15 18",
    "chevron_right": "M 9 6 L 15 12 L 9 18",
    "chevron_up": "M 6 15 L 12 9 L 18 15",
    "close": "M 6 6 L 18 18 M 18 6 L 6 18",
    "home": "M 12 4 L 20 10 V 20 H 4 V 10 L 12 4",
    "arrow_down": "M 12 4 V 14 M 12 14 L 8 10 M 12 14 L 16 10",
    "arrow_left": "M 20 12 H 10 M 10 12 L 14 8 M 10 12 L 14 16",
    "arrow_right": "M 4 12 H 14 M 14 12 L 10 8 M 14 12 L 10 16",
    "arrow_up": "M 12 20 V 10 M 12 10 L 8 14 M 12 10 L 16 14",
    "plus": "M 12 5 V 19 M 5 12 H 19",
    "edit": "M 16 3 L 21 8 L 8 21 L 3 21 L 3 16 L 16 3",
    "menu": "M 3 6 H 18 M 3 12 H 18 M 3 18 H 18",
    "settings": "M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z",
    "play": "M 5 3 L 19 12 L 5 21 Z",
}


VALID_ICON_NAMES = list(ICON_SVG_SINGLE_PATH_STROKE.keys())

def icon_svg_single_path_stroke(name: str, props=None, **additional_props):
    return svg(props, **additional_props)[
        svg_path(d=ICON_SVG_SINGLE_PATH_STROKE[name])
    ]

def icon(name: str, props=None, **additional_props):
    default_props = {
        "name": name,
        **(props or {})
    }

    if name not in VALID_ICON_NAMES:
        raise ValueError(f"Invalid icon name: {name}. Valid icon names are: \n{list(ICON_SVG_SINGLE_PATH_STROKE.keys())}")

    validate_combined_props(default_props, additional_props, ELEMENT_ENUM_TYPE["icon"])

    if name in ICON_SVG_SINGLE_PATH_STROKE:
        return icon_svg_single_path_stroke(name, props, **additional_props)

def input_text(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["input_text"])
    input_properties = NodeInputTextProperties(**properties)
    if not input_properties.id:
        raise ValueError("input_text must have an id prop so that it can be targeted with actions.user.ui_elements_get_value(id)")
    return NodeInputText(input_properties)

def css_deprecated(props=None, **additional_props):
    return validate_combined_props(props, additional_props, "div")

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

class UIElementsLeafProxy:
    def __init__(self, func):
        self.func = func

    def __getitem__(self, item):
        raise TypeError(f"{self.func.__name__} does not support children. Use {self.func.__name__}().")

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

div = UIElementsContainerProxy(div)
text = UIElementsLeafProxy(text)
screen = UIElementsContainerProxy(screen)
active_window = UIElementsContainerProxy(active_window)
button = UIElementsLeafProxy(button)
# icon = UIElementsLeafProxy(icon)
input_text = UIElementsInputTextProxy(input_text)
state = State()
effect = use_effect
ref = Ref

element_collection: Dict[str, callable] = {
    'button': button,
    'active_window': active_window,
    'div': div,
    'icon': icon,
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

def placeholder_svg_child(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg"])
    box_properties = Properties(**properties)
    return NodeContainer('div', box_properties)

def svg(props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg"])
    svg_properties = NodeSvgProperties(**properties)
    return NodeSvg(svg_properties)

def svg_path(d: str, props=None, **additional_props):
    properties = validate_combined_props(props, additional_props, ELEMENT_ENUM_TYPE["svg_path"])
    path_properties = NodeSvgPathProperties(**properties)
    path_properties.d = d
    return NodeSvgPath(path_properties)

element_svg_collection_full = {
    "svg": svg,
    "path": svg_path,
    "rect": placeholder_svg_child,
    "circle": placeholder_svg_child,
    "line": placeholder_svg_child,
    "polyline": placeholder_svg_child,
    "polygon": placeholder_svg_child,
    "ellipse": placeholder_svg_child,
}

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