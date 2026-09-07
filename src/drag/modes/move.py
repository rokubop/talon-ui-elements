"""Moving a `draggable` node by its handle.

The node does not move. Its outline does, and the drop puts it there.
"""

from talon.types import Point2d, Rect

from ...constants import DRAG_CAPTURE_MARGIN
from ...core.state_manager import state_manager
from ...utils import scale_value
from ..session import DragSession
from ..shapes import Dim, Outline


def _bounds(rects) -> Rect:
    """One rect around all of them. Inputs carve holes out of the capture
    area, so there can be several, and they move as a group."""
    if not rects:
        return None
    left = min(r.x for r in rects)
    top = min(r.y for r in rects)
    right = max(r.x + r.width for r in rects)
    bottom = max(r.y + r.height for r in rects)
    return Rect(left, top, right - left, bottom - top)


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
        self._blockable_rects = []
        self._capture_bounds: Rect = None
        self._capture_offset = Point2d(0, 0)

    def begin(self, gpos: Point2d) -> bool:
        box_model = getattr(self.node, "box_model", None)
        if not box_model or not box_model.border_rect:
            return False

        self.start_pos = gpos
        self._mouse_start = state_manager.get_mousedown_start_pos() or gpos
        # Where the last committed layout put it. The base canvas is not
        # repainted for the rest of the drag, so this stays true.
        self.origin = box_model.border_rect.copy()
        self._radius = self.node.properties.get_border_radius()
        self._blockable_rects = self.tree.calculate_blockable_rects()
        self._capture_bounds = _bounds(self._blockable_rects)

        state_manager.set_drag_active(True)
        self._apply(gpos)
        # Nothing is raised here. focused=True is an OS raise, and doing it to
        # the base canvas flickers the UI you are about to drag. The old
        # reason for it was that Talon sank the base canvas when it became the
        # drag source, which it no longer is - it does not move, and the
        # outline is a canvas of its own that opens on top.
        return True

    def move(self, gpos: Point2d) -> None:
        self._apply(gpos)

    def commit(self, gpos: Point2d) -> None:
        self._apply(gpos)
        # Only now does the tree get told. Layout adds this offset to a
        # draggable node's position (Node.v2_drag_offset), so publishing it
        # mid-drag means any repaint we did not ask for - a canvas opening
        # over us, a focus change - moves the real window under the outline.
        self.tree.meta_state.set_drag_offset(self.node_id, self.offset)
        # The capture rects only tracked the cursor loosely. Land them on
        # the drop.
        self._move_capture(self.offset)

    def cancel(self) -> None:
        self.offset = Point2d(0, 0)
        self.tree.meta_state.set_drag_offset(self.node_id, self.offset)
        self._move_capture(self.offset)

    def settle(self) -> None:
        self.tree.render_manager.render_drag_end(
            mouse_pos=None,
            mousedown_start_pos=self._mouse_start,
            mousedown_start_offset=self.offset,
            on_start=self.tree.on_drag_mouseup_begin,
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
        self.offset = gpos - self._mouse_start
        self._keep_capture_under(gpos)

    def _keep_capture_under(self, gpos: Point2d) -> None:
        """The blockable canvases are where mouse events come from, so the
        cursor has to stay inside them or the drag dies mid-air.

        Each one is a native window move, and doing that per mouse report is
        what made moving a window cost more than resizing one, which never
        touches them. Where they sit during a drag does not matter, only that
        events keep arriving, so they are re-centred on the cursor when it
        nears an edge. That buys half the window before the next move.
        """
        bounds = self._capture_bounds
        if not bounds:
            return

        margin = scale_value(DRAG_CAPTURE_MARGIN)
        x = bounds.x + self._capture_offset.x
        y = bounds.y + self._capture_offset.y
        if (x + margin <= gpos.x <= x + bounds.width - margin
                and y + margin <= gpos.y <= y + bounds.height - margin):
            return

        self._move_capture(Point2d(
            gpos.x - bounds.width / 2 - bounds.x,
            gpos.y - bounds.height / 2 - bounds.y,
        ))

    def _move_capture(self, offset: Point2d) -> None:
        self._capture_offset = offset
        self.tree.move_blockable_canvas_rects(self._blockable_rects, offset)
