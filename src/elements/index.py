from talon.screen import Screen
from .div import UIContainer
from .text import UIText
from ..builder import UIBuilder
from ..options import UIOptions, UITextOptions, UIProps, UIOptionsDict, UITextOptionsDict, UIInputTextOptionsDict
from dataclasses import dataclass, fields
from ..utils import get_screen
from typing import TypedDict, Optional, get_origin, get_args, Union

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

class UIOptionsDict(TypedDict):
    id: str
    align: str
    background_color: str
    border_color: str
    border_radius: int
    border_width: int
    border: Border
    bottom: int
    color: str
    flex: int
    flex_direction: str
    justify_content: str
    highlight_color: str
    align_items: str
    height: int
    justify: str
    left: int
    margin: Margin
    opacity: float
    padding: Padding
    right: int
    screen: int
    top: int
    width: int

class UITextOptionsDict(UIOptionsDict):
    id: str
    font_size: int
    font_weight: str

class UIInputTextOptionsDict(UIOptionsDict):
    id: str
    font_size: int
    value: str
    on_change: callable

VALID_PROPS = (
    set(UIOptionsDict.__annotations__.keys())
    .union(set(UITextOptionsDict.__annotations__.keys()))
    .union(set(UIInputTextOptionsDict.__annotations__.keys()))
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

# class UIOptions:
#     id: str = None
#     align: str = "start"
#     background_color: str = None
#     border_color: str = "FF0000"
#     border_radius: int = 0
#     border_width: int = None
#     border: Border = Border(0, 0, 0, 0)
#     bottom: Optional[int] = None
#     top: Optional[int] = None
#     left: Optional[int] = None
#     right: Optional[int] = None
#     color: str = "FFFFFF"
#     flex: int = None
#     flex_direction: str = "column"
#     gap: int = None
#     height: int = 0
#     highlight_color: str = None
#     justify: str = "flex_start"
#     justify_content: str = "flex_start"
#     align_items: str = "flex_start"
#     type: str = None
#     margin: Margin = Margin(0, 0, 0, 0)
#     opacity: float = None
#     padding: Padding = Padding(0, 0, 0, 0)
#     key: str = None
#     width: int = 0

#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             if hasattr(self, key):
#                 setattr(self, key, value)

#         if self.opacity is not None:
#             # convert float to 2 digit hex e.g. 00 44 88 AA FF
#             opacity_hex = format(int(round(self.opacity * 255)), '02X')

#             if self.background_color and len(self.background_color) == 6:
#                     self.background_color = self.background_color + opacity_hex

#             if self.border_color and len(self.border_color) == 6:
#                     self.border_color = self.border_color + opacity_hex

#             if self.color and len(self.color) == 6:
#                     self.color = self.color + opacity_hex

#         self.padding = parse_box_model(Padding, **{k: v for k, v in kwargs.items() if 'padding' in k})
#         self.margin = parse_box_model(Margin, **{k: v for k, v in kwargs.items() if 'margin' in k})
#         self.border = parse_box_model(Border, **{k: v for k, v in kwargs.items() if 'border' in k})

# @dataclass
# class UITextOptions(UIOptions):
#     id: str = None
#     font_size: int = 16
#     font_weight: str = "normal"
#     on_click: any = None

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)

# @dataclass
# class UIInputTextOptions(UIOptions):
#     id: str = None
#     font_size: int = 16
#     value: str = ""
#     on_change: callable = None

#     def __init__(self, **kwargs):
#         kwargs['padding_left'] = max(
#             kwargs.get('padding_left', 0),
#             kwargs.get('padding', 0)
#         ) + max(8, kwargs.get('border_radius', 0))
#         kwargs['padding_right'] = max(
#             kwargs.get('padding_right', 0),
#             kwargs.get('padding', 0)
#         ) + max(8, kwargs.get('border_radius', 0))
#         super().__init__(**kwargs)

# @dataclass
# class UIProps:
#     id: str
#     align: str
#     background_color: str
#     border_color: str
#     border_radius: int
#     border_width: int
#     border_top: int
#     border_right: int
#     border_bottom: int
#     border_left: int
#     bottom: int
#     top: int
#     left: int
#     right: int
#     color: str
#     flex: int
#     flex_direction: str
#     font_size: int
#     font_weight: str
#     gap: int
#     height: int
#     highlight_color: str
#     justify: str
#     justify_content: str
#     align_items: str
#     margin: int
#     margin_top: int
#     margin_right: int
#     margin_bottom: int
#     margin_left: int
#     on_change: callable
#     on_click: callable
#     opacity: float
#     padding: int
#     padding_top: int
#     padding_right: int
#     padding_bottom: int
#     padding_left: int
#     screen: int
#     value: str
#     width: int

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

builders_core = None
updating_builder_id = None

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
    # global builders_core, updating_builder_id
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

    # if updating_builder_id:
    #     # try reusing the builder instead
    #     options["id"] = updating_builder_id

    options["width"] = ref_screen.width
    options["height"] = ref_screen.height

    builder = UIBuilder(
        "screen",
        UIOptions(**options)
    )
    # builders_core[builder.id] = builder
    return builder

def div(props=None, **additional_props):
    options = get_props(props, additional_props)
    box_options = UIOptions(**options)
    return UIContainer('div', box_options)

def text(text_str: str, props=None, **additional_props):
    options = get_props(props, additional_props)
    text_options = UITextOptions(**options)
    return UIText(text_str, text_options)

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

div = UIElementsProxy(div)
text = UIElementsNoChildrenProxy(text)
screen = UIElementsProxy(screen)
