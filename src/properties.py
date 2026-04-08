import hashlib
import inspect
import json
from dataclasses import dataclass
from talon import app
from talon.types import Rect
from typing import TypedDict, Union
from typing import TypedDict
from .border_radius import BorderRadius
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
    ELEMENT_ENUM_TYPE,
)
from .utils import hex_color, scale_value, get_scale, _expand_shorthand_hex, parse_background

COLOR_PROPERTIES = {
    "background_color", "border_color", "color", "stroke", "fill",
    "border_top_color", "border_right_color", "border_bottom_color", "border_left_color",
}

# Properties that should be scaled by the global UI scale setting
SCALABLE_PROPERTIES = {
    'font_size', 'gap', 'width', 'height',
    'min_width', 'max_width', 'min_height', 'max_height',
    'padding', 'margin', 'border_width', 'border_radius',
    'focus_outline_width', 'stroke_width',
    'padding_top', 'padding_right', 'padding_bottom', 'padding_left',
    'padding_x', 'padding_y',
    'margin_top', 'margin_right', 'margin_bottom', 'margin_left',
    'margin_x', 'margin_y',
    'border_top', 'border_right', 'border_bottom', 'border_left',
    'left', 'right', 'top', 'bottom',
    'size'  # For SVG elements
}

_CORNER_RADIUS_KEYS = {
    'border_top_left_radius': 'top_left',
    'border_top_right_radius': 'top_right',
    'border_bottom_right_radius': 'bottom_right',
    'border_bottom_left_radius': 'bottom_left',
}

_BORDER_WIDTH_ALIASES = {
    'border_top_width': 'border_top',
    'border_right_width': 'border_right',
    'border_bottom_width': 'border_bottom',
    'border_left_width': 'border_left',
}

class Properties(PropertiesDimensionalType, PropertiesType):
    """
    These are base properties and not all inclusive.
    Other property classes inherit from this class.
    """
    align_items: str = DEFAULT_ALIGN_ITEMS
    align_self: str = None
    autofocus: bool = False
    background: str = None
    background_color: str = None
    border_color: str = DEFAULT_BORDER_COLOR
    border_top_color: str = None
    border_right_color: str = None
    border_bottom_color: str = None
    border_left_color: str = None
    border_radius: Union[int, float, tuple, BorderRadius] = None
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
    flex_shrink: int = None
    flex_wrap: Union[bool, str] = False
    focus_outline_color: str = DEFAULT_FOCUS_OUTLINE_COLOR
    focus_outline_width: int = DEFAULT_FOCUS_OUTLINE_WIDTH
    font_size: Union[int, float] = DEFAULT_FONT_SIZE
    gap: Union[int, float] = None
    height: Union[int, str, float] = 0
    highlight_style: dict = None
    highlight_color: str = None
    hint_offset: tuple = None
    mount_style: dict = None
    id: str = None
    justify_content: str = DEFAULT_JUSTIFY_CONTENT
    key: str = None
    left: Union[int, str, float] = None
    margin: Margin = Margin(0, 0, 0, 0)
    max_height: Union[int, str] = None
    max_width: Union[int, str] = None
    min_height: Union[int, str] = None
    min_width: Union[int, str] = None
    on_change: callable = None
    on_click: callable = None
    on_drag_end: callable = None
    opacity: Union[int, float] = None
    overflow: Overflow = None
    padding: Padding = Padding(0, 0, 0, 0)
    position: str = 'static'
    resizable: Union[bool, str, list] = False
    right: Union[int, str, float] = None
    top: Union[int, str, float] = None
    transition: dict = None
    unmount_style: dict = None
    value: str = None
    width: Union[int, str, float] = 0
    z_index: int = 0

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        self.color = DEFAULT_COLOR
        self.border_color = DEFAULT_BORDER_COLOR
        self.border_radius = BorderRadius(0)
        self.element_type = kwargs.get('element_type', None)
        self._explicitly_set = set()
        self._highlighted_variant = None

        for key, value in kwargs.items():
            self.update_property(key, value)

        # Scale defaults that weren't explicitly set
        if 'font_size' not in kwargs:
            self.font_size = scale_value(DEFAULT_FONT_SIZE)

        if not self.highlight_color:
            self.highlight_color = _expand_shorthand_hex(self.color) + "33"

        self.validate_properties(kwargs)
        self.update_colors_with_opacity()
        self.init_box_model_properties(kwargs)

    def validate_justify_content(self):
        if self.justify_content:
            valid = ['flex_start', 'flex_end', 'space_between', 'center', 'space_evenly']
            if self.justify_content not in valid:
                print(f"ui_elements: unsupported justify_content '{self.justify_content}', falling back to 'flex_start'. Valid: {valid}")
                self.justify_content = 'flex_start'

    def validate_align_items(self):
        if self.align_items:
            valid = ['stretch', 'center', 'flex_start', 'flex_end']
            if self.align_items not in valid:
                print(f"ui_elements: unsupported align_items '{self.align_items}', falling back to 'flex_start'. Valid: {valid}")
                self.align_items = 'flex_start'

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
            if not isinstance(self.transition, dict):
                raise ValueError(
                    f"\nInvalid value for transition: '{self.transition}'\n"
                    f"transition property should be a dict: transition={{'opacity': 200}} "
                    f"or transition={{'all': 300}}"
                )

    def validate_highlight_style(self):
        if self.highlight_style:
            VALID_VALUES = [
                'background_color', 'border_color', 'color', 'fill', 'stroke',
                'border_top_color', 'border_right_color', 'border_bottom_color', 'border_left_color',
            ]

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

    def validate_mount_style(self):
        if self.mount_style:
            if not isinstance(self.mount_style, dict):
                raise ValueError(
                    f"\nInvalid value for mount_style: '{self.mount_style}'\n"
                    f"mount_style property should be a dictionary: mount_style={{'opacity': 0, 'top': 20}}"
                )

    def validate_unmount_style(self):
        if self.unmount_style:
            if not isinstance(self.unmount_style, dict):
                raise ValueError(
                    f"\nInvalid value for unmount_style: '{self.unmount_style}'\n"
                    f"unmount_style property should be a dictionary: unmount_style={{'opacity': 0, 'top': 20}}"
                )

    def validate_properties(self, kwargs):
        self.validate_justify_content()
        self.validate_align_items()
        self.validate_drop_shadow()
        self.validate_transition()
        self.validate_position_constraints(kwargs)
        self.validate_highlight_style()
        self.validate_mount_style()
        self.validate_unmount_style()

    def init_box_model_properties(self, kwargs):
        self.padding = parse_box_model(Padding, **{k: v for k, v in kwargs.items() if 'padding' in k})
        self.margin = parse_box_model(Margin, **{k: v for k, v in kwargs.items() if 'margin' in k})
        self.border = parse_box_model(Border, **{k: v for k, v in kwargs.items() if 'border' in k})
        self.overflow = Overflow(kwargs.get('overflow'), kwargs.get('overflow_x'), kwargs.get('overflow_y'), kwargs.get('scroll_bar'))

    def inherit_kwarg_properties(self, kwargs: dict):
        """Inherit properties from kwargs dictionary."""
        update_padding = False
        update_margin = False
        update_border = False

        for key, value in kwargs.items():
            if key in self._explicitly_set:
                continue
            if key in COLOR_PROPERTIES:
                value = hex_color(value, property_name=key)

            # Apply scaling to dimensional properties from styles
            if key in SCALABLE_PROPERTIES and value is not None:
                if isinstance(value, (int, float)):
                    value = scale_value(value)

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
            if key in COLOR_PROPERTIES:
                value = hex_color(value, property_name=key)
            if key in ["padding", "margin", "border"]:
                value = parse_box_model(type(getattr(self, key)), **value)
            setattr(self, key, value)
            self._explicitly_set.add(key)

    @staticmethod
    def _apply_opacity_to_color(color: str, opacity_hex: str) -> str:
        """Expand shorthand, strip existing alpha, append opacity."""
        color = _expand_shorthand_hex(color)
        if len(color) > 6:
            color = color[:6]
        return color + opacity_hex

    def update_colors_with_opacity(self):
        if self.opacity is not None:
            # convert float to 2 digit hex e.g. 00, 44, 88, AA, FF
            opacity_hex = format(int(round(self.opacity * 255)), '02X')

            if self.background_color:
                self.background_color = self._apply_opacity_to_color(self.background_color, opacity_hex)

            if self.border_color:
                self.border_color = self._apply_opacity_to_color(self.border_color, opacity_hex)

            for side in ("border_top_color", "border_right_color", "border_bottom_color", "border_left_color"):
                val = getattr(self, side, None)
                if val:
                    setattr(self, side, self._apply_opacity_to_color(val, opacity_hex))

            if self.color:
                self.color = self._apply_opacity_to_color(self.color, opacity_hex)

            if getattr(self, 'fill', None):
                self.fill = self._apply_opacity_to_color(self.fill, opacity_hex)

            if getattr(self, 'stroke', None):
                self.stroke = self._apply_opacity_to_color(self.stroke, opacity_hex)

    def update_property(self, key, value, explicitly_set=True):
        if key in _BORDER_WIDTH_ALIASES:
            key = _BORDER_WIDTH_ALIASES[key]
        if key in _CORNER_RADIUS_KEYS:
            if not isinstance(self.border_radius, BorderRadius):
                self.border_radius = BorderRadius(self.border_radius)
            scaled_val = scale_value(value) if isinstance(value, (int, float)) else value
            setattr(self.border_radius, _CORNER_RADIUS_KEYS[key], float(scaled_val))
            br = self.border_radius
            br._has_radius = bool(br.top_left or br.top_right or br.bottom_right or br.bottom_left)
            br._is_uniform = (br.top_left == br.top_right == br.bottom_right == br.bottom_left)
            self._explicitly_set.add(key)
            return
        if hasattr(self, key):
            if key == "background" and isinstance(value, str):
                gradient = parse_background(value)
                if gradient:
                    value = gradient
                else:
                    value = hex_color(value, property_name=key)
            elif key in COLOR_PROPERTIES:
                value = hex_color(value, property_name=key)

            if key == "border_radius" and value is not None:
                if not isinstance(value, BorderRadius):
                    value = BorderRadius(value)
                if explicitly_set:
                    scale = get_scale()
                    if scale != 1.0:
                        value = value.scale(scale)
                # Preserve individually set corners
                old = self.border_radius
                if isinstance(old, BorderRadius):
                    for corner_key, attr in _CORNER_RADIUS_KEYS.items():
                        if corner_key in self._explicitly_set:
                            setattr(value, attr, getattr(old, attr))
            # Apply scaling to dimensional properties only when explicitly set by user
            # Don't scale when inheriting from parent (already scaled values)
            elif explicitly_set and key in SCALABLE_PROPERTIES and value is not None:
                if isinstance(value, (int, float)):
                    value = scale_value(value)
                elif isinstance(value, str) and "%" not in str(value):
                    # Don't scale percentage values
                    try:
                        numeric_value = float(value)
                        value = scale_value(numeric_value)
                    except (ValueError, TypeError):
                        pass

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
                k: hex_color(v, property_name=k) if k in COLOR_PROPERTIES else v
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

    def has_border_radius(self):
        """Check if border-radius is present and non-zero"""
        return self.get_border_radius().has_radius()

    def get_border_radius(self):
        """Always returns a BorderRadius type"""
        if isinstance(self.border_radius, BorderRadius):
            return self.border_radius
        elif self.border_radius is not None:
            self.border_radius = BorderRadius(self.border_radius)
            return self.border_radius
        else:
            self.border_radius = BorderRadius(0)
            return self.border_radius

    def gc(self):
        pass

    def hash(self) -> str:
        """Return a string hash representing the current properties."""
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
    margin_bottom: Union[int, str]
    margin_left: Union[int, str]
    margin_right: Union[int, str]
    margin_top: Union[int, str]
    margin: Union[int, str]
    margin_x: Union[int, str]
    margin_y: Union[int, str]
    padding_bottom: int
    padding_left: int
    padding_right: int
    padding_top: int
    padding: int

class ValidationProperties(TypedDict, BoxModelValidationProperties):
    align_items: str
    align_self: str
    autofocus: bool
    background: str
    background_color: str
    border_color: str
    border_top_color: str
    border_right_color: str
    border_bottom_color: str
    border_left_color: str
    border_radius: Union[int, float, tuple, BorderRadius]
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
    flex_shrink: int
    flex_wrap: Union[bool, str]
    focus_outline_color: str
    focus_outline_width: int
    font_family: str
    font_size: Union[int, float]
    gap: Union[int, float]
    height: Union[int, str, float]
    highlight_style: dict
    highlight_color: str
    hint_offset: tuple
    id: str
    mount_style: dict
    justify_content: str
    left: Union[int, str, float]
    max_height: Union[int, str]
    max_width: Union[int, str]
    min_height: Union[int, str]
    min_width: Union[int, str]
    opacity: Union[int, float]
    overflow_x: str
    overflow_y: str
    overflow: str
    scroll_bar: str
    position: str
    resizable: Union[bool, str, list]
    right: Union[int, str, float]
    top: Union[int, str, float]
    transition: dict
    unmount_style: dict
    value: str
    border_top_left_radius: Union[int, float]
    border_top_right_radius: Union[int, float]
    border_bottom_right_radius: Union[int, float]
    border_bottom_left_radius: Union[int, float]
    cursor: str
    width: Union[int, str, float]
    z_index: int

class NodeDivValidationProperties(ValidationProperties):
    drop_shadow: tuple
    on_click: callable

class NodeFormValidationProperties(ValidationProperties):
    on_submit: callable

class NodeCursorValidationProperties(ValidationProperties):
    refresh_rate: int

class NodeTextValidationProperties(ValidationProperties):
    text: str
    font_size: Union[int, float]
    font_family: str
    font_style: str
    font_weight: str
    for_id: str
    selectable: bool
    selection_color: str
    stroke_color: str = None
    stroke_width: Union[int, float] = None
    text_align: str
    white_space: str

class NodeCodeValidationProperties(ValidationProperties):
    copyable: bool
    diff: bool
    font_size: Union[int, float]
    font_family: str
    font_style: str
    font_weight: str
    language: str
    theme: Union[str, dict]
    selectable: bool
    selection_color: str
    stroke_color: str = None
    stroke_width: Union[int, float] = None
    text_align: str
    white_space: str

class NodeButtonValidationProperties(NodeTextValidationProperties):
    on_click: callable
    type: str

class NodeLinkValidationProperties(NodeButtonValidationProperties):
    url: str
    close_on_click: bool = False
    minimize_on_click: bool = False

@dataclass
class NodeTextProperties(Properties):
    id: str = None
    font_family: str = ""
    font_size: Union[int, float] = DEFAULT_FONT_SIZE
    font_style: str = "normal"
    font_weight: str = "normal"
    for_id: str = None
    on_click: any = None
    selectable: bool = False
    selection_color: str = "4488FF88"
    stroke_width: Union[int, float] = None
    stroke_color: str = None
    text_align: str = "left"
    type: str = None
    white_space: str = "normal"

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        super().__init__(**kwargs)

    def gc(self):
        if self.on_click:
            self.on_click = None

@dataclass
class NodeCodeProperties(Properties):
    id: str = None
    font_family: str = "monospace"
    font_size: Union[int, float] = DEFAULT_FONT_SIZE
    font_style: str = "normal"
    font_weight: str = "normal"
    for_id: str = None
    language: str = "python"
    copyable: bool = True
    diff: bool = False
    on_click: any = None
    theme: Union[str, dict] = None
    selectable: bool = True
    selection_color: str = "4488FF88"
    stroke_width: Union[int, float] = None
    stroke_color: str = None
    text_align: str = "left"
    type: str = None
    white_space: str = "nowrap"

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        super().__init__(**kwargs)

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
    font_family: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

@dataclass
class NodeFormProperties(Properties):
    on_submit: callable = None
    font_family: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def gc(self):
        if self.on_submit:
            self.on_submit = None

class NodeSvgValidationProperties(ValidationProperties):
    color: str
    background_color: str
    fill: Union[str, bool]
    stroke: str
    stroke_width: Union[int, float]
    stroke_linejoin: str
    stroke_linecap: str
    view_box: str
    size: Union[int, float]

@dataclass
class NodeSvgProperties(Properties):
    fill: Union[str, bool] = None
    stroke: Union[str, bool] = None
    stroke_width: Union[int, float] = 2
    stroke_linejoin: str = "round"
    stroke_linecap: str = "round"
    view_box: str = "0 0 24 24"
    size: Union[int, float] = 24

    def __init__(self, **kwargs):
        if not kwargs.get('fill') and not kwargs.get('stroke'):
            self.fill = DEFAULT_COLOR
            self.stroke = DEFAULT_COLOR

        if kwargs.get('fill') and isinstance(kwargs.get('fill'), bool):
            kwargs['fill'] = DEFAULT_COLOR

        # Scale default size and stroke_width if not explicitly provided
        if 'size' not in kwargs:
            self.size = scale_value(24)
        if 'stroke_width' not in kwargs:
            self.stroke_width = scale_value(2)

        super().__init__(**kwargs)

class NodeSvgPathValidationProperties(NodeSvgValidationProperties):
    d: str
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: Union[int, float]
    stroke: str
    fill: Union[str, bool]

class NodeSvgRectValidationProperties(NodeSvgValidationProperties):
    x: Union[int, float]
    y: Union[int, float]
    width: Union[int, float]
    height: Union[int, float]
    rx: Union[int, float]
    ry: Union[int, float]
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: Union[int, float]
    stroke: str
    fill: Union[str, bool]

class NodeSvgCircleValidationProperties(NodeSvgValidationProperties):
    cx: Union[int, float]
    cy: Union[int, float]
    r: Union[int, float]
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: Union[int, float]
    stroke: str
    fill: Union[str, bool]

class NodeSvgPolylineValidationProperties(NodeSvgValidationProperties):
    points: str
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: Union[int, float]
    stroke: str
    fill: Union[str, bool]

class NodeSvgPolygonValidationProperties(NodeSvgPolylineValidationProperties):
    pass

class NodeSvgLineValidationProperties(NodeSvgValidationProperties):
    x1: Union[int, float]
    y1: Union[int, float]
    x2: Union[int, float]
    y2: Union[int, float]
    stroke_linecap: str
    stroke_linejoin: str
    stroke_width: Union[int, float]
    stroke: str
    fill: Union[str, bool]

class NodeIconValidationProperties(ValidationProperties):
    name: str
    size: Union[int, float]
    stroke_width: Union[int, float]
    stroke_linecap: str = None
    stroke_linejoin: str = None
    stroke_width: Union[int, float] = None
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
            "width",
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
    x: Union[int, float] = 0
    y: Union[int, float] = 0
    width: Union[int, float] = 0
    height: Union[int, float] = 0
    rx: Union[int, float] = 0
    ry: Union[int, float] = 0
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
    cx: Union[int, float] = 0
    cy: Union[int, float] = 0
    r: Union[int, float] = 0
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
    x1: Union[int, float] = 0
    y1: Union[int, float] = 0
    x2: Union[int, float] = 0
    y2: Union[int, float] = 0
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
    placeholder: str = ""
    placeholder_color: str = "FFFFFF55"
    selection_color: str = "4488FF88"
    cursor_color: str = None

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        if kwargs.get('value'):
            kwargs['value'] = str(kwargs['value'])
        if app.platform == "mac":
            # Talon TextArea for mac defaults to a text that looks like code,
            # so change it to something that looks more like normal prose
            self.font_family = "helvetica"
        has_padding = any(
            k in kwargs
            for k in ('padding', 'padding_left', 'padding_right')
        )
        if not has_padding:
            default_pad_x = max(8, kwargs.get('border_radius', 0))
            kwargs['padding_left'] = default_pad_x
            kwargs['padding_right'] = default_pad_x
        super().__init__(**kwargs)

    def gc(self):
        if self.on_change:
            self.on_change = None

@dataclass
class NodeDataTableProperties(Properties):
    id: str = None
    columns: list = None
    data: list = None
    on_select: callable = None
    on_change: callable = None
    multi_select: bool = False
    row_key: str = None
    searchable: bool = True
    search_placeholder: str = "Search..."
    sort_key: str = None
    sort_direction: str = "asc"
    sort_fn: callable = None
    body_height: Union[int, str, float] = None
    header_background_color: str = None
    header_color: str = None
    row_background_color: str = None
    stripe_background_color: str = None
    selected_background_color: str = None
    row_hint_offset: tuple = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def gc(self):
        if self.on_select:
            self.on_select = None
        if self.on_change:
            self.on_change = None


class NodeDataTableValidationProperties(ValidationProperties):
    id: str
    columns: list
    data: list
    on_select: callable
    on_change: callable
    multi_select: bool
    row_key: str
    searchable: bool
    search_placeholder: str
    sort_key: str
    sort_direction: str
    sort_fn: callable
    body_height: Union[int, str, float]
    header_background_color: str
    header_color: str
    row_background_color: str
    stripe_background_color: str
    selected_background_color: str
    row_hint_offset: tuple


class NodeSelectProperties(Properties):
    id: str = None
    font_family: str = ""
    font_size: int = DEFAULT_FONT_SIZE
    options: list = None
    value = ""
    on_change: callable = None
    placeholder: str = "Select..."
    placeholder_color: str = "FFFFFF55"

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        if app.platform == "mac":
            self.font_family = "helvetica"
        super().__init__(**kwargs)

    def gc(self):
        if self.on_change:
            self.on_change = None

class NodeSelectValidationProperties(ValidationProperties):
    id: str
    font_size: int
    font_family: str
    options: list
    value: Union[str, int, float]
    on_change: callable
    placeholder: str
    placeholder_color: str

class NodeInputTextValidationProperties(ValidationProperties):
    id: str
    font_size: int
    value: Union[str, int, float] = None
    on_change: callable
    placeholder: str
    placeholder_color: str
    selection_color: str
    cursor_color: str

@dataclass
class NodeTextareaProperties(Properties):
    id: str = None
    font_family: str = ""
    font_size: int = DEFAULT_FONT_SIZE
    stroke_width: int = None
    stroke_color: str = None
    value = ""
    on_change: callable = None
    placeholder: str = ""
    placeholder_color: str = "FFFFFF55"
    selection_color: str = "4488FF88"
    cursor_color: str = None
    rows: int = 3

    def __init__(self, **kwargs):
        self.font_size = DEFAULT_FONT_SIZE
        if kwargs.get('value'):
            kwargs['value'] = str(kwargs['value'])
        if app.platform == "mac":
            self.font_family = "helvetica"
        has_padding = any(
            k in kwargs
            for k in ('padding', 'padding_left', 'padding_right', 'padding_top', 'padding_bottom')
        )
        if not has_padding:
            default_pad_x = max(8, kwargs.get('border_radius', 0))
            kwargs['padding_left'] = default_pad_x
            kwargs['padding_right'] = default_pad_x
            kwargs['padding_top'] = 8
            kwargs['padding_bottom'] = 8
        super().__init__(**kwargs)

    def gc(self):
        if self.on_change:
            self.on_change = None

class NodeTextareaValidationProperties(ValidationProperties):
    id: str
    font_size: int
    value: Union[str, int, float] = None
    on_change: callable
    placeholder: str
    placeholder_color: str
    selection_color: str
    cursor_color: str
    rows: int

@dataclass
class NodeWindowProperties(Properties):
    drag_title_bar_only: bool = True
    drop_shadow: tuple[int, int, int, int, str] = None
    icon: object = None
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
    icon: object
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
    animated: bool
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
    ELEMENT_ENUM_TYPE["code"]: NodeCodeValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["cursor"]: NodeCursorValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["data_table"]: NodeDataTableValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["div"]: NodeDivValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["form"]: NodeFormValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["icon"]: NodeIconValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["link"]: NodeLinkValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["input_text"]: NodeInputTextValidationProperties.__annotations__,
    ELEMENT_ENUM_TYPE["select"]: NodeSelectValidationProperties.__annotations__,
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
    ELEMENT_ENUM_TYPE["textarea"]: NodeTextareaValidationProperties.__annotations__,
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

def _resolve_aliases(props):
    if any(k in _BORDER_WIDTH_ALIASES for k in props):
        return {_BORDER_WIDTH_ALIASES.get(k, k): v for k, v in props.items()}
    return props

_IGNORED_PROPS = {"key"}

def validate_props(props, element_type):
    props = {k: v for k, v in props.items() if k not in _IGNORED_PROPS}
    props = _resolve_aliases(props)
    invalid_props = props.keys() - VALID_ELEMENT_PROP_TYPES[element_type]
    if invalid_props:
        valid_props_message = ",\n".join(sorted(VALID_ELEMENT_PROP_TYPES[element_type]))
        raise ValueError(
            f"\nInvalid property for \"{element_type}\": {', '.join(sorted(invalid_props))}\n\n"
            f"Valid properties for \"{element_type}\" are:\n"
            f"{valid_props_message}"
        )

    _MARGIN_KEYS = {"margin", "margin_top", "margin_right", "margin_bottom", "margin_left", "margin_x", "margin_y"}

    type_errors = []
    for key, value in props.items():
        expected_type = VALID_ELEMENT_PROP_TYPES[element_type][key]
        if expected_type is callable:
            if not callable(value):
                type_errors.append(f"{key}: expected callable, got {type(value).__name__} {value}")
        elif not isinstance(value, expected_type) and value is not None:
            type_errors.append(f"{key}: expected {expected_type.__name__}, got {type(value).__name__} {value}")
        elif key in _MARGIN_KEYS and isinstance(value, str) and value != "auto":
            type_errors.append(f"{key}: string value must be \"auto\", got \"{value}\"")

    if type_errors:
        raise ValueError(
            f"\nInvalid property type:\n" +
            "\n".join(type_errors)
        )

    return props

def validate_combined_props(props, additional_props, element_type):
    combined_props = combine_props(props, additional_props)
    combined_props = validate_props(combined_props, element_type)
    return combined_props
