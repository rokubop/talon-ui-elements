from dataclasses import dataclass
from typing import Union
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d

@dataclass
class BoxModelSpacing:
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

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

def grow_rect(orig_rect: Rect, new_rect: Rect):
    if new_rect.x < orig_rect.x:
        orig_rect.width += orig_rect.x - new_rect.x
        orig_rect.x = new_rect.x
    if new_rect.y < orig_rect.y:
        orig_rect.height += orig_rect.y - new_rect.y
        orig_rect.y = new_rect.y
    if new_rect.x + new_rect.width > orig_rect.x + orig_rect.width:
        orig_rect.width = new_rect.x + new_rect.width - orig_rect.x
    if new_rect.y + new_rect.height > orig_rect.y + orig_rect.height:
        orig_rect.height = new_rect.y + new_rect.height - orig_rect.y

@dataclass
class BoxModelLayout:
    margin_spacing: BoxModelSpacing
    padding_spacing: BoxModelSpacing
    border_spacing: BoxModelSpacing
    margin_rect: Rect
    padding_rect: Rect
    border_rect: Rect
    content_rect: Rect
    content_children_rect: Rect
    scroll_box_rect: Union[Rect, None] = None
    # Margin > Border > Scrollbox > Padding > Content > Content children

    def __init__(self, x: int, y: int, margin_spacing: BoxModelSpacing, padding_spacing: BoxModelSpacing, border_spacing: BoxModelSpacing, width: int = None, height: int = None):
        self.scrollable = True if height else False
        self.margin_spacing = margin_spacing
        self.padding_spacing = padding_spacing
        self.border_spacing = border_spacing
        self.margin_rect = Rect(x, y, width or 0, height or 0)
        self.border_rect = Rect(x + margin_spacing.left, y + margin_spacing.top, width or 0, height or 0)
        self.padding_rect = Rect(x + margin_spacing.left + border_spacing.left, y + margin_spacing.top + border_spacing.top, width - border_spacing.left - border_spacing.right if width else 0, height - border_spacing.top - border_spacing.bottom if height else 0)
        content_x = x + margin_spacing.left + border_spacing.left + padding_spacing.left
        content_y = y + margin_spacing.top + margin_spacing.top + padding_spacing.top
        content_width = width - padding_spacing.left - padding_spacing.right - border_spacing.left - border_spacing.right if width else 0
        content_height = height - padding_spacing.top - padding_spacing.bottom - border_spacing.top - border_spacing.bottom if height else 0
        self.content_rect = Rect(content_x, content_y, content_width, content_height)
        self.content_children_rect = Rect(self.content_rect.x, self.content_rect.y, 0, 0)

        if self.scrollable:
            self.scroll_box_rect = Rect(self.padding_rect.x, self.padding_rect.y, self.padding_rect.width, self.padding_rect.height)

    def accumulate_dimensions(self, rect: Rect):
        grow_rect(self.content_children_rect, rect)
        grow_rect(self.content_rect, rect)
        self.padding_rect.width = self.content_rect.width + self.padding_spacing.left + self.padding_spacing.right
        self.padding_rect.height = self.content_rect.height + self.padding_spacing.top + self.padding_spacing.bottom
        self.border_rect.width = self.padding_rect.width + self.border_spacing.left + self.border_spacing.right
        self.margin_rect.width = self.padding_rect.width + self.margin_spacing.left + self.margin_spacing.right

        # If the box is scrollable, the height of the margin/border is static
        # If the box is not scrollable, the height of the margin/border is dynamic so change it
        if not self.scrollable:
            self.border_rect.height = self.padding_rect.height + self.border_spacing.top + self.border_spacing.bottom
            self.margin_rect.height = self.padding_rect.height + self.margin_spacing.top + self.margin_spacing.bottom

    def prepare_render(self, cursor: Point2d, flex_direction: str = "column", align_items: str = "stretch", justify_content: str = "flex_start"):
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
            self.scroll_box_rect.x = self.padding_rect.x
            self.scroll_box_rect.y = self.padding_rect.y

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

    def adjust_scroll_y(self, scroll_y: int, scroll_y_percentage: Union[float, int], c: SkiaCanvas):
        if self.scrollable:
            self.padding_rect.y -= scroll_y
            self.content_rect.y -= scroll_y
            self.content_children_rect.y -= scroll_y

            if self.scroll_box_rect:
                visible_area_height = self.scroll_box_rect.height
                total_content_height = self.content_rect.height

                if total_content_height > visible_area_height:
                    thumb_height = max(20, visible_area_height * (visible_area_height / total_content_height))
                else:
                    thumb_height = visible_area_height

                thumb_width = 10

                c.paint.color = "FFFFFF22"
                c.draw_rect(
                    Rect(self.scroll_box_rect.x + self.scroll_box_rect.width - thumb_width,
                        self.scroll_box_rect.y,
                        thumb_width,
                        self.scroll_box_rect.height
                    ))

                thumb_y = self.scroll_box_rect.y + scroll_y_percentage * (self.scroll_box_rect.height - thumb_height)
                thumb_y = max(self.scroll_box_rect.y, min(thumb_y, self.scroll_box_rect.y + self.scroll_box_rect.height - thumb_height))

                c.draw_rect(
                    Rect(self.scroll_box_rect.x + self.scroll_box_rect.width - thumb_width,
                        thumb_y,
                        thumb_width,
                        thumb_height)
                )

@dataclass
class Margin(BoxModelSpacing):
    pass

@dataclass
class Padding(BoxModelSpacing):
    pass

@dataclass
class Border(BoxModelSpacing):
    pass