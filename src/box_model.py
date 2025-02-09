from dataclasses import dataclass
from typing import Union
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from .interfaces import (
    BoxModelLayoutType,
    BoxModelSpacing,
    BoxModelV2Type,
    NodeType,
    OverflowType,
    PropertiesDimensionalType,
    Size2d,
)
from .constants import (
    DEFAULT_SCROLL_BAR_WIDTH,
    DEFAULT_SCROLL_BAR_TRACK_COLOR,
    DEFAULT_SCROLL_BAR_THUMB_COLOR
)

@dataclass
class Overflow(OverflowType):
    x: str = "visible"
    y: str = "visible"
    scrollable: bool = False
    scrollable_x: bool = False
    scrollable_y: bool = False

    def __init__(self, overflow: str = "visible", overflow_x: str = None, overflow_y: str = None):
        self.x = overflow_x or overflow
        self.y = overflow_y or overflow
        self.scrollable_x = self.x == "scroll" or self.x == "auto"
        self.scrollable_y = self.y == "scroll" or self.y == "auto"
        self.scrollable = self.scrollable_x or self.scrollable_y

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

def grow_rect_x(orig_rect: Rect, new_rect: Rect, max_width: int = None):
    new_x = orig_rect.x
    new_width = orig_rect.width
    if new_rect.x < orig_rect.x:
        new_width = orig_rect.width + orig_rect.x - new_rect.x
        new_x = new_rect.x
    if new_rect.x + new_rect.width > orig_rect.x + orig_rect.width:
        new_width = new_rect.x + new_rect.width - orig_rect.x
    orig_rect.x = new_x
    orig_rect.width = new_width

def grow_rect_y(orig_rect: Rect, new_rect: Rect, max_height: int = None):
    new_y = orig_rect.y
    new_height = orig_rect.height
    if new_rect.y < orig_rect.y:
        new_height = orig_rect.height + orig_rect.y - new_rect.y
        new_y = new_rect.y
    if new_rect.y + new_rect.height > orig_rect.y + orig_rect.height:
        new_height = new_rect.y + new_rect.height - orig_rect.y
    orig_rect.y = new_y
    orig_rect.height = new_height

@dataclass
class BoxModelLayout(BoxModelLayoutType):
    margin_spacing: BoxModelSpacing
    padding_spacing: BoxModelSpacing
    border_spacing: BoxModelSpacing
    margin_rect: Rect
    padding_rect: Rect
    border_rect: Rect
    content_rect: Rect
    content_children_rect: Rect
    scroll_box_rect: Union[Rect, None] = None
    # Margin > Border > ScrollBox > Padding > Content > Content children

    def __init__(
        self,
        x: int,
        y: int,
        margin_spacing: BoxModelSpacing,
        padding_spacing: BoxModelSpacing,
        border_spacing: BoxModelSpacing,
        width: int = None,
        height: int = None,
        min_width: int = None,
        min_height: int = None,
        max_width: int = None,
        max_height: int = None,
        fixed_width: bool = None,
        fixed_height: bool = None,
        overflow: Overflow = None,
        constraint_nodes: list[NodeType] = None
    ):
        self.constraints = self.reduce_constraints(constraint_nodes)
        self.fixed_width = fixed_width if fixed_width is not None else width is not None
        self.fixed_height = fixed_height if fixed_height is not None else height is not None
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width or 0
        self.max_height =  max_height or 0
        self.width = width or min_width or 0
        self.height = height or min_height or 0
        self.margin_spacing = margin_spacing
        self.padding_spacing = padding_spacing
        self.border_spacing = border_spacing
        self.content_width = None
        self.content_height = None
        self.scrollable = False
        if self.fixed_width and not self.max_width:
            self.max_width = self.width
        if self.fixed_height and not self.max_height:
            self.max_height = self.height
        if overflow:
            self.scrollable = overflow.scrollable

        if isinstance(width, str):
            if "%" in width:
                self.width = 0 # calculated later
            else:
                self.width = int(width)
        if isinstance(height, str) and "%" in height:
            if "%" in height:
                self.height = 0 # calculated later
            else:
                self.height = int(height)

        self.margin_rect = Rect(x, y, self.width, self.height)
        self.border_rect = Rect(x + margin_spacing.left, y + margin_spacing.top, self.width, self.height)
        self.padding_rect = Rect(x + margin_spacing.left + border_spacing.left, y + margin_spacing.top + border_spacing.top, self.width - border_spacing.left - border_spacing.right if self.width else 0, self.height - border_spacing.top - border_spacing.bottom if self.height else 0)
        content_x = x + margin_spacing.left + border_spacing.left + padding_spacing.left
        content_y = y + margin_spacing.top + margin_spacing.top + padding_spacing.top
        self.content_width = self.width - padding_spacing.left - padding_spacing.right - border_spacing.left - border_spacing.right if self.width else 0
        self.content_height = self.height - padding_spacing.top - padding_spacing.bottom - border_spacing.top - border_spacing.bottom if self.height else 0
        self.content_rect = Rect(content_x, content_y, self.content_width, self.content_height)
        self.max_content_width = 0
        self.max_content_height = 0
        self.max_border_width = 0
        self.max_border_height = 0
        self.max_margin_width = 0
        self.max_margin_height = 0
        if self.max_width:
            self.max_content_width = self.content_width + max_width - width if max_width else None
        if self.constraints["max_width"]:
            self.max_border_width = self.constraints["max_width"]
            self.max_margin_width = self.constraints["max_width"] + margin_spacing.left + margin_spacing.right
        if self.max_height:
            self.max_content_height = self.content_height + max_height - height if max_height else None
        if self.constraints["max_height"]:
            self.max_border_height = self.constraints["max_height"]
            self.max_margin_height = self.constraints["max_height"] + margin_spacing.top + margin_spacing.bottom

        self.content_children_rect = Rect(self.content_rect.x, self.content_rect.y, 0, 0)
        self.intrinsic_margin_rect = self.margin_rect.copy()
        self.intrinsic_border_rect = self.border_rect.copy()
        self.intrinsic_padding_rect = self.padding_rect.copy()
        self.intrinsic_content_rect = self.content_rect.copy()
        self.intrinsic_content_children_rect = self.content_children_rect.copy()
        self.layout_scroll_box_rect()

    def margin_rect_with_overflow(self):
        return Rect(
            self.margin_rect.x,
            self.margin_rect.y,
            self.content_rect.width + self.padding_spacing.left + self.padding_spacing.right + self.border_spacing.left + self.border_spacing.right + self.margin_spacing.left + self.margin_spacing.right,
            self.content_rect.height + self.padding_spacing.top + self.padding_spacing.bottom + self.border_spacing.top + self.border_spacing.bottom + self.margin_spacing.top + self.margin_spacing.bottom
        )

    def layout_scroll_box_rect(self):
        if self.scrollable:
            self.scroll_box_rect = Rect(
                self.border_rect.x + self.border_spacing.left,
                self.border_rect.y + self.border_spacing.top,
                self.border_rect.width - self.border_spacing.left - self.border_spacing.right,
                self.border_rect.height - self.border_spacing.top - self.border_spacing.bottom
            )

    def redistribute_from_rect(self, rect: Rect):
        self.margin_rect = rect
        self.border_rect = Rect(rect.x + self.margin_spacing.left, rect.y + self.margin_spacing.top, rect.width, rect.height)
        self.padding_rect = Rect(
            rect.x + self.margin_spacing.left + self.border_spacing.left,
            rect.y + self.margin_spacing.top + self.border_spacing.top,
            max(rect.width - self.border_spacing.left - self.border_spacing.right, self.padding_rect.width),
            max(rect.height - self.border_spacing.top - self.border_spacing.bottom, self.padding_rect.height)
        )
        self.content_rect = Rect(self.padding_rect.x + self.padding_spacing.left, self.padding_rect.y + self.padding_spacing.top, self.padding_rect.width - self.padding_spacing.left - self.padding_spacing.right, self.padding_rect.height - self.padding_spacing.top - self.padding_spacing.bottom)
        self.content_children_rect = Rect(self.content_rect.x, self.content_rect.y, 0, 0)
        self.clamp_dimensions()
        self.layout_scroll_box_rect()

    def clamp_dimensions(self):
        if self.constraints["max_width"]:
            self.border_rect.width = min(self.border_rect.width, self.constraints["max_width"])
            self.margin_rect.width = self.border_rect.width + self.margin_spacing.left + self.margin_spacing.right
        if self.constraints["max_height"]:
            self.border_rect.height = min(self.border_rect.height, self.constraints["max_height"])
            self.margin_rect.height = self.border_rect.height + self.margin_spacing.top + self.margin_spacing.bottom

    def accumulate_intrinsic_outer_dimensions_width(self, new_width: int):
        if new_width > self.intrinsic_margin_rect.width:
            diff = new_width - self.intrinsic_margin_rect.width
            self.intrinsic_margin_rect.width += diff
            self.intrinsic_border_rect.width += diff
            self.intrinsic_padding_rect.width += diff
            self.intrinsic_content_rect.width = self.intrinsic_padding_rect.width - self.padding_spacing.left - self.padding_spacing.right
            self.intrinsic_content_children_rect.width = self.intrinsic_content_rect.width

    def accumulate_intrinsic_outer_dimensions_height(self, new_height: int):
        if new_height > self.intrinsic_margin_rect.height:
            diff = new_height - self.intrinsic_margin_rect.height
            self.intrinsic_margin_rect.height += diff
            self.intrinsic_border_rect.height += diff
            self.intrinsic_padding_rect.height += diff
            self.intrinsic_content_rect.height = self.intrinsic_padding_rect.height - self.padding_spacing.top - self.padding_spacing.bottom
            self.intrinsic_content_children_rect.height = self.intrinsic_content_rect.height

    def accumulate_outer_dimensions_width(self, new_width: int):
        if new_width > self.margin_rect.width:
            new_width = max(new_width, self.max_width)
            diff = new_width - self.margin_rect.width
            self.width = new_width
            self.margin_rect.width += diff
            self.border_rect.width += diff
            new_padding_rect_width = self.padding_rect.width + diff
            self.padding_rect.width = max(self.padding_rect.width, new_padding_rect_width)
            self.content_rect.width = self.padding_rect.width - self.padding_spacing.left - self.padding_spacing.right
            self.content_children_rect.width = self.content_rect.width
            self.clamp_dimensions()
            self.layout_scroll_box_rect()

    def accumulate_outer_dimensions_height(self, new_height: int):
        if new_height > self.margin_rect.height:
            new_height = max(new_height, self.max_height)
            diff = new_height - self.margin_rect.height
            self.height = new_height
            self.margin_rect.height += diff
            self.border_rect.height += diff
            new_padding_rect_height = self.padding_rect.height + diff
            self.padding_rect.height = max(self.padding_rect.height, new_padding_rect_height)
            self.content_rect.height = self.padding_rect.height - self.padding_spacing.top - self.padding_spacing.bottom
            self.content_children_rect.height = self.content_rect.height
            self.clamp_dimensions()
            self.layout_scroll_box_rect()

    def accumulate_intrinsic_content_dimensions(self, rect: Rect, axis: str = None):
        if not axis or axis == "x":
            grow_rect_x(self.intrinsic_content_children_rect, rect)
            grow_rect_x(self.intrinsic_content_rect, rect)
            self.intrinsic_padding_rect.width = self.intrinsic_content_rect.width + self.padding_spacing.left + self.padding_spacing.right
            self.intrinsic_border_rect.width = self.intrinsic_padding_rect.width + self.border_spacing.left + self.border_spacing.right
            self.intrinsic_margin_rect.width = self.intrinsic_border_rect.width + self.margin_spacing.left + self.margin_spacing.right

        if not axis or axis == "y":
            grow_rect_y(self.intrinsic_content_children_rect, rect)
            grow_rect_y(self.intrinsic_content_rect, rect)
            self.intrinsic_padding_rect.height = self.intrinsic_content_rect.height + self.padding_spacing.top + self.padding_spacing.bottom
            self.intrinsic_border_rect.height = self.intrinsic_padding_rect.height + self.border_spacing.top + self.border_spacing.bottom
            self.intrinsic_margin_rect.height = self.intrinsic_border_rect.height + self.margin_spacing.top + self.margin_spacing.bottom

    def accumulate_content_dimensions(self, rect: Rect, axis: str = None):
        if not axis or axis == "x" and not self.fixed_width:
            grow_rect_x(self.content_children_rect, rect, self.max_content_width)
            grow_rect_x(self.content_rect, rect, self.max_content_width)
            self.padding_rect.width = self.content_rect.width + self.padding_spacing.left + self.padding_spacing.right
            self.border_rect.width = self.padding_rect.width + self.border_spacing.left + self.border_spacing.right
            self.margin_rect.width = self.border_rect.width + self.margin_spacing.left + self.margin_spacing.right
            self.width = self.margin_rect.width

        if not axis or axis == "y" and not self.fixed_height:
            grow_rect_y(self.content_children_rect, rect, self.max_content_height)
            grow_rect_y(self.content_rect, rect, self.max_content_height)
            self.padding_rect.height = self.content_rect.height + self.padding_spacing.top + self.padding_spacing.bottom
            self.border_rect.height = self.padding_rect.height + self.border_spacing.top + self.border_spacing.bottom
            self.margin_rect.height = self.border_rect.height + self.margin_spacing.top + self.margin_spacing.bottom
            self.height = self.margin_rect.height

        self.clamp_dimensions()
        self.layout_scroll_box_rect()

    def move_delta(self, x: int, y: int, flex_direction: str = "column", align_items: str = "stretch", justify_content: str = "flex_start"):
        self.border_rect.x += x
        self.border_rect.y += y
        self.margin_rect.x += x
        self.margin_rect.y += y
        self.padding_rect.x += x
        self.padding_rect.y += y
        self.content_rect.x = self.padding_rect.x + self.padding_spacing.left
        self.content_rect.y = self.padding_rect.y + self.padding_spacing.top
        self.content_children_rect.x = self.content_rect.x
        self.content_children_rect.y = self.content_rect.y

        if flex_direction == "row":
            if justify_content == "center":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width // 2 - self.content_children_rect.width // 2
            elif justify_content == "flex_end":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width - self.content_children_rect.width
            if align_items == "center":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height // 2 - self.content_children_rect.height // 2
            elif align_items == "flex_end":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height - self.content_children_rect.height
        else:
            if justify_content == "center":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height // 2 - self.content_children_rect.height // 2
            elif justify_content == "flex_end":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height - self.content_children_rect.height
            if align_items == "center":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width // 2 - self.content_children_rect.width // 2
            elif align_items == "flex_end":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width - self.content_children_rect.width

        self.layout_scroll_box_rect()

    def position_for_render(self, cursor: Point2d, flex_direction: str = "column", align_items: str = "stretch", justify_content: str = "flex_start"):
        self.margin_rect.x = cursor.x
        self.margin_rect.y = cursor.y
        self.border_rect.x = cursor.x + self.margin_spacing.left
        self.border_rect.y = cursor.y + self.margin_spacing.top
        self.padding_rect.x = cursor.x + self.margin_spacing.left + self.border_spacing.left
        self.padding_rect.y = cursor.y + self.margin_spacing.top + self.border_spacing.top
        self.content_rect.x = cursor.x + self.margin_spacing.left + self.border_spacing.left + self.padding_spacing.left
        self.content_rect.y = cursor.y + self.margin_spacing.top + self.border_spacing.top + self.padding_spacing.top
        self.content_children_rect.x = self.content_rect.x
        self.content_children_rect.y = self.content_rect.y
        if self.scrollable:
            self.scroll_box_rect.x = cursor.x + self.margin_spacing.left + self.border_spacing.left
            self.scroll_box_rect.y = cursor.y + self.margin_spacing.top + self.border_spacing.top

        if flex_direction == "row":
            if justify_content == "center":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width // 2 - self.content_children_rect.width // 2
            elif justify_content == "flex_end":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width - self.content_children_rect.width
            if align_items == "center":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height // 2 - self.content_children_rect.height // 2
            elif align_items == "flex_end":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height - self.content_children_rect.height
        else:
            if justify_content == "center":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height // 2 - self.content_children_rect.height // 2
            elif justify_content == "flex_end":
                self.content_children_rect.y = self.content_rect.y + self.content_rect.height - self.content_children_rect.height
            if align_items == "center":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width // 2 - self.content_children_rect.width // 2
            elif align_items == "flex_end":
                self.content_children_rect.x = self.content_rect.x + self.content_rect.width - self.content_children_rect.width

        self.layout_scroll_box_rect()

    def adjust_scroll_y(self, offset_y: int, c: SkiaCanvas):
        if self.scrollable:
            self.padding_rect.y -= offset_y
            self.content_rect.y -= offset_y
            self.content_children_rect.y -= offset_y

            if self.scroll_box_rect:
                view_height = self.scroll_box_rect.height
                total_scrollable_height = self.intrinsic_padding_rect.height

                if total_scrollable_height > view_height:
                    if self.intrinsic_padding_rect.height > 0:
                        scroll_y_percentage = offset_y / (total_scrollable_height - view_height)
                    else:
                        scroll_y_percentage = 0

                    thumb_height = max(20, view_height * (view_height / total_scrollable_height))

                    thumb_width = DEFAULT_SCROLL_BAR_WIDTH
                    thumb_y = self.scroll_box_rect.y + scroll_y_percentage * (self.scroll_box_rect.height - thumb_height)
                    thumb_y = max(self.scroll_box_rect.y, min(thumb_y, self.scroll_box_rect.y + self.scroll_box_rect.height - thumb_height))

                    bar_rect = Rect(
                        self.scroll_box_rect.x + self.scroll_box_rect.width - thumb_width,
                        self.scroll_box_rect.y,
                        thumb_width,
                        self.scroll_box_rect.height
                    )
                    c.paint.style = c.paint.Style.FILL
                    c.paint.color = DEFAULT_SCROLL_BAR_TRACK_COLOR
                    c.draw_rect(bar_rect)

                    thumb_rect = Rect(
                        self.scroll_box_rect.x + self.scroll_box_rect.width - thumb_width,
                        thumb_y,
                        thumb_width,
                        thumb_height
                    )
                    c.paint.color = DEFAULT_SCROLL_BAR_THUMB_COLOR
                    c.draw_rect(thumb_rect)

    def reduce_constraints(self, constraint_nodes: list[NodeType]) -> list[NodeType]:
        constraints = {
            "max_width": None,
            "max_height": None,
            "get_clip_rect": None
        }

        def get_clip_rect(node: NodeType):
            return lambda: node.box_model.scroll_box_rect

        if constraint_nodes:
            for node in constraint_nodes:
                if node.properties.max_width:
                    constraints["max_width"] = min(constraints["max_width"], node.properties.max_width) \
                        if constraints["max_width"] else node.properties.max_width
                if node.properties.max_height:
                    constraints["max_height"] = min(constraints["max_height"], node.properties.max_height) \
                        if constraints["max_height"] else node.properties.max_height
                if node.properties.is_scrollable():
                    constraints["get_clip_rect"] = get_clip_rect(node)

        return constraints

    def gc(self):
        self.constraints["get_clip_rect"] = None

class BoxModelV2(BoxModelV2Type):
    def __init__(
        self,
        properties: PropertiesDimensionalType,
        content_size: Size2d,
    ):
        if not content_size:
            raise ValueError("Size2d content_size is required for BoxModelV2")

        self.width = properties.width or properties.min_width or 0
        self.height = properties.height or properties.min_height or 0
        self.min_width = properties.min_width
        self.min_height = properties.min_height
        self.max_width = properties.max_width
        self.max_height =  properties.max_height
        self.fixed_width = bool(properties.width)
        self.fixed_height = bool(properties.height)
        self.overflow = properties.overflow
        self.overflow_size = Size2d(0, 0)

        self.margin_spacing = properties.margin
        self.padding_spacing = properties.padding
        self.border_spacing = properties.border

        self.margin_pos = None
        self.padding_pos = None
        self.border_pos = None
        self.content_pos = None
        self.content_children_pos = None

        self.margin_size = None
        self.padding_size = None
        self.border_size = None
        self.content_size = None
        self.content_children_size = None

        self.calculated_margin_size = None
        self.calculated_padding_size = None
        self.calculated_border_size = None
        self.calculated_content_size = None
        self.calculated_content_children_size = None

        self.intrinsic_margin_size = None
        self.intrinsic_border_size = None
        self.intrinsic_padding_size = None
        self.intrinsic_content_size = None
        self.intrinsic_content_children_size = content_size

        if isinstance(self.width, str):
            if "%" in self.width:
                self.width = 0 # calculated later
            else:
                self.width = int(self.width)

        if isinstance(self.height, str) and "%" in self.height:
            if "%" in self.height:
                self.height = 0 # calculated later
            else:
                self.height = int(self.height)

        self.init_intrinsic_sizes(content_size)

    @property
    def margin_rect(self):
        return Rect(self.margin_pos.x, self.margin_pos.y, self.margin_size.width, self.margin_size.height)

    @property
    def padding_rect(self):
        return Rect(self.padding_pos.x, self.padding_pos.y, self.padding_size.width, self.padding_size.height)

    @property
    def border_rect(self):
        return Rect(self.border_pos.x, self.border_pos.y, self.border_size.width, self.border_size.height)

    @property
    def content_rect(self):
        return Rect(self.content_pos.x, self.content_pos.y, self.content_size.width, self.content_size.height)

    @property
    def content_children_rect(self):
        return Rect(self.content_children_pos.x, self.content_children_pos.y, self.content_children_size.width, self.content_children_size.height)

    @staticmethod
    def content_size_to_border_size(content_size: Size2d, padding_spacing: BoxModelSpacing, border_spacing: BoxModelSpacing):
        return Size2d(
            content_size.width + padding_spacing.left + padding_spacing.right + border_spacing.left + border_spacing.right,
            content_size.height + padding_spacing.top + padding_spacing.bottom + border_spacing.top + border_spacing.bottom
        )

    def init_intrinsic_sizes(self, content_size: Size2d):
        self.intrinsic_content_children_size = content_size
        if content_size.width or content_size.height:
            if self.width or self.height:
                content_to_border_size = BoxModelV2.content_size_to_border_size(
                    content_size,
                    self.padding_spacing,
                    self.border_spacing
                )
                self.resolve_intrinsic_sizes_from_border_size(
                    Size2d(
                        max(self.width, content_to_border_size.width),
                        max(self.height, content_to_border_size.height)
                    )
                )
            else:
                self.resolve_intrinsic_sizes_from_content_size(content_size)
        else:
            self.resolve_intrinsic_sizes_from_border_size(
                Size2d(self.width, self.height)
            )
        self.init_calculated_sizes()

    def init_calculated_sizes(self):
        self.calculated_margin_size = self.intrinsic_margin_size.copy()
        self.calculated_border_size = self.intrinsic_border_size.copy()
        self.calculated_padding_size = self.intrinsic_padding_size.copy()
        self.calculated_content_size = self.intrinsic_content_size.copy()
        self.calculated_content_children_size = self.intrinsic_content_children_size.copy()

    def resolve_intrinsic_sizes_from_border_size(self, border_size: Size2d):
        self.intrinsic_border_size = border_size
        self.intrinsic_margin_size = Size2d(
            self.intrinsic_border_size.width + self.margin_spacing.left + self.margin_spacing.right,
            self.intrinsic_border_size.height + self.margin_spacing.top + self.margin_spacing.bottom
        )
        self.intrinsic_padding_size = Size2d(
            border_size.width - self.border_spacing.left - self.border_spacing.right,
            border_size.height - self.border_spacing.top - self.border_spacing.bottom
        )
        self.intrinsic_content_size = Size2d(
            self.intrinsic_padding_size.width - self.padding_spacing.left - self.padding_spacing.right,
            self.intrinsic_padding_size.height - self.padding_spacing.top - self.padding_spacing.bottom
        )

    def resolve_intrinsic_sizes_from_content_size(self, content_size: Size2d):
        self.intrinsic_content_size = content_size
        self.intrinsic_padding_size = Size2d(
            content_size.width + self.padding_spacing.left + self.padding_spacing.right,
            content_size.height + self.padding_spacing.top + self.padding_spacing.bottom
        )
        self.intrinsic_border_size = Size2d(
            self.intrinsic_padding_size.width + self.border_spacing.left + self.border_spacing.right,
            self.intrinsic_padding_size.height + self.border_spacing.top + self.border_spacing.bottom
        )
        self.intrinsic_margin_size = Size2d(
            self.intrinsic_border_size.width + self.margin_spacing.left + self.margin_spacing.right,
            self.intrinsic_border_size.height + self.margin_spacing.top + self.margin_spacing.bottom
        )

    def grow_calculated_height_to(self, height: int):
        if height > self.calculated_margin_size.height:
            diff = height - self.calculated_margin_size.height
            self.calculated_margin_size.height += diff
            self.calculated_border_size.height += diff
            self.calculated_padding_size.height += diff
            self.calculated_content_size.height += diff

    def grow_calculated_width_to(self, width: int):
        if width > self.calculated_margin_size.width:
            diff = width - self.calculated_margin_size.width
            self.calculated_margin_size.width += diff
            self.calculated_border_size.width += diff
            self.calculated_padding_size.width += diff
            self.calculated_content_size.width += diff

    def grow_calculated_height_by(self, height: int):
        self.grow_calculated_height_to(self.calculated_margin_size.height + height)

    def grow_calculated_width_by(self, width: int):
        self.grow_calculated_width_to(self.calculated_margin_size.width + width)

    def maximize_content_children_width(self):
        self.calculated_content_children_size.width = self.calculated_content_size.width

    def maximize_content_children_height(self):
        self.calculated_content_children_size.height = self.calculated_content_size.height

    def constrain_size(self, available_size: Size2d = None):
        margin_width = self.calculated_margin_size.width
        margin_height = self.calculated_margin_size.height
        max_width = self.max_width or self.width
        max_height = self.max_height or self.height
        available_size_width = available_size.width if available_size else None
        available_size_height = available_size.height if available_size else None

        if max_width:
            margin_width = min(margin_width, max_width + self.margin_spacing.left + self.margin_spacing.right)
        if available_size_width:
            margin_width = min(margin_width, available_size_width)

        if max_height:
            margin_height = min(margin_height, max_height + self.margin_spacing.top + self.margin_spacing.bottom)
        if available_size_height:
            margin_height = min(margin_height, available_size_height)

        if margin_width < self.calculated_margin_size.width:
            self.overflow_size.width = self.calculated_margin_size.width - margin_width
            border_width = margin_width - self.margin_spacing.left - self.margin_spacing.right
            padding_width = border_width - self.border_spacing.left - self.border_spacing.right
            content_width = padding_width - self.padding_spacing.left - self.padding_spacing.right
            content_constraint_width = content_width
            content_children_width = content_width if self.overflow.x != "visible" else self.calculated_content_children_size.width
        else:
            self.overflow_size.width = 0
            border_width = self.calculated_border_size.width
            padding_width = self.calculated_padding_size.width
            content_width = self.calculated_content_size.width
            content_constraint_width = content_width if (max_width or available_size_width) else None
            content_children_width = self.calculated_content_children_size.width

        if margin_height < self.calculated_margin_size.height:
            self.overflow_size.height = self.calculated_margin_size.height - margin_height
            border_height = margin_height - self.margin_spacing.top - self.margin_spacing.bottom
            padding_height = border_height - self.border_spacing.top - self.border_spacing.bottom
            content_height = padding_height - self.padding_spacing.top - self.padding_spacing.bottom
            content_constraint_height = content_height
            content_children_height = content_height if self.overflow.y != "visible" else self.calculated_content_children_size.height
        else:
            self.overflow_size.height = 0
            border_height = self.calculated_border_size.height
            padding_height = self.calculated_padding_size.height
            content_height = self.calculated_content_size.height
            content_constraint_height = content_height if (max_height or available_size_height) else None
            content_children_height = self.calculated_content_children_size.height

        self.margin_size = Size2d(margin_width, margin_height)
        self.border_size = Size2d(border_width, border_height)
        self.padding_size = Size2d(padding_width, padding_height)
        self.content_size = Size2d(content_width, content_height)
        self.content_children_size = Size2d(content_children_width, content_children_height)

        content_constraint_size = Size2d(content_constraint_width, content_constraint_height) \
            if content_constraint_width or content_constraint_height else None

        return content_constraint_size

    def position_for_render(self, cursor: Point2d, flex_direction: str = "column", align_items: str = "stretch", justify_content: str = "flex_start"):
        self.margin_pos = cursor.to_point2d()
        self.border_pos = Point2d(
            self.margin_pos.x + self.margin_spacing.left,
            self.margin_pos.y + self.margin_spacing.top
        )
        self.padding_pos = Point2d(
            self.border_pos.x + self.border_spacing.left,
            self.border_pos.y + self.border_spacing.top
        )
        self.content_pos = Point2d(
            self.padding_pos.x + self.padding_spacing.left,
            self.padding_pos.y + self.padding_spacing.top
        )
        self.content_children_pos = self.content_pos.copy()

        if flex_direction == "row":
            if justify_content == "center":
                self.content_children_pos.x = self.content_pos.x + self.content_size.width // 2 - self.content_children_size.width // 2
            elif justify_content == "flex_end":
                self.content_children_pos.x = self.content_pos.x + self.content_size.width - self.content_children_size.width
            if align_items == "center":
                self.content_children_pos.y = self.content_pos.y + self.content_size.height // 2 - self.content_children_size.height // 2
            elif align_items == "flex_end":
                self.content_children_pos.y = self.content_pos.y + self.content_size.height - self.content_children_size.height
        else:
            if justify_content == "center":
                self.content_children_pos.y = self.content_pos.y + self.content_size.height // 2 - self.content_children_size.height // 2
            elif justify_content == "flex_end":
                self.content_children_pos.y = self.content_pos.y + self.content_size.height - self.content_children_size.height
            if align_items == "center":
                self.content_children_pos.x = self.content_pos.x + self.content_size.width // 2 - self.content_children_size.width // 2
            elif align_items == "flex_end":
                self.content_children_pos.x = self.content_pos.x + self.content_size.width - self.content_children_size.width
