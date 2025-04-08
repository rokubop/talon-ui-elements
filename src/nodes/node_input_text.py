from talon import app
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect
from ..constants import ELEMENT_ENUM_TYPE
from ..box_model import BoxModelV2
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

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        self.box_model = BoxModelV2(
            self.properties,
            clip_nodes=self.clip_nodes,
            relative_positional_node=self.relative_positional_node
        )
        return self.box_model.intrinsic_margin_size

    def v2_build_render_list(self):
        self.tree.append_to_render_list(
            node=self,
            draw=self.v2_render
        )

    def v2_render(self, c: SkiaCanvas):
        self.v2_render_background(c)
        self.v2_render_borders(c)

        top_left_pos = self.box_model.content_children_pos.copy()

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

        input_rect = Rect(
            top_left_pos.x,
            top_left_pos.y + platform_adjustment_x,
            self.box_model.content_size.width,
            self.box_model.content_size.height + platform_adjustment_height
        )
        top_offset = 0
        clip_rect = self.box_model.clip_rect
        if clip_rect:
            new_input_rect = input_rect.intersect(clip_rect)
            top_offset = new_input_rect.top - input_rect.top
            input_rect = new_input_rect
        entity_manager.update_input_rect(self.id, input_rect, top_offset=top_offset)