import re
from talon.skia import Path
from talon.skia.canvas import Canvas as SkiaCanvas, Paint
from talon.types import Rect
from .node import Node
from ..box_model import BoxModelV2
from ..cursor import Cursor
from ..interfaces import NodeSvgType, NodeType, Size2d
from ..properties import NodeSvgProperties

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

class NodeRenderOnly():
    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        pass

    def v2_layout(self, cursor: Cursor):
        self.box_model.shift_relative_position(cursor)

class NodeSvg(Node, NodeSvgType):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg", properties=properties)
        self.size = self.properties.size
        self.stroke_cap = linecap[self.properties.stroke_linecap]
        self.stroke_join = linejoin[self.properties.stroke_linejoin]
        self.properties.width = self.properties.width or self.properties.size
        self.properties.height = self.properties.height or self.properties.size

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        self.box_model = BoxModelV2(
            self.properties,
            Size2d(self.properties.width, self.properties.height),
            self.clip_nodes,
            self.relative_positional_node
        )
        return self.box_model.intrinsic_margin_size

class NodeSvgPath(Node, NodeType, NodeRenderOnly):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_path", properties=properties)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.v2_render
            )

    def v2_render_decorator(self, c):
        return self.v2_render(c)

    def v2_render(self, c: SkiaCanvas):
        scale = self.parent_node.size / 24
        top_left_pos = self.parent_node.box_model.content_children_pos
        new_d = scale_d(self.properties.d, scale)
        path = Path.from_svg(new_d)
        translated_path = Path()
        translated_path.add_path_offset(path, dx=top_left_pos.x, dy=top_left_pos.y, add_mode=Path.AddMode.APPEND)

        prev_paint = c.paint.clone()

        c.paint.style = c.paint.Style.STROKE
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke

        if self.properties.fill and self.properties.fill != "none":
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.fill

        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale

        c.draw_path(translated_path, c.paint)

        c.paint = prev_paint

class NodeSvgRect(Node, NodeType, NodeRenderOnly):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_rect", properties=properties)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.v2_render
            )

    def v2_render_decorator(self, c):
        return self.v2_render(c)

    def v2_render(self, c: SkiaCanvas):
        scale = self.parent_node.size / 24

        x = self.properties.x * scale
        y = self.properties.y * scale
        width = self.properties.width * scale
        height = self.properties.height * scale
        rx = self.properties.rx * scale
        ry = self.properties.ry * scale

        prev_paint = c.paint.clone()

        top_left_pos = self.parent_node.box_model.content_children_pos

        c.paint.style = c.paint.Style.STROKE
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke

        if self.properties.fill and self.properties.fill != "none":
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.fill

        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.draw_round_rect(Rect(x + top_left_pos.x, y + top_left_pos.y, width, height), rx, ry)

        c.paint = prev_paint

class NodeSvgCircle(Node, NodeType, NodeRenderOnly):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_circle", properties=properties)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.v2_render
            )

    def v2_render_decorator(self, c):
        return self.v2_render(c)

    def v2_render(self, c: SkiaCanvas):
        scale = self.parent_node.size / 24

        cx = self.properties.cx * scale
        cy = self.properties.cy * scale
        r = self.properties.r * scale

        prev_paint = c.paint.clone()

        top_left_pos = self.parent_node.box_model.content_children_pos

        c.paint.style = c.paint.Style.STROKE
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke

        if self.properties.fill and self.properties.fill != "none":
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.fill

        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.draw_circle(cx + top_left_pos.x, cy + top_left_pos.y, r)

        c.paint = prev_paint

class NodeSvgPolyline(Node, NodeType, NodeRenderOnly):
    def __init__(self, element_type: str, properties: NodeSvgProperties = None):
        super().__init__(element_type=element_type, properties=properties)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.v2_render
            )

    def v2_render_decorator(self, c):
        return self.v2_render(c)

    def v2_render(self, c: SkiaCanvas):
        scale = self.parent_node.size / 24

        raw_points = self.properties.points.split(" ")
        top_left_pos = self.parent_node.box_model.content_children_pos
        points = [
            (
                float(raw_points[i]) * scale + top_left_pos.x,
                float(raw_points[i + 1]) * scale + top_left_pos.y
            )
            for i in range(0, len(raw_points), 2)
        ]

        prev_paint = c.paint.clone()

        top_left_pos = self.parent_node.box_model.content_children_pos

        c.paint.style = c.paint.Style.STROKE
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke

        if self.properties.fill and self.properties.fill != "none":
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.fill

        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.draw_points(mode=c.PointMode.POLYGON, points=points)

        c.paint = prev_paint

class NodeSvgLine(Node, NodeType, NodeRenderOnly):
    def __init__(self, properties: NodeSvgProperties = None):
        super().__init__(element_type="svg_line", properties=properties)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.v2_render
            )

    def v2_render_decorator(self, c):
        return self.v2_render(c)

    def v2_render(self, c: SkiaCanvas):
        scale = self.parent_node.size / 24

        x1 = self.properties.x1 * scale
        y1 = self.properties.y1 * scale
        x2 = self.properties.x2 * scale
        y2 = self.properties.y2 * scale

        prev_paint = c.paint.clone()

        top_left_pos = self.parent_node.box_model.content_children_pos

        c.paint.style = c.paint.Style.STROKE
        c.paint.color = self.properties.stroke or self.parent_node.properties.stroke

        if self.properties.fill and self.properties.fill != "none":
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.fill

        c.paint.stroke_cap = linecap[self.properties.stroke_linecap] if self.properties.stroke_linecap else self.parent_node.stroke_cap
        c.paint.stroke_join = linejoin[self.properties.stroke_linejoin] if self.properties.stroke_linejoin else self.parent_node.stroke_join
        c.paint.stroke_width = (self.properties.stroke_width or self.parent_node.properties.stroke_width) * scale
        c.draw_line(x1 + top_left_pos.x, y1 + top_left_pos.y, x2 + top_left_pos.x, y2 + top_left_pos.y)

        c.paint = prev_paint