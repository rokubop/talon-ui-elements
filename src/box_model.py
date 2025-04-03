from dataclasses import dataclass
from typing import Union
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from .interfaces import (
    BoxModelSpacing,
    BoxModelV2Type,
    NodeType,
    OverflowType,
    PropertiesDimensionalType,
    Size2d,
)
from .constants import (
    DEFAULT_SCROLL_BAR_WIDTH,
)

@dataclass
class Overflow(OverflowType):
    x: str = "visible"
    y: str = "visible"
    scrollable: bool = False
    scrollable_x: bool = False
    scrollable_y: bool = False
    is_boundary: bool = False

    def __init__(self, overflow: str = "visible", overflow_x: str = None, overflow_y: str = None):
        self.x = overflow_x or overflow or "visible"
        self.y = overflow_y or overflow or "visible"
        self.scrollable_x = self.x == "scroll" or self.x == "auto"
        self.scrollable_y = self.y == "scroll" or self.y == "auto"
        self.scrollable = self.scrollable_x or self.scrollable_y
        self.is_boundary = self.x != "visible" or self.y != "visible"

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

class BoxModelV2(BoxModelV2Type):
    def __init__(
        self,
        properties: PropertiesDimensionalType,
        content_size: Size2d = Size2d(0, 0),
        clip_nodes: list[NodeType] = [],
        relative_positional_node: NodeType = None,
    ):
        self.id = properties.id
        self.width = properties.width
        self.height = properties.height
        self.min_width = properties.min_width
        self.min_height = properties.min_height
        self.max_width = properties.max_width
        self.max_height =  properties.max_height
        self.width_percent = properties.width if isinstance(properties.width, str) and "%" in properties.width else None
        self.height_percent = properties.height if isinstance(properties.height, str) and "%" in properties.height else None
        self.fixed_width = bool(properties.width)
        self.fixed_height = bool(properties.height)
        self.overflow = properties.overflow
        self.overflow_size = Size2d(0, 0)
        self.position = properties.position
        self._position_left = properties.left
        self._position_top = properties.top
        self._position_right = properties.right
        self._position_bottom = properties.bottom

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

        self.scroll_bar_track_rect = None
        self.scroll_bar_thumb_rect = None

        self.clip_nodes = clip_nodes
        self.relative_positional_node = relative_positional_node

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
    def border_rect(self):
        return Rect(self.border_pos.x, self.border_pos.y, self.border_size.width, self.border_size.height)

    @property
    def padding_rect(self):
        return Rect(self.padding_pos.x, self.padding_pos.y, self.padding_size.width, self.padding_size.height)

    @property
    def content_rect(self):
        return Rect(self.content_pos.x, self.content_pos.y, self.content_size.width, self.content_size.height)

    @property
    def content_children_rect(self):
        return Rect(self.content_children_pos.x, self.content_children_pos.y, self.content_children_size.width, self.content_children_size.height)

    @property
    def content_children_with_padding_size(self):
        return Size2d(
            self.content_children_size.width + self.padding_spacing.left + self.padding_spacing.right,
            self.content_children_size.height + self.padding_spacing.top + self.padding_spacing.bottom
        )

    @property
    def padding_with_scroll_bar_rect(self):
        return Rect(
            self.padding_pos.x,
            self.padding_pos.y,
            self.padding_size.width + self.conditional_scroll_bar_y_width,
            self.padding_size.height
        )

    @property
    def conditional_scroll_bar_y_width(self):
        return DEFAULT_SCROLL_BAR_WIDTH if self.has_scroll_bar_y() else 0

    @classmethod
    def _resolve_percent(self, value, total):
        if isinstance(value, str) and "%" in value and total:
            percent = float(value.strip().replace("%", "")) / 100
            return int(total * percent)
        return value

    @property
    def position_left(self):
        return BoxModelV2._resolve_percent(self._position_left, self.border_size.width)

    @property
    def position_top(self):
        return BoxModelV2._resolve_percent(self._position_top, self.border_size.height)

    @property
    def position_right(self):
        return BoxModelV2._resolve_percent(self._position_right, self.border_size.width)

    @property
    def position_bottom(self):
        return BoxModelV2._resolve_percent(self._position_bottom, self.border_size.height)

    @property
    def intrinsic_margin_size_with_bounding_constraints(self):
        width = self.intrinsic_margin_size.width
        max_width = self.width or self.max_width
        if max_width and max_width < width:
            width = max_width
        height = self.intrinsic_margin_size.height
        max_height = self.height or self.max_height
        if max_height and max_height < height:
            height = max_height
        return Size2d(width, height)

    @property
    def clip_rect(self):
        clip_rect = None
        for node_ref in self.clip_nodes:
            node = node_ref()
            if clip_rect:
                clip_rect = clip_rect.intersect(node.box_model_v2.padding_rect)
            else:
                clip_rect = node.box_model_v2.padding_rect
        return clip_rect

    @property
    def visible_rect(self):
        return self.clip_rect.intersect(self.padding_rect) if self.clip_rect else self.padding_rect

    @staticmethod
    def content_size_to_border_size(
        content_size: Size2d,
        padding_spacing: BoxModelSpacing,
        border_spacing: BoxModelSpacing,
        conditional_scroll_bar_y_width: bool
    ) -> Size2d:
        return Size2d(
            content_size.width + padding_spacing.left + padding_spacing.right + border_spacing.left + border_spacing.right + conditional_scroll_bar_y_width,
            content_size.height + padding_spacing.top + padding_spacing.bottom + border_spacing.top + border_spacing.bottom
        )

    def init_intrinsic_sizes(self, content_size: Size2d):
        init_width = self.width or self.min_width or 0
        init_height = self.height or self.min_height or 0

        if self.relative_positional_node:
            relative_node = self.relative_positional_node()
            box_model = relative_node.box_model_v2
            if box_model:
                container_width = box_model.border_size.width
                container_height = box_model.border_size.height

                if self.width_percent:
                    init_width = BoxModelV2._resolve_percent(self.width_percent, container_width)
                if self.height_percent:
                    init_height = BoxModelV2._resolve_percent(self.height_percent, container_height)

                left = BoxModelV2._resolve_percent(self._position_left, container_width)
                right = BoxModelV2._resolve_percent(self._position_right, container_width)
                top = BoxModelV2._resolve_percent(self._position_top, container_height)
                bottom = BoxModelV2._resolve_percent(self._position_bottom, container_height)

                if not init_width and left is not None and right is not None:
                    init_width = container_width - left - right

                if not init_height and top is not None and bottom is not None:
                    init_height = container_height - top - bottom

        if content_size.width or content_size.height:
            if init_width or init_height:
                content_to_border_size = BoxModelV2.content_size_to_border_size(
                    content_size,
                    self.padding_spacing,
                    self.border_spacing,
                    self.conditional_scroll_bar_y_width
                )
                self.resolve_intrinsic_sizes_from_border_size(
                    Size2d(
                        max(init_width, content_to_border_size.width),
                        max(init_height, content_to_border_size.height)
                    )
                )
            else:
                self.resolve_intrinsic_sizes_from_content_size(content_size)
        else:
            self.resolve_intrinsic_sizes_from_border_size(
                Size2d(init_width, init_height)
            )
        self.init_calculated_sizes()

    def shrink_content_children_size(self, shrunk_content_children_size: Size2d):
        if shrunk_content_children_size.width < self.content_children_size.width:
            self.content_children_size.width = shrunk_content_children_size.width
        if shrunk_content_children_size.height < self.content_children_size.height:
            self.content_children_size.height = shrunk_content_children_size.height

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
            self.intrinsic_padding_size.width + self.border_spacing.left + self.border_spacing.right + self.conditional_scroll_bar_y_width,
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

    def constrain_size(self, available_size: Size2d = None, overflow: Overflow = None) -> Size2d:
        margin_width = self.calculated_margin_size.width
        margin_height = self.calculated_margin_size.height
        content_constraint_width = self.calculated_content_size.width
        content_constraint_height = self.calculated_content_size.height
        available_size_width = available_size.width if available_size else None
        available_size_height = available_size.height if available_size else None

        # if not getattr(overflow, 'scrollable_x', False):
        max_width = self.max_width or self.width

        if max_width:
            margin_width = min(margin_width, max_width + self.margin_spacing.left + self.margin_spacing.right)

        if available_size_width:
            margin_width = min(margin_width, available_size_width) if margin_width else available_size_width
        # if not max_width and not available_size_width:
        #     margin_width = max(margin_width, self.intrinsic_margin_size.width)

        if margin_width < self.calculated_margin_size.width:
            self.overflow_size.width = self.calculated_margin_size.width - margin_width
            border_width = margin_width - self.margin_spacing.left - self.margin_spacing.right
            padding_width = border_width - self.border_spacing.left - self.border_spacing.right - self.conditional_scroll_bar_y_width
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

        if getattr(overflow, 'scrollable_x', False):
            # border_width = self.calculated_border_size.width
            # padding_width = self.calculated_padding_size.width
            # content_width = self.calculated_content_size.width
            content_children_width = self.calculated_content_children_size.width
            content_constraint_width = None
            if available_size_width:
                self.overflow_size.width = max(0, margin_width - available_size_width)

        # if not getattr(overflow, 'scrollable_y', False):
        max_height = self.max_height or self.height

        if max_height:
            margin_height = min(margin_height, max_height + self.margin_spacing.top + self.margin_spacing.bottom)

        if available_size_height:
            margin_height = min(margin_height, available_size_height) if margin_height else available_size_height
        # if not max_height and not available_size_height:
        #     margin_height = max(margin_height, self.intrinsic_margin_size.height)


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

        if getattr(overflow, 'scrollable_y', False):
            content_children_height = self.calculated_content_children_size.height
            if available_size_height:
                self.overflow_size.height = max(0, margin_height - available_size_height)
            content_constraint_height = None

        self.margin_size = Size2d(margin_width, margin_height)
        self.border_size = Size2d(border_width, border_height)
        self.padding_size = Size2d(padding_width, padding_height)
        self.content_size = Size2d(content_width, content_height)
        self.content_children_size = Size2d(content_children_width, content_children_height)

        content_constraint_size = Size2d(content_constraint_width, content_constraint_height) \
            if content_constraint_width or content_constraint_height else None

        return content_constraint_size

    def reposition(self, offset: Point2d):
        self.margin_pos += offset
        self.border_pos += offset
        self.padding_pos += offset
        self.content_pos += offset
        self.content_children_pos += offset
        if self.scroll_bar_thumb_rect:
            self.scroll_bar_thumb_rect.x += offset.x
            self.scroll_bar_thumb_rect.y += offset.y
        if self.scroll_bar_track_rect:
            self.scroll_bar_track_rect.x += offset.x
            self.scroll_bar_track_rect.y += offset.y

    def set_top_left(self, top_left: Point2d):
        diff = top_left - self.margin_pos
        self.reposition(diff)

    def shift_relative_position(self, cursor):
        if self.position == "relative":
            offset = Point2d(
                self.position_left or 0,
                self.position_top or 0
            )
            if self.position_right:
                offset.x = -self.position_right
            if self.position_bottom:
                offset.y = -self.position_bottom
            self.reposition(offset)
            cursor.move_to(cursor.x + offset.x, cursor.y + offset.y)

    def position_from_relative_parent(self, cursor: Point2d):
        relative_positional_node = self.relative_positional_node()
        relative_border = relative_positional_node.box_model_v2.border_rect

        x = relative_border.x
        y = relative_border.y
        left = self._position_left
        right = self._position_right
        top = self._position_top
        bottom = self._position_bottom

        if left is not None:
            x += BoxModelV2._resolve_percent(left, relative_border.width)
        elif right is not None:
            x += (
                relative_border.width
                - BoxModelV2._resolve_percent(right, relative_border.width)
                - self.margin_size.width
            )

        if top is not None:
            y += BoxModelV2._resolve_percent(top, relative_border.height)
        elif bottom is not None:
            y += (
                relative_border.height
                - BoxModelV2._resolve_percent(bottom, relative_border.height)
                - self.margin_size.height
            )

        cursor.move_to(x, y)

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

    def is_visible(self) -> Union[bool, str]:
        clip_rect = self.clip_rect
        if not clip_rect:
            return True

        region = self.margin_rect
        new_rect = region.intersect(clip_rect)
        if region.width == new_rect.width and region.height == new_rect.height:
            return True
        elif new_rect.width > 0 and new_rect.height > 0:
            return "partial"
        return False

    def has_scroll_bar_y(self):
        return self.overflow.scrollable_y

    def resolve_scroll_bar_rects(self, offset_y):
        view_height = self.padding_size.height
        total_scrollable_height = self.content_children_with_padding_size.height

        if view_height and total_scrollable_height and total_scrollable_height > view_height:
            self.scroll_bar_track_rect = Rect(
                self.padding_pos.x + self.padding_size.width,
                self.padding_pos.y,
                DEFAULT_SCROLL_BAR_WIDTH,
                self.padding_size.height
            )

            thumb_height = view_height * (view_height / total_scrollable_height)
            thumb_pos_y = self.padding_pos.y + \
                (-offset_y / (total_scrollable_height - view_height)) \
                * (self.padding_size.height - thumb_height)

            self.scroll_bar_thumb_rect = Rect(
                self.padding_pos.x + self.padding_size.width,
                thumb_pos_y,
                DEFAULT_SCROLL_BAR_WIDTH,
                thumb_height
            )

    def adjust_scroll_y(self, offset_y: int):
        self.content_children_pos.y += offset_y
        self.resolve_scroll_bar_rects(offset_y)

    def gc(self):
        self.clip_nodes = []
        self.relative_positional_node = None