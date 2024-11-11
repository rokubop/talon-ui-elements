from typing import Optional, TypedDict
from .core.box_model import Border, Margin, Padding, parse_box_model
from dataclasses import dataclass, fields
from typing import TypedDict, Optional, get_origin, get_args

class UIOptions:
    id: str = None
    align: str = "start"
    background_color: str = None
    border_color: str = "FF0000"
    border_radius: int = 0
    border_width: int = None
    border: Border = Border(0, 0, 0, 0)
    bottom: Optional[int] = None
    top: Optional[int] = None
    left: Optional[int] = None
    right: Optional[int] = None
    color: str = "FFFFFF"
    flex: int = None
    flex_direction: str = "column"
    key: str = None
    guid: str = None
    gap: int = None
    height: int = 0
    highlight_color: str = None
    justify: str = "flex_start"
    justify_content: str = "flex_start"
    align_items: str = "flex_start"
    type: str = None
    margin: Margin = Margin(0, 0, 0, 0)
    opacity: float = None
    padding: Padding = Padding(0, 0, 0, 0)
    width: int = 0
    screen: int = 0

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

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

class NodeTextOptionsDict(UIOptionsDict):
    id: str
    font_size: int
    font_weight: str

class UIInputTextOptionsDict(UIOptionsDict):
    id: str
    font_size: int
    value: str
    on_change: callable

@dataclass
class NodeTextOptions(UIOptions):
    id: str = None
    font_size: int = 16
    font_weight: str = "normal"
    on_click: any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

VALID_PROPS = (
    set(UIOptionsDict.__annotations__.keys())
    .union(set(NodeTextOptionsDict.__annotations__.keys()))
    .union(set(UIInputTextOptionsDict.__annotations__.keys()))
)

@dataclass
class UIProps:
    id: str
    align: str
    background_color: str
    border_color: str
    border_radius: int
    border_width: int
    border_top: int
    border_right: int
    border_bottom: int
    border_left: int
    bottom: int
    top: int
    left: int
    right: int
    color: str
    flex: int
    flex_direction: str
    font_size: int
    font_weight: str
    gap: int
    height: int
    highlight_color: str
    justify: str
    justify_content: str
    align_items: str
    margin: int
    margin_top: int
    margin_right: int
    margin_bottom: int
    margin_left: int
    on_change: callable
    on_click: callable
    opacity: float
    padding: int
    padding_top: int
    padding_right: int
    padding_bottom: int
    padding_left: int
    screen: int
    value: str
    width: int

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