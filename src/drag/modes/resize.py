"""Dragging a `resizable` node's edge.

The node keeps its size until the drop. The outline is what moves.
"""

from talon.types import Point2d, Rect

from ...constants import RESIZE_MIN_HEIGHT, RESIZE_MIN_WIDTH
from ...events import ResizeEndEvent
from ...utils import get_scale, scale_value
from ..session import DragSession
from ..shapes import Outline


class ResizeSession(DragSession):
    kind = "resize"
    preview = True
    pause_renders = True

    def __init__(self, tree, node, edge: str):
        super().__init__(tree)
        self.node = node
        self.node_id = node.id
        self.edge = edge
        self.start_rect: Rect = None
        self.ghost: Rect = None
        self._radius = None
        self._resized: ResizeEndEvent = None
        self._on_resize_end = None

    def begin(self, gpos: Point2d) -> bool:
        box_model = getattr(self.node, "box_model", None)
        if not box_model or not box_model.border_rect:
            return False

        self.start_pos = gpos
        self.start_rect = box_model.border_rect.copy()
        self.ghost = self.start_rect.copy()
        self._radius = self.node.properties.get_border_radius()

        # The constraints the consumer declared, before any earlier resize
        # overrode them. Saved once per node, and outlives this session.
        constraints = self.tree.meta_state.resize_original_constraints
        if self.node_id not in constraints:
            constraints[self.node_id] = {
                "min_width": box_model.min_width,
                "min_height": box_model.min_height,
                "max_width": box_model.max_width,
                "max_height": box_model.max_height,
            }
        return True

    def move(self, gpos: Point2d) -> None:
        self.ghost = self._resolve_rect(gpos)

    def commit(self, gpos: Point2d) -> None:
        self.ghost = self._resolve_rect(gpos)
        ms = self.tree.meta_state
        scale = get_scale() or 1.0
        width = self.ghost.width / scale
        height = self.ghost.height / scale

        # Only the dragged axis is pinned. A side panel resized by its right
        # edge keeps stretching to its parent's height; pinning that too
        # froze it at whatever the window was tall when you let go.
        if "left" in self.edge or "right" in self.edge:
            ms.set_ref_property_override(self.node_id, "width", width)
            ms.set_ref_property_override(self.node_id, "max_width", width)
        if "top" in self.edge or "bottom" in self.edge:
            ms.set_ref_property_override(self.node_id, "height", height)
            ms.set_ref_property_override(self.node_id, "max_height", height)

        # A parent that centers or end-aligns its children moves the node when
        # its size changes. Cancel that out so it lands on the outline.
        compensation = self._layout_compensation()
        dx = (self.ghost.x - self.start_rect.x) + compensation.x
        dy = (self.ghost.y - self.start_rect.y) + compensation.y
        if (dx or dy) and self.node_id in ms._draggable_offset:
            ms._draggable_offset[self.node_id] = Point2d(
                ms._draggable_offset[self.node_id].x + dx,
                ms._draggable_offset[self.node_id].y + dy,
            )

        if hasattr(self.node, "save_resize_dimensions"):
            self.node.save_resize_dimensions(width, height)

        self._on_resize_end = getattr(self.node.properties, "on_resize_end", None)
        self._resized = ResizeEndEvent(
            id=self.node_id, width=width, height=height, edge=self.edge
        )
        self.tree.destroy_blockable_canvas()

    def settle(self) -> None:
        self.tree.render_base_canvas()
        if self._on_resize_end:
            self._on_resize_end(self._resized)

    def shapes(self) -> list:
        return [Outline(self.ghost, self._radius)]

    def _resolve_rect(self, gpos: Point2d) -> Rect:
        dx = gpos.x - self.start_pos.x
        dy = gpos.y - self.start_pos.y
        edge = self.edge
        sr = self.start_rect

        x, y, w, h = sr.x, sr.y, sr.width, sr.height
        if "right" in edge:
            w = sr.width + dx
        if "left" in edge:
            w = sr.width - dx
            x = sr.x + dx
        if "bottom" in edge:
            h = sr.height + dy
        if "top" in edge:
            h = sr.height - dy
            y = sr.y + dy

        constraints = self.tree.meta_state.resize_original_constraints.get(self.node_id, {})
        min_w = constraints.get("min_width") or scale_value(RESIZE_MIN_WIDTH)
        min_h = constraints.get("min_height") or scale_value(RESIZE_MIN_HEIGHT)
        max_w = constraints.get("max_width")
        max_h = constraints.get("max_height")

        if w < min_w:
            if "left" in edge:
                x = sr.x + sr.width - min_w
            w = min_w
        if max_w and w > max_w:
            if "left" in edge:
                x = sr.x + sr.width - max_w
            w = max_w

        if h < min_h:
            if "top" in edge:
                y = sr.y + sr.height - min_h
            h = min_h
        if max_h and h > max_h:
            if "top" in edge:
                y = sr.y + sr.height - max_h
            h = max_h

        return Rect(x, y, w, h)

    def _layout_compensation(self) -> Point2d:
        parent = self.node.parent_node
        if not parent:
            return Point2d(0, 0)

        dw = self.ghost.width - self.start_rect.width
        dh = self.ghost.height - self.start_rect.height
        flex_direction = parent.properties.flex_direction or "column"
        justify = parent.properties.justify_content or "flex_start"
        align = parent.properties.align_items or "stretch"

        def shift(delta, alignment):
            if alignment == "center":
                return delta / 2
            if alignment == "flex_end":
                return delta
            return 0

        if flex_direction == "column":
            return Point2d(shift(dw, align), shift(dh, justify))
        return Point2d(shift(dw, justify), shift(dh, align))
