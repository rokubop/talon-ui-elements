"""The one place that knows a drag is happening.

One active session decides what a mouse event means. Was four independent
`is_*_dragging()` checks across on_mousemove, on_mousedown and on_mouseup.
"""

from talon.types import Point2d

from ..constants import KEY_ESCAPE
from ..core.state_manager import state_manager
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
        """The tree is frozen behind an outline, so it is not where the
        cursor says it is."""
        return self.session is not None and self.session.preview

    def is_kind(self, *kinds: str) -> bool:
        return self.session is not None and self.session.kind in kinds

    def start(self, session: DragSession, gpos: Point2d) -> bool:
        """Renders are paused before begin, so setup cannot race a render."""
        if self.session:
            return False

        if session.pause_renders:
            self.tree.render_manager.pause()
        # Current before begin: a draw landing from begin must already see
        # the tree as previewing.
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
        # A raise here lands in the canvas mouse handler and strands the
        # session with renders paused.
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
        """The tree is going, or its canvases are being rebuilt under it.
        Neither path goes through commit or cancel, so undo what begin did."""
        session, self.session = self.session, None
        if session:
            # pause_renders and is_drag_active are global, not per tree. A
            # session dropped here would leave every other tree frozen and
            # hover dead everywhere.
            if session.pause_renders:
                self.tree.render_manager.resume()
            state_manager.set_drag_active(False)
        self.overlay.destroy()

    def prepare(self) -> None:
        """Build the outline canvas before a drag needs it."""
        self.overlay.prepare()

    def raise_to_top(self) -> None:
        self.overlay.raise_to_top()

    def on_key(self, e) -> None:
        """Esc only. The decorator owns every other key, and this canvas is
        sitting on top of it."""
        if e.down and (e.key or "").lower() == KEY_ESCAPE:
            self.cancel()

    def _paint(self) -> None:
        self.overlay.set_shapes(self.session.shapes())

    def _end(self, apply: callable) -> bool:
        session = self.session
        if not session:
            return False

        # Outline first, so no real frame paints under a stale ghost.
        self.session = None
        self.overlay.close()

        try:
            apply(session)
        except Exception as e:
            print(f"ui_elements: {session.kind} drag failed to end: {e}")
            log_trace()
        finally:
            if session.pause_renders:
                self.tree.render_manager.resume()
        try:
            session.settle()
        except Exception as e:
            print(f"ui_elements: {session.kind} drag failed to settle: {e}")
            log_trace()
        return True
