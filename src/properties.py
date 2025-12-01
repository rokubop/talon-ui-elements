import inspect
from dataclasses import dataclass
from talon import app
from talon.types import Rect
from typing import TypedDict, Union
from typing import TypedDict
from .box_model import (
    Overflow,
    parse_box_model
)
from .interfaces import (
    PropertiesType,
    PropertiesDimensionalType,
    Border,
    Margin,
    Padding
)
from .constants import (
    DEFAULT_ALIGN_ITEMS,
    DEFAULT_BORDER_COLOR,
    DEFAULT_COLOR,
    DEFAULT_FLEX_DIRECTION,
    DEFAULT_FONT_SIZE,
    DEFAULT_JUSTIFY_CONTENT,
    DEFAULT_FOCUS_OUTLINE_COLOR,
    DEFAULT_FOCUS_OUTLINE_WIDTH,
    ELEMENT_ENUM_TYPE
)
from .utils import hex_color

class Properties(PropertiesDimensionalType, PropertiesType):
    """
    These are base properties and not all inclusive.
    Other property classes inherit from this class.
    """
    align_items: str = DEFAULT_ALIGN_ITEMS
    align_self: str = None
    autofocus: bool = False
    background_color: str = None
    border_color: str = DEFAULT_BORDER_COLOR
    border_radius: int = 0
    border_width: int = None
    border: Border = Border(0, 0, 0, 0)
    bottom: Union[int, str, float] = None
    class_name: str = None
    color: str = DEFAULT_COLOR
    disabled: bool = False
    disabled_style: dict = None
    drag_handle: bool = False
    draggable: bool = False
    drop_shadow: tuple[int, int, int, int, str] = None
    flex_direction: str = DEFAULT_FLEX_DIRECTION
    flex: int = None
    flex_wrap: bool = False
    focus_outline_color: str = DEFAULT_FOCUS_OUTLINE_COLOR
    focus_outline_width: int = DEFAULT_FOCUS_OUTLINE_WIDTH
    font_size: int = DEFAULT_FONT_SIZE
    gap: int = None
    height: Union[int, str, float] = 0
    highlight_style: dict = None
    highlight_color: str = None
    id: str = None
    justify_content: str = DEFAULT_JUSTIFY_CONTENT
    key: str = None
    left: Union[int, str, float] = None
    margin: Margin = Margin(0, 0, 0, 0)
    max_height: int = None
    max_width: int = None
    min_height: int = None
    min_width: int = None
    on_change: callable = None
    on_click: callable = None
    on_drag_end: callable = None
    opacity: Union[int, float] = None
    overflow: Overflow = None
    padding: Padding = Padding(0, 0, 0, 0)
    position: str = 'static'
    right: Union[int, str, float] = None
    top: Union[int, str, float] = None
    transition: list[str] = None
    value: str = None
    width: Union[int, str, float] = 0
    z_index: int = 0

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        self.color = DEFAULT_COLOR
        self.border_color = DEFAULT_BORDER_COLOR
        self.element_type = kwargs.get('element_type', None)
        self._explicitly_set = set()
        self._highlighted_variant = None

        for key, value in kwargs.items():
            self.update_property(key, value)

        if not self.highlight_color:
            self.highlight_color = f"{self.color}33"

        self.validate_properties(kwargs)
        self.update_colors_with_opacity()
        self.init_box_model_properties(kwargs)

    def validate_justify_content(self):
        if self.justify_content:
            if self.justify_content not in ['flex_start', 'flex_end', 'space_between', 'center', 'space_evenly']:
                raise ValueError(
                    f"\nInvalid value for justify_content: '{self.justify_content}'\n"
                    f"Valid values are: 'flex_start', 'flex_end', 'space_between', 'space_evenly', 'center'"
                )

    def validate_align_items(self):
        if self.align_items:
            if self.align_items not in ['stretch', 'center', 'flex_start', 'flex_end']:
                raise ValueError(
                    f"\nInvalid value for align_items: '{self.align_items}'\n"
                    f"Valid values are: 'stretch', 'center', 'flex_start', 'flex_end'"
                )

    def validate_drop_shadow(self):
        if self.drop_shadow:
            if not isinstance(self.drop_shadow, tuple):
                raise ValueError(
                    f"\nInvalid value for drop_shadow: '{self.drop_shadow}'\n"
                    f"Valid values are: drop_shadow=(x_offset, y_offset, blur_x, blur_y, color)"
                )
            if len(self.drop_shadow) != 5:
                raise ValueError(
                    f"\nInvalid value for drop_shadow: '{self.drop_shadow}'\n"
                    f"Valid values are: drop_shadow=(x_offset, y_offset, blur_x, blur_y, color)"
                )
            if not isinstance(self.drop_shadow[0], int) or not isinstance(self.drop_shadow[1], int):
                raise ValueError(
                    f"\nInvalid value for x_offset or y_offset in drop_shadow: '{self.drop_shadow}'\n"
                    f"Use int for x_offset and y_offset: drop_shadow=(x_offset, y_offset, blur_x, blur_y, color)"
                )
            if not isinstance(self.drop_shadow[2], int) or not isinstance(self.drop_shadow[3], int):
                raise ValueError(
                    f"\nInvalid value for blur_x or blur_y in drop_shadow: '{self.drop_shadow}'\n"
                    f"Use int for blur_x and blur_y: drop_shadow=(x_offset, y_offset, blur_x, blur_y, color)"
                )
            if not isinstance(self.drop_shadow[4], str):
                raise ValueError(
                    f"\nInvalid value for color in drop_shadow.: '{self.drop_shadow}'\n"
                    f"Use a string for the 'color' value: drop_shadow=(x_offset, y_offset, blur_x, blur_y, color)"
                )

    def validate_position_constraints(self, kwargs):
        if kwargs.get('position'):
            if self.position not in ['absolute', 'relative', 'fixed', 'static']:
                raise ValueError(
                    f"\nInvalid value for position: '{self.position}'\n"
                    f"Valid values are: 'static' (default), 'relative', 'absolute', 'fixed'"
                )

            if self.position == 'relative':
                if kwargs.get('top') is not None and kwargs.get('bottom') is not None:
                    raise ValueError(
                        f"\nCannot set both 'top' and 'bottom' for relative position"
                    )
                if kwargs.get('left') is not None and kwargs.get('right') is not None:
                    raise ValueError(
                        f"\nCannot set both 'left' and 'right' for relative position"
                    )

            if self.position in ['absolute', 'fixed']:
                if all(kwargs.get(p) is not None for p in ['left', 'right', 'width']):
                    raise ValueError(
                        f"\nCannot set 3 constraints - 'left', 'right', AND 'width' for absolute/fixed position"
                        f"\nMust set only 2 constraints"
                    )
                if all(kwargs.get(p) is not None for p in ['top', 'bottom', 'height']):
                    raise ValueError(
                        f"\nCannot set 3 constraints - 'top', 'bottom', AND 'height' for absolute/fixed position"
                        f"\nMust set only 2 constraints"
                    )

        elif any(kwargs.get(dir) is not None for dir in ["left", "right", "top", "bottom"]):
            raise ValueError(
                f"\nCannot use 'left', 'right', 'top', or 'bottom' without setting position to 'absolute', 'relative', or 'fixed'"
            )

    def validate_transition(self):
        if self.transition:
            VALID_VALUES = ['opacity']

            if not isinstance(self.transition, list):
                raise ValueError(
                    f"\nInvalid value for transition: '{self.transition}'\n"
                    f"transition property should be a list: transition=['opacity']"
                )
            if any(prop not in VALID_VALUES for prop in self.transition):
                raise ValueError(
                    f"\nInvalid value for transition: '{self.transition}'\n"
                    f"Valid values are: {VALID_VALUES}\n"
                )

    def validate_highlight_style(self):
        if self.highlight_style:
            VALID_VALUES = ['background_color', 'border_color', 'color', 'fill', 'stroke']

            if not isinstance(self.highlight_style, dict):
                raise ValueError(
                    f"\nInvalid value for highlight_style: '{self.highlight_style}'\n"
                    f"highlight_style property should be a dictionary: highlight_style={{'background_color': '...', 'border_color': '...', ...}}"
                )

            if any(prop not in VALID_VALUES for prop in self.highlight_style):
                raise ValueError(
                    f"\nInvalid value for highlight_style: '{self.highlight_style}'\n"
                    f"Valid values are: {VALID_VALUES}\n"
                )

    def validate_properties(self, kwargs):
        self.validate_justify_content()
        self.validate_align_items()
        self.validate_drop_shadow()
        self.validate_transition()
        self.validate_position_constraints(kwargs)
        self.validate_highlight_style()

    def init_box_model_properties(self, kwargs):
        self.padding = parse_box_model(Padding, **{k: v for k, v in kwargs.items() if 'padding' in k})
        self.margin = parse_box_model(Margin, **{k: v for k, v in kwargs.items() if 'margin' in k})
        self.border = parse_box_model(Border, **{k: v for k, v in kwargs.items() if 'border' in k})
        self.overflow = Overflow(kwargs.get('overflow'), kwargs.get('overflow_x'), kwargs.get('overflow_y'))

    def inherit_kwarg_properties(self, kwargs: dict):
        """Inherit properties from kwargs dictionary."""
        update_padding = False
        update_margin = False
        update_border = False

        for key, value in kwargs.items():
            if key in self._explicitly_set:
                continue
            if key in ["background_color", "border_color", "color", "stroke", "fill"]:
                value = hex_color(value, property_name=key)

            update_padding = 'padding' in key or update_padding
            update_margin = 'margin' in key or update_margin
            update_border = 'border' in key or update_border
            setattr(self, key, value)
            self._explicitly_set.add(key)

        if update_padding:
            self.padding = parse_box_model(Padding, **{k: v for k, v in kwargs.items() if 'padding' in k})
        if update_margin:
            self.margin = parse_box_model(Margin, **{k: v for k, v in kwargs.items() if 'margin' in k})
        if update_border:
            self.border = parse_box_model(Border, **{k: v for k, v in kwargs.items() if 'border' in k})

        self.validate_properties(kwargs)

    def inherit_explicit_properties(self, properties: 'Properties'):
        """Inherit properties from another Properties object."""
        for key in properties._explicitly_set:
            value = getattr(properties, key)
            if key in ["background_color", "border_color", "color", "stroke", "fill"]:
                value = hex_color(value, property_name=key)
            if key in ["padding", "margin", "border"]:
                value = parse_box_model(type(getattr(self, key)), **value)
            setattr(self, key, value)
            self._explicitly_set.add(key)

    def update_colors_with_opacity(self):
        if self.opacity is not None:
            # convert float to 2 digit hex e.g. 00, 44, 88, AA, FF
            opacity_hex = format(int(round(self.opacity * 255)), '02X')

            if self.background_color:
                if self.background_color.startswith("#"):
                    self.background_color = self.background_color[1:]
                if len(self.background_color) > 6:
                    self.background_color = self.background_color[:6]
                self.background_color = self.background_color + opacity_hex

            if self.border_color:
                if self.border_color.startswith("#"):
                    self.border_color = self.border_color[1:]
                if len(self.border_color) > 6:
                    self.border_color = self.border_color[:6]
                self.border_color = self.border_color + opacity_hex

            if self.color:
                if self.color.startswith("#"):
                    self.color = self.color[1:]
                if len(self.color) > 6:
                    self.color = self.color[:6]
                self.color = self.color + opacity_hex

            if getattr(self, 'fill', None):
                if self.fill.startswith("#"):
                    self.fill = self.fill[1:]
                if len(self.fill) > 6:
                    self.fill = self.fill[:6]
                self.fill = self.fill + opacity_hex

            if getattr(self, 'stroke', None):
                if self.stroke.startswith("#"):
                    self.stroke = self.stroke[1:]
                if len(self.stroke) > 6:
                    self.stroke = self.stroke[:6]
                self.stroke = self.stroke + opacity_hex

    def update_property(self, key, value, explicitly_set=True):
        if hasattr(self, key):
            if key in ["background_color", "border_color", "color", "fill", "stroke"]:
                value = hex_color(value, property_name=key)

            if key == "on_click" and value is not None and callable(value):
                try:
                    sig = inspect.signature(value)
                    params = list(sig.parameters.values())
                    if len(params) > 0:
                        first_param = params[0]
                        # Check for common mistake: lambda with default parameter as first arg
                        if first_param.default != inspect.Parameter.empty and first_param.name != 'e' and first_param.name != 'event':
                            raise ValueError(
                                f"on_click function signature error: First parameter '{first_param.name}' "
                                f"has a default value, suggesting it might be a captured variable. "
                                f"The on_click callback receives a ClickEvent as its first parameter. "
                                f"Correct usage: on_click=lambda e: your_function(captured_var) "
                                f"or on_click=lambda e, var=captured_var: your_function(var)"
                            )
                except (ValueError, TypeError) as e:
                    if "on_click function signature error" in str(e):
                        raise

            setattr(self, key, value)
            if explicitly_set:
                self._explicitly_set.add(key)

    def update_overrides(self, overrides):
        for key, value in overrides.items():
            self.update_property(key, value)

    def get_variant(self, state: str) -> 'Properties':
        """Get a variant of the properties based on the state"""
        if state == "highlighted" and self.highlight_style:
            if hasattr(self, "_highlighted_variant"):
                return self._highlighted_variant

            variant = Properties.__new__(Properties)
            variant.__dict__ = self.__dict__.copy()
            variant.__dict__.update({
                k: hex_color(v, property_name=k) if k in {"color", "background_color", "border_color", "fill", "stroke"} else v
                for k, v in self.highlight_style.items()
            })
            self._highlighted_variant = variant
            return variant

        return self

    def is_user_set(self, key: str) -> bool:
        """Check if a property was explicitly set by the user."""
        return key in self._explicitly_set

    def is_scrollable(self):
        return self.overflow and self.overflow.scrollable

    def gc(self):
        pass

    def hash(self) -> str:
        """Return a string hash representing the current properties."""
        import json
        import hashlib

        props = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith('_') and not callable(v)
        }
        def safe_serialize(obj):
            try:
                json.dumps(obj)
                return obj
            except (TypeError, OverflowError):
                return repr(obj)
        props = {k: safe_serialize(v) for k, v in props.items()}
        props_json = json.dumps(props, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(props_json.encode('utf-8')).hexdigest()

class BoxModelValidationProperties(TypedDict):
    border_bottom: int
    border_left: int
    border_right: int
    border_top: int
    border: int
    margin_bottom: int
    margin_left: int
    margin_right: int
    margin_top: int
    margin: int
    padding_bottom: int
    padding_left: int
    padding_right: int
    padding_top: int
    padding: int

class ValidationProperties(TypedDict, BoxModelValidationProperties):
    align_items: str
    align_self: str
    autofocus: bool
    background_color: str
    border_color: str
    border_radius: int
    border_width: int
    bottom: Union[int, str, float]
    class_name: str
    color: str
    disabled: bool
    disabled_style: dict
    drag_handle: bool
    draggable: bool
    drop_shadow: tuple[int, int, int, int, str]
    element_type: str
    flex_direction: str
    flex: int
    flex_wrap: bool
    focus_outline_color: str
    focus_outline_width: int
    font_family: str
    font_size: int
    gap: int
    height: Union[int, str, float]
    highlight_style: dict
    highlight_color: str
    id: str
    justify_content: str
    left: Union[int, str, float]
    max_height: int
    max_width: int
    min_height: int
    min_width: int
    opacity: Union[int, float]
    overflow_x: str
    overflow_y: str
    overflow: str
    position: str
    right: Union[int, str, float]
    top: Union[int, str, float]
    transition: list[str]
    value: str
    width: Union[int, str, float]
    z_index: int

class NodeDivValidationProperties(ValidationProperties):
    drop_shadow: tuple

class NodeCursorValidationProperties(ValidationProperties):
    refresh_rate: int

class NodeTextValidationProperties(ValidationProperties):
    text: str
    font_size: int
    font_family: str
    font_weight: str
    for_id: str
    stroke_color: str = None
    stroke_width: int = None
    text_align: str

class NodeButtonValidationProperties(NodeTextValidationProperties):
    on_click: callable

class NodeLinkValidationProperties(NodeButtonValidationProperties):
    url: str
    close_on_click: bool = False
    minimize_on_click: bool = False

@dataclass
class NodeTextProperties(Properties):
    id: str = None
    font_family: str = ""
    font_size: int = DEFAULT_FONT_SIZE
    font_weight: str = "normal"
    for_id: str = None
    on_click: any = None
    stroke_width: int = None
    stroke_color: str = None
    text_align: str = "left"

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        super().__init__(**kwargs)

    def gc(self):
        if self.on_click:
            self.on_click = None

class NodeScreenValidationProperties(ValidationProperties):
    screen: int

class NodeActiveWindowValidationProperties(ValidationProperties):
    pass

@dataclass
class NodeRootProperties(Properties):
    screen: int = 0
    align_items: str = "flex_start"
    boundary_rect: Rect = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class NodeRootValidationProperties(ValidationProperties):
    screen: int

@dataclass
class NodeDivProperties(Properties):
    drop_shadow: tuple

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class NodeSvgValidationProperties(ValidationProperties):
    color: str
    background_color: str
    fill: Union[str, bool]
    stroke: str
    stroke_width: int
    stroke_linejoin: str
    stroke_linecap: str
    view_box: str
    size: int

@dataclass
class NodeSvgProperties(Properties):
    fill: Union[str, bool] = None
    stroke: Union[str, bool] = None
    stroke_width: int = 2
    stroke_linejoin: str = "round"
    stroke_linecap: str = "round"
    view_box: str = "0 0 24 24"
    size: int = 24

    def __init__(self, **kwargs):
        if not kwargs.get('fill') and not kwargs.get('stroke'):
            self.fill = DEFAULT_COLOR
            self.stroke = DEFAULT_COLOR

        if kwargs.get('fill') and isinstance(kwargs.get('fill'), bool):
            kwargs['fill'] = DEFAULT_COLOR
        super().__init__(**kwargs)

class NodeSvgPathValidationProperties(NodeSvgValidationProperties):
    d: str
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: int
    stroke: str
    fill: Union[str, bool]

class NodeSvgRectValidationProperties(NodeSvgValidationProperties):
    x: int
    y: int
    width: int
    height: int
    rx: int
    ry: int
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: int
    stroke: str
    fill: Union[str, bool]

class NodeSvgCircleValidationProperties(NodeSvgValidationProperties):
    cx: int
    cy: int
    r: int
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: int
    stroke: str
    fill: Union[str, bool]

class NodeSvgPolylineValidationProperties(NodeSvgValidationProperties):
    points: str
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: int
    stroke: str
    fill: Union[str, bool]

class NodeSvgPolygonValidationProperties(NodeSvgPolylineValidationProperties):
    pass

class NodeSvgLineValidationProperties(NodeSvgValidationProperties):
    x1: int
    y1: int
    x2: int
    y2: int
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: int
    stroke: str
    fill: Union[str, bool]

class NodeIconValidationProperties(ValidationProperties):
    name: str
    size: int
    stroke_width: int
    stroke_linecap: str = None
    stroke_linejoin: str = None
    stroke_width: int = None
    stroke: str = None
    fill: Union[str, bool] = None

@dataclass
class NodeTableProperties(NodeDivProperties):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class NodeTableRowProperties(NodeDivProperties):
    def __init__(self, **kwargs):
        allowed_properties = [
            "background_color",
            "border_color",
            "border_width",
            "border_top",
            "border_bottom",
            "height",
            "padding_top",
            "padding_bottom",
        ]

        for key in kwargs.keys():
            if key not in allowed_properties:
                raise ValueError(
                    f"\nInvalid property for 'tr': {key}\n"
                    f"Valid properties are: {', '.join(allowed_properties)}\n"
                    f"Or set properties directly on the child 'td' or 'th' elements"
                )

        super().__init__(**kwargs)

@dataclass
class NodeTableHeaderProperties(NodeDivProperties):
    colspan: int = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class NodeTableDataProperties(NodeDivProperties):
    colspan: int = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class NodeTableValidationProperties(NodeDivValidationProperties):
    pass

class NodeTableRowValidationProperties(NodeDivValidationProperties):
    pass

class NodeTableHeaderValidationProperties(NodeDivValidationProperties):
    pass

class NodeTableDataValidationProperties(NodeDivValidationProperties):
    colspan: int

@dataclass
class NodeSvgPathProperties(Properties):
    d: str = ""
    stroke_linecap: str = None
    stroke_linejoin: str = None
    stroke_width: int = None
    stroke: str = None
    fill: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class NodeSvgRectProperties(Properties):
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    rx: int = 0
    ry: int = 0
    stroke_linecap: str = None
    stroke_linejoin: str = None
    stroke_width: int = None
    stroke: str = None
    fill: str = None

    def __init__(self, **kwargs):
        if kwargs.get('fill') and isinstance(kwargs.get('fill'), bool):
            kwargs['fill'] = DEFAULT_COLOR
        if not kwargs.get('width') or not kwargs.get('height'):
            raise ValueError(
                f"\nInvalid property value for 'width' or 'height' for svg rect: {kwargs.get('width')}, {kwargs.get('height')}\n"
                f"Must provide a value for 'width' and 'height'"
            )

        super().__init__(**kwargs)

@dataclass
class NodeSvgCircleProperties(Properties):
    cx: int = 0
    cy: int = 0
    r: int = 0
    stroke_linecap: str = None
    stroke_linejoin: str = None
    stroke_width: int = None
    stroke: str = None
    fill: str = None

    def __init__(self, **kwargs):
        if kwargs.get('fill') and isinstance(kwargs.get('fill'), bool):
            kwargs['fill'] = DEFAULT_COLOR
        if not kwargs.get('r'):
            raise ValueError(
                f"\nInvalid property value for 'r' for svg circle: {kwargs.get('r')}\n"
                f"Must provide a value for 'r'"
            )

        super().__init__(**kwargs)

@dataclass
class NodeSvgPolylineProperties(Properties):
    points: str = ""
    stroke_linecap: str = None
    stroke_linejoin: str = None
    stroke_width: int = None
    stroke: str = None
    fill: str = None

    def __init__(self, **kwargs):
        if not kwargs.get('points'):
            raise ValueError(
                f"\nInvalid property value for 'points' for svg polyline: {kwargs.get('points')}\n"
                f"Must provide a value for 'points'"
            )

        super().__init__(**kwargs)

@dataclass
class NodeSvgPolygonProperties(NodeSvgPolylineProperties):
    def __init__(self, **kwargs):
        if kwargs.get('fill') and isinstance(kwargs.get('fill'), bool):
            kwargs['fill'] = DEFAULT_COLOR
        super().__init__(**kwargs)

@dataclass
class NodeSvgLineProperties(Properties):
    x1: int = 0
    y1: int = 0
    x2: int = 0
    y2: int = 0
    stroke_linecap: str = None
    stroke_linejoin: str = None
    stroke_width: int = None
    stroke: str = None
    fill: str = None

    def __init__(self, **kwargs):
        if not all(key in kwargs for key in ['x1', 'y1', 'x2', 'y2']):
            raise ValueError(
                f"\nInvalid property value for 'x1', 'y1', 'x2', 'y2' for svg line: {kwargs.get('x1')}, {kwargs.get('y1')}, {kwargs.get('x2')}, {kwargs.get('y2')}\n"
                f"Must provide a value for 'x1', 'y1', 'x2', 'y2'"
            )

        super().__init__(**kwargs)

@dataclass
class NodeInputTextProperties(Properties):
    id: str = None
    font_family: str = ""
    font_size: int = DEFAULT_FONT_SIZE
    stroke_width: int = None
    stroke_color: str = None
    value = ""
    on_change: callable = None

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        if kwargs.get('value'):
            kwargs['value'] = str(kwargs['value'])
        if app.platform == "mac":
            # Talon TextArea for mac defaults to a text that looks like code,
            # so change it to something that looks more like normal prose
            self.font_family = "helvetica"
        kwargs['padding_left'] = max(
            kwargs.get('padding_left', 0),
            kwargs.get('padding', 0)
        ) + max(8, kwargs.get('border_radius', 0))
        kwargs['padding_right'] = max(
            kwargs.get('padding_right', 0),
            kwargs.get('padding', 0)
        ) + max(8, kwargs.get('border_radius', 0))
        super().__init__(**kwargs)

    def gc(self):
        if self.on_change:
            self.on_change = None

class NodeInputTextValidationProperties(ValidationProperties):
    id: str
    font_size: int
    value: Union[str, int, float] = None
    on_change: callable

@dataclass
class NodeWindowProperties(Properties):
    drop_shadow: tuple[int, int, int, int, str] = None
    minimized: bool = False
    minimized_style: dict = None
    minimized_body: callable = None
    on_close: callable = None
    on_minimize: callable = None
    on_restore: callable = None
    show_close: bool = True
    show_minimize: bool = True
    show_title_bar: bool = True
    title_bar_style: dict = None
    title: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def gc(self):
        if self.on_close:
            self.on_close = None
        if self.on_minimize:
            self.on_minimize = None
        if self.on_restore:
            self.on_restore = None
        if self.minimized_body:
            self.minimized_body = None

class NodeWindowValidationProperties(ValidationProperties):
    drop_shadow: tuple[int, int, int, int, str]
    minimized: bool
    minimized_style: dict
    minimized_body: callable
    on_close: callable
    on_minimize: callable
    on_restore: callable
    show_close: bool
    show_minimize: bool
    show_title_bar: bool
    title_bar_style: dict
    title: str

@dataclass
class NodeCheckboxProperties(NodeSvgProperties):
    checked: bool = False
    on_change: callable = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def gc(self):
        if self.on_change:
            self.on_change = None

class NodeCheckboxValidationProperties(ValidationProperties, NodeSvgValidationProperties):
    checked: bool
    on_change: callable

@dataclass
class NodeSwitchProperties(NodeSvgProperties):
    checked: bool = False
    on_change: callable = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def gc(self):
        if self.on_change:
            self.on_change = None

class NodeSwitchValidationProperties(ValidationProperties, NodeSvgValidationProperties):
    checked: bool
    on_change: callable

@dataclass
class NodeModalProperties(Properties):
    title: str = None
    on_close: callable = None
    open: bool = False
    backdrop: bool = True
    backdrop_color: str = "00000000"
    backdrop_click_close: bool = True
    show_title_bar: bool = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def gc(self):
        if self.on_close:
            self.on_close = None

class NodeModalValidationProperties(ValidationProperties):
    title: str
    on_close: callable
    open: bool
    backdrop: bool
    backdrop_color: str
    backdrop_click_close: bool
    show_title_bar: bool

@dataclass
class NodeCursorProperties(Properties):
    refresh_rate: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

VALID_ELEMENT_PROP_TYPES = {
    ELEMENT_ENUM_TYPE["active_window"]: NodeActiveWindowValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["button"]: NodeButtonValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["checkbox"]: NodeCheckboxValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["cursor"]: NodeCursorValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["div"]: NodeDivValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["icon"]: NodeIconValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["link"]: NodeLinkValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["input_text"]: NodeInputTextValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["modal"]: NodeModalValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["screen"]: NodeScreenValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["svg_circle"]: NodeSvgCircleValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["svg_line"]: NodeSvgLineValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["svg_path"]: NodeSvgPathValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["svg_polygon"]: NodeSvgPolygonValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["svg_polyline"]: NodeSvgPolylineValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["svg_rect"]: NodeSvgRectValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["svg"]: NodeSvgValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["switch"]: NodeSwitchValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["table"]: NodeTableValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["td"]: NodeTableDataValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["text"]: NodeTextValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["th"]: NodeTableHeaderValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["tr"]: NodeTableRowValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["window"]: NodeWindowValidationProperties.__annotations__,
}

def combine_props(props, additional_props):
    if props is None:
        return additional_props
    if additional_props is None:
        return props
    return {**props, **additional_props}

def validate_props(props, element_type):
    invalid_props = props.keys() - VALID_ELEMENT_PROP_TYPES[element_type]
    if invalid_props:
        valid_props_message = ",\n".join(sorted(VALID_ELEMENT_PROP_TYPES[element_type]))
        raise ValueError(
            f"\nInvalid property for \"{element_type}\": {', '.join(sorted(invalid_props))}\n\n"
            f"Valid properties for \"{element_type}\" are:\n"
            f"{valid_props_message}"
        )

    type_errors = []
    for key, value in props.items():
        expected_type = VALID_ELEMENT_PROP_TYPES[element_type][key]
        if expected_type is callable:
            if not callable(value):
                type_errors.append(f"{key}: expected callable, got {type(value).__name__} {value}")
        elif not isinstance(value, expected_type) and value is not None:
            type_errors.append(f"{key}: expected {expected_type.__name__}, got {type(value).__name__} {value}")

    if type_errors:
        raise ValueError(
            f"\nInvalid property type:\n" +
            "\n".join(type_errors)
        )

    return props

def validate_combined_props(props, additional_props, element_type):
    combined_props = combine_props(props, additional_props)
    validate_props(combined_props, element_type)
    return combined_props
