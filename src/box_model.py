from dataclasses import dataclass
from typing import Union
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from .interfaces import BoxModelLayoutType, NodeType

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

@dataclass
class Overflow:
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
        # if self.scroll_box_rect:
        return Rect(
            self.margin_rect.x,
            self.margin_rect.y,
            self.content_rect.width + self.padding_spacing.left + self.padding_spacing.right + self.border_spacing.left + self.border_spacing.right + self.margin_spacing.left + self.margin_spacing.right,
            self.content_rect.height + self.padding_spacing.top + self.padding_spacing.bottom + self.border_spacing.top + self.border_spacing.bottom + self.margin_spacing.top + self.margin_spacing.bottom
        )
        # return self.margin_rect

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
        print("redistribute_from_rect", self.content_children_rect)
        self.clamp_dimensions()
        self.layout_scroll_box_rect()

    def clamp_dimensions(self):
        # if self.constraints["max_width"]:
        #     self.max_border_width = self.constraints["max_width"]
        #     self.max_margin_width = self.constraints["max_width"] + margin_spacing.left + margin_spacing.right
        # if self.max_height:
        #     self.max_content_height = self.content_height + max_height - height if max_height else None
        # if self.constraints["max_height"]:
        #     self.max_border_height = self.constraints["max_height"]
        #     self.max_margin_height = self.constraints["max_height"] + margin_spacing.top + margin_spacing.bottom

        if self.constraints["max_width"]:
            self.border_rect.width = min(self.border_rect.width, self.constraints["max_width"])
            self.margin_rect.width = self.border_rect.width + self.margin_spacing.left + self.margin_spacing.right
            # self.width = self.border_rect.width
        if self.constraints["max_height"]:
            self.border_rect.height = min(self.border_rect.height, self.constraints["max_height"])
            self.margin_rect.height = self.border_rect.height + self.margin_spacing.top + self.margin_spacing.bottom
            # self.height = self.border_rect.height


        # if self.max_margin_width and self.margin_rect.width > self.max_margin_width:
        #     self.margin_rect.width = self.max_margin_width
        # if self.max_margin_height and self.margin_rect.height > self.max_margin_height:
        #     self.margin_rect.height = self.max_margin_height
        # if self.max_border_width and self.border_rect.width > self.max_border_width:
        #     self.border_rect.width = self.max_border_width
        # if self.max_border_height and self.border_rect.height > self.max_border_height:
        #     self.border_rect.height = self.max_border_height

        # if self.max_width and self.width > self.max_width:
        #     self.width = self.max_width
        # if self.max_height and self.height > self.max_height:
        #     self.height = self.max_height

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
            # print("accumulate_outer_dimensions_height", self.content_children_rect)
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

        # print("accumulate_content_dimensions", self.content_children_rect)

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

                    thumb_width = 10
                    thumb_y = self.scroll_box_rect.y + scroll_y_percentage * (self.scroll_box_rect.height - thumb_height)
                    thumb_y = max(self.scroll_box_rect.y, min(thumb_y, self.scroll_box_rect.y + self.scroll_box_rect.height - thumb_height))

                    bar_rect = Rect(
                        self.scroll_box_rect.x + self.scroll_box_rect.width - thumb_width,
                        self.scroll_box_rect.y,
                        thumb_width,
                        self.scroll_box_rect.height
                    )
                    c.paint.color = "FFFFFF22"
                    c.draw_rect(bar_rect)

                    thumb_rect = Rect(
                        self.scroll_box_rect.x + self.scroll_box_rect.width - thumb_width,
                        thumb_y,
                        thumb_width,
                        thumb_height
                    )
                    c.paint.color = "FFFFFF44"
                    c.draw_rect(thumb_rect)

    def reduce_constraints(self, constraint_nodes: list[NodeType]) -> list[NodeType]:
        constraints = {
            # "width": None,
            # "height": None,
            "max_width": None,
            "max_height": None,
            "get_clip_rect": None
        }

        def get_clip_rect(node: NodeType):
            return lambda: node.box_model.scroll_box_rect

        if constraint_nodes:
            for node in constraint_nodes:
                # if node.properties.width:
                #     constraints["width"] = min(constraints["width"], node.properties.width) \
                #         if constraints["width"] else node.properties.width
                # if node.properties.height:
                #     constraints["height"] = min(constraints["height"], node.properties.height) \
                #         if constraints["height"] else node.properties.height
                if node.properties.max_width:
                    constraints["max_width"] = min(constraints["max_width"], node.properties.max_width) \
                        if constraints["max_width"] else node.properties.max_width
                if node.properties.max_height:
                    constraints["max_height"] = min(constraints["max_height"], node.properties.max_height) \
                        if constraints["max_height"] else node.properties.max_height
                if node.properties.is_scrollable():
                    constraints["get_clip_rect"] = get_clip_rect(node)

        return constraints