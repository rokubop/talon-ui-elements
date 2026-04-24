"""
Pynput-based mouse proxy for blocks_mouse canvases.

Workaround for GIL contention in Talon's native blocks_mouse mouse callback
dispatch on Windows. The blocking canvas is kept (for click suppression) but
mouse/scroll callbacks are handled via pynput instead of canvas.register().

pynput callbacks fire on their own thread. We call handlers directly to
minimize latency - the tree's on_mouse/on_scroll are lightweight dispatchers.

pynput is imported lazily (only when a Tree opts in via the
`user.ui_elements_mouse_use_pynput` setting) so it isn't a hard dependency.
"""

from talon.types import Point2d

_warned_missing = False


class _Vec2:
    __slots__ = ("x", "y")
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


class SyntheticMouseEvent:
    __slots__ = ("event", "gpos")
    def __init__(self, event: str, gpos: Point2d):
        self.event = event
        self.gpos = gpos


class SyntheticScrollEvent:
    __slots__ = ("gpos", "degrees", "pixels")
    def __init__(self, gpos: Point2d, dy: float, dx: float):
        self.gpos = gpos
        self.degrees = _Vec2(x=dx, y=dy)
        self.pixels = _Vec2(0, 0)


def try_create_mouse_proxy(on_mouse, on_scroll):
    """Return a MouseProxy if pynput is importable, else warn (once) and return None."""
    global _warned_missing
    try:
        from pynput import mouse as pynput_mouse
    except ImportError:
        if not _warned_missing:
            _warned_missing = True
            print(
                "talon_ui_elements: setting 'user.ui_elements_mouse_use_pynput' is "
                "enabled but the 'pynput' package is not installed in Talon's Python "
                "environment. Install pynput using Talon's bundled pip and restart "
                "Talon. Falling back to the default canvas.register() mouse handling."
            )
        return None
    return MouseProxy(on_mouse, on_scroll, pynput_mouse)


class MouseProxy:
    """Replaces canvas mouse/scroll registration with a pynput listener."""

    def __init__(self, on_mouse, on_scroll, pynput_mouse):
        self._on_mouse = on_mouse
        self._on_scroll = on_scroll
        self._pynput_mouse = pynput_mouse
        self._listener = None
        self._rects = []
        self._active = False
        # Mirror the native blocks_mouse capture semantics: once a mousedown
        # lands inside a rect, keep delivering move/up events globally until
        # the button is released. Without this, dragging a window breaks as
        # soon as the cursor outruns the rect update and mouseup is lost if
        # released outside, leaving the tree stuck in drag state.
        self._pressed = False

    def _in_any_rect(self, x, y):
        for rect in self._rects:
            if (rect.x <= x <= rect.x + rect.width and
                    rect.y <= y <= rect.y + rect.height):
                return True
        return False

    def _handle_move(self, x, y):
        if not self._active:
            return
        if not self._pressed and not self._in_any_rect(x, y):
            return
        self._on_mouse(SyntheticMouseEvent("mousemove", Point2d(x, y)))

    def _handle_click(self, x, y, button, pressed):
        if not self._active:
            return
        if button != self._pynput_mouse.Button.left:
            return
        if pressed:
            if not self._in_any_rect(x, y):
                return
            self._pressed = True
            self._on_mouse(SyntheticMouseEvent("mousedown", Point2d(x, y)))
        else:
            if not self._pressed:
                return
            self._pressed = False
            self._on_mouse(SyntheticMouseEvent("mouseup", Point2d(x, y)))

    def _handle_scroll(self, x, y, dx, dy):
        if not self._active or not self._in_any_rect(x, y):
            return
        self._on_scroll(SyntheticScrollEvent(Point2d(x, y), dy=dy, dx=dx))

    def start(self, rects):
        self._rects = list(rects)
        self._active = True
        if self._listener is None:
            self._listener = self._pynput_mouse.Listener(
                on_move=self._handle_move,
                on_click=self._handle_click,
                on_scroll=self._handle_scroll,
                daemon=True,
            )
            self._listener.start()

    def update_rects(self, rects):
        self._rects = list(rects)

    def stop(self):
        self._active = False
        self._rects = []
        self._pressed = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
