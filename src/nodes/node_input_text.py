from talon import app
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.typeface import Typeface
from talon.types import Rect
from ..constants import ELEMENT_ENUM_TYPE
from ..box_model import BoxModelLayout, BoxModelV2
from ..cursor import Cursor
from ..entity_manager import entity_manager
from ..properties import NodeInputTextProperties
from .node import Node

class NodeInputText(Node):
    def __init__(self, properties: NodeInputTextProperties = None):
        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["input_text"],
            properties=properties
        )
        self.interactive = True
        self.properties.width = self.properties.width or round(self.properties.font_size * 15)
        self.properties.height = self.properties.height or round(self.properties.font_size * 2.2)
        self.properties.background_color = self.properties.background_color or "333333"
        self.properties.color = self.properties.color or "FFFFFF"
        self.properties.value = self.properties.value or ""
        if self.properties.gap is None:
            self.properties.gap = 16

    @property
    def input(self):
        input_data = entity_manager.get_input_data(self.id)
        if input_data:
            return input_data.input
        return None

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        if not self.tree.redistribute_box_model:
            self.box_model = BoxModelLayout(
                cursor.virtual_x,
                cursor.virtual_y,
                self.properties.margin,
                self.properties.padding,
                self.properties.border,
                self.properties.width,
                self.properties.height,
                constraint_nodes=self.constraint_nodes)

        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        c.paint.textsize = self.properties.font_size
        c.paint.typeface = Typeface.from_name(self.properties.font_family)

        self.box_model.accumulate_intrinsic_content_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, self.properties.width, self.properties.height))
        self.box_model.accumulate_content_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, self.properties.width, self.properties.height))
        return self.box_model.margin_rect, self.box_model.intrinsic_margin_rect

    def grow_intrinsic_size(self, c: SkiaCanvas, cursor: Cursor):
        return self.box_model.margin_rect

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        self.box_model_v2 = BoxModelV2(self.properties, clip_nodes=self.clip_nodes)
        return self.box_model_v2.intrinsic_margin_size

    def render_background(self, c: SkiaCanvas, cursor: Cursor):
        cursor.move_to(self.box_model.padding_rect.x, self.box_model.padding_rect.y)
        if self.properties.background_color:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.background_color

            if self.properties.border_radius:
                properties = RoundRect.from_rect(self.box_model.padding_rect, x=self.properties.border_radius, y=self.properties.border_radius)
                c.draw_rrect(properties)
            else:
                c.draw_rect(self.box_model.padding_rect)

    def v2_render(self, c: SkiaCanvas):
        self.v2_render_background(c)
        self.v2_render_borders(c)

        top_left_pos = self.box_model_v2.content_children_pos.copy()

        # Reason why node doesn't "own" the input:
        # - because nodes get recreated on every render
        # - input is a stateful entity that needs to persist
        if not entity_manager.get_input_data(self.id):
            entity_manager.create_input(self)

        platform_adjustment_x = 0
        platform_adjustment_height = 0

        if app.platform == "mac":
            platform_adjustment_x = 6
            platform_adjustment_height = -6

        # get_clip_rect = self.box_model.constraints["get_clip_rect"]
        # clip_rect = get_clip_rect() if get_clip_rect else None
        input_rect = Rect(
            top_left_pos.x,
            top_left_pos.y + platform_adjustment_x,
            self.box_model_v2.content_size.width,
            self.box_model_v2.content_size.height + platform_adjustment_height
        )
        top_offset = 0
        # if clip_rect:
        #     new_input_rect = input_rect.intersect(clip_rect)
        #     top_offset = new_input_rect.top - input_rect.top
        #     input_rect = new_input_rect
        entity_manager.update_input_rect(self.id, input_rect, top_offset=top_offset)

    def render(self, c: SkiaCanvas, cursor: Cursor):
        self.box_model.position_for_render(cursor, self.properties.flex_direction, self.properties.align_items, self.properties.justify_content)

        self.render_background(c, cursor)

        cursor.move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)

        # Reason why node doesn't "own" the input:
        # - because nodes get recreated on every render
        # - input is a stateful entity that needs to persist
        if not entity_manager.get_input_data(self.id):
            entity_manager.create_input(self)

        platform_adjustment_x = 0
        platform_adjustment_height = 0

        if app.platform == "mac":
            platform_adjustment_x = 6
            platform_adjustment_height = -6

        get_clip_rect = self.box_model.constraints["get_clip_rect"]
        clip_rect = get_clip_rect() if get_clip_rect else None
        input_rect = Rect(cursor.x, cursor.y + platform_adjustment_x, self.box_model.content_rect.width, self.box_model.content_rect.height + platform_adjustment_height)
        top_offset = 0
        if clip_rect:
            new_input_rect = input_rect.intersect(clip_rect)
            top_offset = new_input_rect.top - input_rect.top
            input_rect = new_input_rect
        entity_manager.update_input_rect(self.id, input_rect, top_offset=top_offset)

        return self.box_model.margin_rect
