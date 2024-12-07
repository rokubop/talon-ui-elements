from dataclasses import dataclass, fields
from talon import app
from typing import Optional, TypedDict, Union
from typing import TypedDict, Optional, get_origin, get_args
from .box_model import Border, Margin, Padding, parse_box_model
from .constants import (
    DEFAULT_COLOR,
    DEFAULT_BORDER_COLOR,
    DEFAULT_FONT_SIZE,
    DEFAULT_FLEX_DIRECTION,
    DEFAULT_ALIGN_ITEMS,
    DEFAULT_JUSTIFY_CONTENT
)

class Properties:
    align_items: str = DEFAULT_ALIGN_ITEMS
    align_self: str = None
    background_color: str = None
    border_color: str = DEFAULT_BORDER_COLOR
    border_radius: int = 0
    border_width: int = None
    border: Border = Border(0, 0, 0, 0)
    color: str = DEFAULT_COLOR
    flex_direction: str = DEFAULT_FLEX_DIRECTION
    flex: int = None
    font_size: int = DEFAULT_FONT_SIZE
    gap: int = None
    height: Union[int, str] = 0
    highlight_color: str = None
    id: str = None
    justify_content: str = DEFAULT_JUSTIFY_CONTENT
    key: str = None
    margin: Margin = Margin(0, 0, 0, 0)
    max_height: int = None
    max_width: int = None
    min_height: int = None
    min_width: int = None
    on_change: callable = None
    on_click: callable = None
    opacity: float = None
    padding: Padding = Padding(0, 0, 0, 0)
    value: str = None
    width: Union[int, str] = 0

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        self.color = DEFAULT_COLOR
        self.border_color = DEFAULT_BORDER_COLOR

        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        if not self.highlight_color:
            self.highlight_color = f"{self.color}33"

        if self.justify_content:
            if self.justify_content not in ['flex_start', 'flex_end', 'space_between', 'center']:
                raise ValueError(
                    f"\nInvalid value for justify_content: '{self.justify_content}'\n"
                    f"Valid values are: 'flex_start', 'flex_end', 'space_between', 'center'"
                )
        if self.align_items:
            if self.align_items not in ['stretch', 'center', 'flex_start', 'flex_end']:
                raise ValueError(
                    f"\nInvalid value for align_items: '{self.align_items}'\n"
                    f"Valid values are: 'stretch', 'center', 'flex_start', 'flex_end'"
                )

        if self.opacity is not None:
            # convert float to 2 digit hex e.g. 00 44 88 AA FF
            opacity_hex = format(int(round(self.opacity * 255)), '02X')

            if self.background_color and len(self.background_color) == 6:
                    self.background_color = self.background_color + opacity_hex

            if self.border_color and len(self.border_color) == 6:
                    self.border_color = self.border_color + opacity_hex

            if self.color and len(self.color) == 6:
                    self.color = self.color + opacity_hex

        self.padding = parse_box_model(Padding, **{k: v for k, v in kwargs.items() if 'padding' in k})
        self.margin = parse_box_model(Margin, **{k: v for k, v in kwargs.items() if 'margin' in k})
        self.border = parse_box_model(Border, **{k: v for k, v in kwargs.items() if 'border' in k})

    def update_overrides(self, overrides):
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)

class PropertiesDict(TypedDict):
    align_items: str
    align_self: str
    background_color: str
    border_color: str
    border_radius: int
    border_width: int
    border: Border
    color: str
    flex_direction: str
    flex: int
    height: Union[int, str]
    highlight_color: str
    id: str
    justify_content: str
    margin: Margin
    max_height: int
    max_width: int
    min_height: int
    min_width: int
    on_change: callable
    on_click: callable
    opacity: float
    padding: Padding
    value: str
    width: Union[int, str]

class NodeTextPropertiesDict(PropertiesDict):
    id: str
    font_size: int
    font_weight: str

@dataclass
class NodeTextProperties(Properties):
    id: str = None
    font_size: int = DEFAULT_FONT_SIZE
    font_weight: str = "normal"
    on_click: any = None
    font_family: str = None

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        super().__init__(**kwargs)

class NodeScreenPropertiesDict(PropertiesDict):
    screen: int

@dataclass
class NodeScreenProperties(Properties):
    screen: int = 0
    align_items: str = "flex_start"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class NodeInputTextProperties(Properties):
    id: str = None
    font_family: str = None
    font_size: int = DEFAULT_FONT_SIZE
    value = ""
    on_change: callable = None

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        if app.platform == "mac":
            # Talon TextArea for mac defaults to a text that looks like code,
            # so change it to something that looks more like normal prose
            self.font_family = "Helvetica"
        kwargs['padding_left'] = max(
            kwargs.get('padding_left', 0),
            kwargs.get('padding', 0)
        ) + max(8, kwargs.get('border_radius', 0))
        kwargs['padding_right'] = max(
            kwargs.get('padding_right', 0),
            kwargs.get('padding', 0)
        ) + max(8, kwargs.get('border_radius', 0))
        super().__init__(**kwargs)

class NodeInputTextPropertiesDict(PropertiesDict):
    id: str
    font_size: int
    value: str
    on_change: callable

VALID_PROPS = (
    set(PropertiesDict.__annotations__.keys())
    .union(set(NodeTextPropertiesDict.__annotations__.keys()))
    .union(set(NodeInputTextPropertiesDict.__annotations__.keys()))
    .union(set(NodeScreenPropertiesDict.__annotations__.keys()))
)

@dataclass
class UIProps:
    align_items: str
    align_self: str
    background_color: str
    border_bottom: int
    border_color: str
    border_left: int
    border_radius: int
    border_right: int
    border_top: int
    border_width: int
    color: str
    flex_direction: str
    flex: int
    font_family: str
    font_size: int
    font_weight: str
    gap: int
    height: Union[int, str]
    highlight_color: str
    id: str
    justify_content: str
    margin_bottom: int
    margin_left: int
    margin_right: int
    margin_top: int
    margin: int
    max_height: int
    max_width: int
    min_height: int
    min_width: int
    on_change: callable
    on_click: callable
    opacity: float
    padding_bottom: int
    padding_left: int
    padding_right: int
    padding_top: int
    padding: int
    screen: int
    value: str
    width: Union[int, str]

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