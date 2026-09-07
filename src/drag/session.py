"""One drag, from mousedown to mouseup.

Two flags decide how a drag behaves for its whole life:

    preview        outline where it will land instead of moving the real
                   thing. Only geometry drags want this.
    pause_renders  hold the tree's render queue for the duration.

A session that previews must also pause, or the tree would re-lay out
underneath its own outline.

Ending a drag is two steps because renders are still paused for the first
one. `commit` mutates state, the controller resumes, then `settle` paints
and fires callbacks.
"""

from talon.types import Point2d


class DragSession:
    kind = "drag"
    preview = False
    pause_renders = False

    def __init__(self, tree):
        self.tree = tree
        self.start_pos: Point2d = None

    def begin(self, gpos: Point2d) -> bool:
        """False to abandon the drag before it starts."""
        self.start_pos = gpos
        return True

    def move(self, gpos: Point2d) -> None:
        pass

    def commit(self, gpos: Point2d) -> None:
        """Mouseup. Apply the result. Renders are still paused."""
        pass

    def cancel(self) -> None:
        """Escape. Leave nothing behind. Renders are still paused."""
        pass

    def settle(self) -> None:
        """Renders are live again. Paint, and call the consumer back."""
        pass

    def shapes(self) -> list:
        """What the overlay draws. Empty unless preview is set."""
        return []
