from talon.skia.canvas import Canvas as SkiaCanvas
from ..cursor import Cursor
from ..properties import Properties
from .node_container import NodeContainer

class NodeButton(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="button", properties=properties)
        self.on_click = self.properties.on_click or (lambda: None)
        self.is_hovering = False
        self.interactive = True

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        if self.element_type == "button" and self.tree.render_version == 1 and not self.properties.background_color:
            # render_version 2+ we don't add a default background color for button
            self.properties.background_color = "444444"

        return super().virtual_render(c, cursor)

    def render(self, c: SkiaCanvas, cursor: Cursor):
        return super().render(c, cursor)

    def grow_intrinsic_size(self, c, cursor):
        return super().grow_intrinsic_size(c, cursor)