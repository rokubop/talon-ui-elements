from talon.skia import Path
from talon.skia.canvas import Canvas as SkiaCanvas, Paint
from talon.types import Point2d, Rect
from ..box_model import BoxModelLayout
from ..cursor import Cursor
from ..interfaces import NodeSvgType, NodeType
from ..properties import NodeSvgProperties
from .node import Node
import re

def scale_d(path, scale_factor):
    def scale_coordinates(coords):
        return [float(c) * scale_factor if c.replace('.', '', 1).isdigit() else c for c in coords]

    def process_subpath(subpath):
        scaled_segments = []
        pattern = re.compile(r"([a-zA-Z])([^a-zA-Z]*)")
        matches = pattern.findall(subpath)

        for command, parameters in matches:
            params = re.findall(r"[-+]?\d*\.?\d+", parameters)
            if params:
                scaled_params = scale_coordinates(params)
                scaled_segments.append(f"{command}{' '.join(map(str, scaled_params))}")
            else:
                scaled_segments.append(command)

        return " ".join(scaled_segments)

    commands = path.strip().split("M")[1:]
    scaled_path_segments = []

    for command in commands:
        subpath = f"M{command.strip()}"
        scaled_subpath = process_subpath(subpath)
        scaled_path_segments.append(scaled_subpath)

    return " ".join(scaled_path_segments)

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
        new_d = scale_d(self.properties.d, scale)
        path = Path.from_svg(new_d)
        translated_path = Path()
        translated_path.add_path_offset(path, dx=cursor.x, dy=cursor.y, add_mode=Path.AddMode.APPEND)

        prev_paint = c.paint.clone()

        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke

        c.draw_path(translated_path, c.paint)

        c.paint = prev_paint

class NodeSvgRect(Node, NodeType):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_rect", properties=properties)

    def virtual_render(self):
        pass

    def render(self, c: SkiaCanvas, cursor: Cursor):
        scale = self.parent_node.size / 24

        x = self.properties.x * scale
        y = self.properties.y * scale
        width = self.properties.width * scale
        height = self.properties.height * scale
        rx = self.properties.rx * scale
        ry = self.properties.ry * scale

        prev_paint = c.paint.clone()

        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke
        c.draw_round_rect(Rect(x + cursor.x, y + cursor.y, width, height), rx, ry)

        c.paint = prev_paint

class NodeSvgCircle(Node, NodeType):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_circle", properties=properties)

    def virtual_render(self):
        pass

    def render(self, c: SkiaCanvas, cursor: Cursor):
        scale = self.parent_node.size / 24

        cx = self.properties.cx * scale
        cy = self.properties.cy * scale
        r = self.properties.r * scale

        prev_paint = c.paint.clone()

        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke
        c.draw_circle(cx + cursor.x, cy + cursor.y, r)

        c.paint = prev_paint

class NodeSvgPolyline(Node, NodeType):
    def __init__(self, element_type: str, properties: NodeSvgProperties = None):
        super().__init__(element_type=element_type, properties=properties)

    def virtual_render(self):
        pass

    def render(self, c: SkiaCanvas, cursor: Cursor):
        scale = self.parent_node.size / 24

        raw_points = self.properties.points.split(" ")
        points = [
            (
                float(raw_points[i]) * scale + cursor.x,
                float(raw_points[i + 1]) * scale + cursor.y
            )
            for i in range(0, len(raw_points), 2)
        ]

        prev_paint = c.paint.clone()

        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke
        c.draw_points(mode=c.PointMode.POLYGON, points=points)

        c.paint = prev_paint

class NodeSvgLine(Node, NodeType):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_line", properties=properties)

    def virtual_render(self):
        pass

    def render(self, c: SkiaCanvas, cursor: Cursor):
        scale = self.parent_node.size / 24

        x1 = self.properties.x1 * scale + cursor.x
        y1 = self.properties.y1 * scale + cursor.y
        x2 = self.properties.x2 * scale + cursor.x
        y2 = self.properties.y2 * scale + cursor.y

        prev_paint = c.paint.clone()

        c.paint.style = c.paint.Style.STROKE
        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke
        c.draw_line(x1, y1, x2, y2)

        c.paint = prev_paint