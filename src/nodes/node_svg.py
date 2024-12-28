from talon.skia import Path
from talon.skia.canvas import Canvas as SkiaCanvas, Paint
from talon.types import Point2d
from ..box_model import BoxModelLayout
from ..cursor import Cursor
from ..interfaces import NodeSvgType, NodeType
from ..properties import NodeSvgProperties
from .node import Node

def scale_path(path, scale_factor):
    scaled_path = Path()
    subpath_start = True

    commands = path.strip().split("M")[1:]

    for command in commands:
        subpath = f"M{command.strip()}"

        subpath_path = Path.from_svg(subpath)
        for i in range(subpath_path.count_points()):
            point = subpath_path.get_point(i)
            scaled_point = (point.x * scale_factor, point.y * scale_factor)

            if i == 0 or subpath_start:
                scaled_path.move_to(*scaled_point)
                subpath_start = False
            else:
                scaled_path.line_to(*scaled_point)

    return scaled_path

linecap = {
    "butt": 0,
    "round": 1,
    "square": 2
}

linejoin = {
    "miter": 0,
    "round": 1,
    "bevel": 2
}

class NodeSvg(Node, NodeSvgType):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg", properties=properties)
        self.size = self.properties.size
        self.stroke_cap = linecap[self.properties.stroke_linecap]
        self.stroke_join = linejoin[self.properties.stroke_linejoin]
        self.stroke_width = self.properties.stroke_width
        self.properties.width = self.properties.width or self.properties.size
        self.properties.height = self.properties.height or self.properties.size

    def grow_intrinsic_size(self, c: SkiaCanvas, cursor: Cursor):
        return self.box_model.margin_rect

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        if not self.tree.redistribute_box_model:
            self.box_model = BoxModelLayout(
                cursor.virtual_x,
                cursor.virtual_y,
                self.properties.margin,
                self.properties.padding,
                self.properties.border,
                self.properties.width,
                self.properties.height)

        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)

        return self.box_model.margin_rect

    def render(self, c: SkiaCanvas, cursor: Cursor, scroll_region_key: int = None):
        self.box_model.position_for_render(cursor, self.properties.flex_direction, self.properties.align_items, self.properties.justify_content)

        last_cursor = Point2d(cursor.x, cursor.y)

        for child in self.children_nodes:
            child.render(c, cursor)

        cursor.move_to(last_cursor.x, last_cursor.y)

        return self.box_model.margin_rect

class NodeSvgPath(Node, NodeType):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_path", properties=properties)

    def virtual_render(self):
        pass

    def render(self, c: SkiaCanvas, cursor: Cursor):
        scale = self.parent_node.size / 24
        path = scale_path(self.properties.d, scale)
        translated_path = Path()
        translated_path.add_path_offset(path, dx=cursor.x, dy=cursor.y, add_mode=Path.AddMode.APPEND)
        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_cap = self.parent_node.stroke_cap
        c.paint.stroke_join = self.parent_node.stroke_join
        c.paint.stroke_width = self.parent_node.stroke_width * scale
        c.paint.color = self.properties.color

        c.draw_path(translated_path, c.paint)

        c.paint = Paint() # Reset paint