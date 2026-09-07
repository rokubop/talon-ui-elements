"""The one place that knows a drag is happening.

Mouse events reach the tree from four directions and used to be answered by
four independent `is_*_dragging()` checks scattered through on_mousemove,
on_mousedown and on_mouseup. There is one active session now, and it decides.
"""

from talon.types import Point2d

from ..constants import KEY_ESCAPE
from ..utils import log_trace
from .overlay import DragOverlay
from .session import DragSession


class DragController:
    def __init__(self, tree):
        self.tree = tree
        self.session: DragSession = None
        self.overlay = DragOverlay(tree.create_overlay_canvas, self.on_key)

    @property
    def active(self) -> bool:
        return self.session is not None

    @property
    def previewing(self) -> bool:
        """True while the tree is frozen behind an outline. Anything that
        reads layout mid-drag has to know the tree is not where the cursor
        says it is."""
        return self.session is not None and self.session.preview

    def is_kind(self, *kinds: str) -> bool:
        return self.session is not None and self.session.kind in kinds

    def start(self, session: DragSession, gpos: Point2d) -> bool:
        """Renders are already paused when a session's begin runs, so setup
        can paint without a queued render racing it."""
        if self.session:
            return False

        if session.pause_renders:
            self.tree.render_manager.pause()
        # Both current before begin: a session may paint from begin, and the
        # draw that lands has to already see the tree as previewing.
        self.session = session
        if session.preview:
            self.overlay.open()

        try:
            started = session.begin(gpos)
        except Exception as e:
            started = False
            print(f"ui_elements: {session.kind} drag failed to start: {e}")
            log_trace()

        if not started:
            self.session = None
            self.overlay.close()
            if session.pause_renders:
                self.tree.render_manager.resume()
            return False

        if session.preview:
            self._paint()
        return True

    def move(self, gpos: Point2d) -> bool:
        """True when the session consumed the event."""
        if not self.session:
            return False
        # A raise here would land in the canvas mouse handler and leave the
        # session current with renders paused. Consume it and hold the drag.
        try:
            self.session.move(gpos)
            if self.session.preview:
                self._paint()
        except Exception as e:
            print(f"ui_elements: {self.session.kind} drag move failed: {e}")
            log_trace()
        return True

    def commit(self, gpos: Point2d) -> bool:
        return self._end(lambda session: session.commit(gpos))

    def cancel(self) -> bool:
        return self._end(lambda session: session.cancel())

    def destroy(self) -> None:
        self.session = None
        self.overlay.destroy()

    def prepare(self) -> None:
        """Build the outline canvas ahead of a drag, so starting one does not
        pay for it."""
        self.overlay.prepare()

    def raise_to_top(self) -> None:
        self.overlay.raise_to_top()

    def on_key(self, e) -> None:
        """Only Esc, and only while a drag is up. Everything else belongs to
        the decorator, which this canvas is currently sitting on top of."""
        if e.down and (e.key or "").lower() == KEY_ESCAPE:
            self.cancel()

    def _paint(self) -> None:
        self.overlay.set_shapes(self.session.shapes())

    def _end(self, apply: callable) -> bool:
        session = self.session
        if not session:
            return False

        # Drop the outline first, so the tree never paints a real frame with
        # a stale ghost still on top of it.
        self.session = None
        self.overlay.close()

        try:
            apply(session)
        except Exception as e:
            print(f"ui_elements: {session.kind} drag failed to end: {e}")
            log_trace()
        finally:
            # Whatever happened, the queue does not stay paused.
            if session.pause_renders:
                self.tree.render_manager.resume()
        try:
            session.settle()
        except Exception as e:
            print(f"ui_elements: {session.kind} drag failed to settle: {e}")
            log_trace()
        return True
