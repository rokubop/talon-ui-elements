"""One drag, from mousedown to mouseup.

`preview` outlines where it lands instead of moving the real thing.
`pause_renders` holds the tree's render queue for the duration. A session that
previews must also pause, or the tree re-lays out under its own outline.
A paused session takes the mouse through the drag overlay, so its mouseup
always arrives and renders always resume.
`refocuses` means settle hands keyboard focus back to the tree itself.

Ending is two steps: `commit` mutates state while renders are still paused,
the controller resumes, `settle` paints and fires callbacks.
"""

from talon.types import Point2d, Rect


def drag_bounds(tree, node) -> Rect:
    """Where a node's `drag_bounds` keeps a move or resize: the tree's root
    for "root", an `(x, y, width, height)` or Rect in screen pixels, or None
    for anywhere."""
    bounds = getattr(node.properties, "drag_bounds", None)
    if bounds == "root":
        return getattr(getattr(tree, "root_node", None), "boundary_rect", None)
    if isinstance(bounds, (tuple, list)):
        return Rect(*bounds)
    return bounds if isinstance(bounds, Rect) else None


class DragSession:
    kind = "drag"
    preview = False
    pause_renders = False
    refocuses = False

    def __init__(self, tree):
        self.tree = tree
        self.start_pos: Point2d = None

    def begin(self, gpos: Point2d) -> bool:
        """False abandons the drag before it starts."""
        self.start_pos = gpos
        return True

    def move(self, gpos: Point2d) -> None:
        pass

    def commit(self, gpos: Point2d) -> None:
        """Mouseup. Renders are still paused."""
        pass

    def cancel(self) -> None:
        """Esc. Renders are still paused."""
        pass

    def settle(self) -> None:
        """Renders are live again."""
        pass

    def shapes(self) -> list:
        """Empty unless preview is set."""
        return []
