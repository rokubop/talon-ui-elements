from dataclasses import dataclass
from talon import cron
from talon.experimental.textarea import DarkThemeLabels, TextArea
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect
from ..constants import ELEMENT_ENUM_TYPE
from ..box_model import BoxModelLayout
from ..cursor import Cursor
from ..entity_manager import entity_manager
from ..options import NodeInputTextOptions
from ..state_manager import state_manager
from .node import Node

class NodeInputText(Node):
    def __init__(self, options: NodeInputTextOptions = None):
        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["input_text"],
            options=options
        )
        self.interactive = True
        self.options.width = self.options.width or round(self.options.font_size * 15)
        self.options.height = self.options.height or round(self.options.font_size * 2.2)
        self.options.background_color = self.options.background_color or "333333"
        self.options.color = self.options.color or "FFFFFF"
        self.options.value = self.options.value or ""
        if self.options.gap is None:
            self.options.gap = 16

    @property
    def input(self):
        input_data = entity_manager.get_input_data(self.id)
        if input_data:
            return input_data.input
        return None

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        self.box_model = BoxModelLayout(
            cursor.virtual_x,
            cursor.virtual_y,
            self.options.margin,
            self.options.padding,
            self.options.border,
            self.options.width,
            self.options.height)

        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        c.paint.textsize = self.options.font_size
        self.box_model.accumulate_content_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, self.options.width, self.options.height))
        return self.box_model.margin_rect

    def grow_intrinsic_size(self, c: SkiaCanvas, cursor: Cursor):
        return self.box_model.margin_rect

    def render_background(self, c: SkiaCanvas, cursor: Cursor):
        cursor.move_to(self.box_model.padding_rect.x, self.box_model.padding_rect.y)
        if self.options.background_color:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.options.background_color

            if self.options.border_radius:
                options = RoundRect.from_rect(self.box_model.padding_rect, x=self.options.border_radius, y=self.options.border_radius)
                c.draw_rrect(options)
            else:
                c.draw_rect(self.box_model.padding_rect)

    def render(self, c: SkiaCanvas, cursor: Cursor, scroll_region_key: int = None):
        self.box_model.position_for_render(cursor, self.options.flex_direction, self.options.align_items, self.options.justify_content)

        self.render_background(c, cursor)

        cursor.move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)

        # Reason why node doesn't "own" the input:
        # - because nodes get recreated on every render
        # - input is a stateful entity that needs to persist
        if not entity_manager.get_input_data(self.id):
            entity_manager.create_input(self)

        input_rect = Rect(cursor.x, cursor.y, self.box_model.content_rect.width, self.box_model.content_rect.height)
        entity_manager.update_input_rect(self.id, input_rect)

        return self.box_model.margin_rect