"""Moving a `draggable` node by its handle.

The node does not move. Its outline does, and the drop puts it there.
"""

from talon.types import Point2d, Rect

from ...core.state_manager import state_manager
from ...events import DragEndEvent
from ...utils import get_scale
from ..session import DragSession, drag_bounds
from ..shapes import Dim, Outline


class MoveSession(DragSession):
    kind = "move"
    preview = True
    pause_renders = True

    def __init__(self, tree, node):
        super().__init__(tree)
        self.node = node
        self.node_id = node.id
        self.origin: Rect = None
        self.offset = Point2d(0, 0)
        self._radius = None
        self._mouse_start: Point2d = None
        self._bounds: Rect = None
        self._dropped: DragEndEvent = None

    def begin(self, gpos: Point2d) -> bool:
        box_model = getattr(self.node, "box_model", None)
        if not box_model or not box_model.border_rect:
            return False

        self.start_pos = gpos
        self._mouse_start = state_manager.get_mousedown_start_pos() or gpos
        # Where the last committed layout put it. Nothing repaints the base
        # for the rest of the drag, so it stays true.
        self.origin = box_model.border_rect.copy()
        self._radius = self.node.properties.get_border_radius()
        self._bounds = drag_bounds(self.tree, self.node)

        state_manager.set_drag_active(True)
        self._apply(gpos)
        # Nothing is raised. focused=True is an OS raise, and doing it to the
        # base canvas flickers the window you are about to drag. Talon only
        # sank that canvas when it was the drag source, which it no longer is.
        return True

    def move(self, gpos: Point2d) -> None:
        self._apply(gpos)

    def commit(self, gpos: Point2d) -> None:
        self._apply(gpos)
        # Only now. Layout adds this offset to the node's position
        # (Node.v2_drag_offset), so publishing it mid-drag lets any repaint we
        # did not ask for move the real window under its own outline.
        self.tree.meta_state.set_drag_offset(self.node_id, self.offset)
        scale = getattr(self.tree, "scale", None) or get_scale() or 1.0
        self._dropped = DragEndEvent(
            id=self.node_id, dx=self.offset.x / scale, dy=self.offset.y / scale
        )

    def cancel(self) -> None:
        self.offset = Point2d(0, 0)
        self._dropped = None
        self.tree.meta_state.set_drag_offset(self.node_id, self.offset)

    def settle(self) -> None:
        self.tree.render_manager.render_drag_end(
            mouse_pos=None,
            mousedown_start_pos=self._mouse_start,
            mousedown_start_offset=self.offset,
            on_start=self.tree.on_drag_mouseup_begin,
            node_id=self.node_id,
            drag_end_event=self._dropped,
        )

    def shapes(self) -> list:
        target = Rect(
            self.origin.x + self.offset.x,
            self.origin.y + self.offset.y,
            self.origin.width,
            self.origin.height,
        )
        return [
            Dim(self.origin, self._radius),
            Outline(target, self._radius),
        ]

    def _apply(self, gpos: Point2d) -> None:
        # The drag overlay catches the mouse on every screen, so the
        # blockable canvases stay put. The drop's render moves them.
        offset = gpos - self._mouse_start
        b, o = self._bounds, self.origin
        if b:
            # Stops at the edges. Bigger than its bounds, it pins top left.
            offset = Point2d(
                max(b.x - o.x, min(offset.x, b.x + b.width - o.x - o.width)),
                max(b.y - o.y, min(offset.y, b.y + b.height - o.y - o.height)),
            )
        self.offset = offset
