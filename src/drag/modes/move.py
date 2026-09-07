"""Moving a `draggable` node by its handle.

The node does not move. Its outline does, and the drop puts it there.
"""

from talon.types import Point2d, Rect

from ...core.state_manager import state_manager
from ..session import DragSession
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
        self._blockable_rects = []

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

        state_manager.set_drag_active(True)
        hovered_id = state_manager.get_hovered_id()
        if hovered_id:
            self.tree.meta_state.set_unhighlighted(hovered_id)
        self._apply(gpos)

        # The one render of the whole drag. It repaints the tree in place,
        # drops the hover highlight the grab left behind, and raises the
        # canvases Talon sinks when a drag starts on them.
        self.tree.render_manager.render_drag_start(
            mouse_pos=gpos,
            mousedown_start_pos=self._mouse_start,
            mousedown_start_offset=self.offset,
        )
        return True

    def move(self, gpos: Point2d) -> None:
        self._apply(gpos)

    def commit(self, gpos: Point2d) -> None:
        self._apply(gpos)

    def cancel(self) -> None:
        self.offset = Point2d(0, 0)
        self.tree.meta_state.set_drag_offset(self.node_id, self.offset)
        self.tree.move_blockable_canvas_rects(self._blockable_rects, self.offset)

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
        self.tree.meta_state.set_drag_offset(self.node_id, self.offset)
        # The blockable canvases are where mouse events come from. They have
        # to follow the outline or the drag dies the moment the cursor leaves
        # where the window used to be.
        self.tree.move_blockable_canvas_rects(self._blockable_rects, self.offset)
