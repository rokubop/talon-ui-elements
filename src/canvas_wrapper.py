from weakref import WeakMethod
from talon.canvas import Canvas

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