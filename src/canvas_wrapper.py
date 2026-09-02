import time
from weakref import WeakMethod
from talon import settings
from talon.canvas import Canvas

_interval = 0.0
_next_check = 0.0
_last_move = 0.0


def _read_interval():
    try:
        rate = int(settings.get("user.ui_elements_mouse_rate") or 0)
    except Exception:
        rate = 0
    return 1 / rate if rate > 0 else 0.0


class ThrottledCanvas(Canvas):
    """
    When using a mouse with a high-refresh-rate, it sends too
    many mousemove events, which can starve the canvas draw thread.
    """

    def on_mouse(self, e):
        global _interval, _next_check, _last_move
        if type(e).__name__ == "MouseMoveEvent":
            now = time.perf_counter()
            if now >= _next_check:
                _next_check = now + 1.0
                _interval = _read_interval()
            if _interval:
                if now - _last_move < _interval:
                    return
                _last_move = now
        return super().on_mouse(e)


class CanvasWeakRef:
    """
    A lightweight wrapper for Talon's Canvas that uses weak references
    for event callbacks e.g. 'draw', 'mouse', and 'scroll', ensuring
    proper garbage collection for bound method like self.on_draw (Otherwise
    self is kept alive by the bound method and can't garbage collect).
    """
    def __init__(self, canvas: Canvas):
        self.canvas = canvas
        self.weak_draw = None
        self.weak_mouse = None
        self.weak_scroll = None
        self.weak_key = None

    def register(self, event, callback):
        weak_attr = f"weak_{event}"
        if getattr(self, weak_attr) is not None:
            raise ValueError(f"A callback for '{event}' is already registered.")
        weak_callback = WeakMethod(callback)
        setattr(self, weak_attr, weak_callback)

        def handler(*args, **kwargs):
            cb = weak_callback()
            if cb:
                cb(*args, **kwargs)

        setattr(self, f"_{event}_handler", handler)
        self.canvas.register(event, handler)

    def unregister(self, event, callback):
        weak_attr = f"weak_{event}"
        weak_callback = getattr(self, weak_attr)
        if weak_callback is None:
            return
        handler = getattr(self, f"_{event}_handler", None)
        if handler:
            self.canvas.unregister(event, handler)
        setattr(self, weak_attr, None)
        setattr(self, f"_{event}_handler", None)

    def __getattr__(self, name):
        """passthrough to canvas"""
        return getattr(self.canvas, name)

    def __setattr__(self, name, value):
        """passthrough to canvas except for the following"""
        if name in [
            "canvas",
            "weak_draw",
            "weak_mouse",
            "weak_scroll",
            "weak_key",
            "_draw_handler",
            "_mouse_handler",
            "_scroll_handler",
            "_key_handler"
        ]:
            super().__setattr__(name, value)
        else:
            setattr(self.canvas, name, value)

    def close(self):
        self.canvas.close()
        self.canvas = None