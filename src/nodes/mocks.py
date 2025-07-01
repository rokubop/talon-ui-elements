from .tree import Tree

class DotDict:
    def __init__(self):
        self.__dict__["_values"] = {}

    def __getattr__(self, name):
        val = self._values.get(name)
        if val is None:
            val = DotDict()
            self._values[name] = val
        return val

    def __setattr__(self, name, value):
        self._values[name] = value

class MockCanvas:
    def __init__(self, *args, **kwargs):
        self.log = []
        self.rect = kwargs.get("rect", None)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.on_draw = None
        self.paint = DotDict()

    def register(self, event_type, callback):
        self.log.append(("register", event_type, callback))
        if event_type == "draw":
            self.on_draw = callback

    def unregister(self, event_type, callback):
        self.log.append(("unregister", event_type, callback))
        if event_type == "draw" and self.on_draw == callback:
            self.on_draw = None

    def freeze(self):
        self.log.append(("freeze",))
        if self.on_draw:
            self.on_draw(self)

    def move(self, x, y):
        self.log.append(("move", x, y))

    def close(self):
        self.log.append(("close",))
        self.on_draw = None
        self.rect = None

    @classmethod
    def from_rect(cls, rect):
        instance = cls(rect=rect)
        instance.log.append(("from_rect", rect))
        return instance

    def __getattr__(self, name):
        # fallback for any method/property not stubbed
        print(f"MockCanvas __getattr__ _called for {name}")
        def method(*args, **kwargs):
            print(f"MockCanvas _called {name} with args: {args}, kwargs: {kwargs}")
            self.log.append((name, args, kwargs))
        return method

class MockSurface:
    def __init__(self, *args, **kwargs):
        self.log = []
        self.rect = kwargs.get("rect", None)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)

    def canvas(*args, **kwargs):
        return MockCanvas(*args, **kwargs)

    def snapshot(self):
        self.log.append(("snapshot",))
        return self

class MockTree(Tree):
    Canvas = MockCanvas
    Surface = MockSurface

    def __init__(self, *args, **kwargs):
        self._called = []
        super().__init__(*args, **kwargs)

    def called(self, method_name):
        return [m for m, _, _ in self._called if m == method_name]

    def called_times(self, method_name):
        return len(self.called(method_name))

    def log_call(method):
        def wrapped(self, *args, **kwargs):
            self._called.append((method.__name__, args, kwargs))
            return method(self, *args, **kwargs)
        return wrapped

    @log_call
    def render(self, *args, **kwargs):
        return super().render(*args, **kwargs)

    @log_call
    def render_base_canvas(self, *args, **kwargs):
        return super().render_base_canvas(*args, **kwargs)

    @log_call
    def render_decorator_canvas(self, *args, **kwargs):
        return super().render_decorator_canvas(*args, **kwargs)

    @log_call
    def draw_blockable_canvases(self, *args, **kwargs):
        return super().draw_blockable_canvases(*args, **kwargs)

    @log_call
    def on_draw_base_canvas(self, *args, **kwargs):
        return super().on_draw_base_canvas(*args, **kwargs)

    @log_call
    def on_draw_decorator_canvas(self, *args, **kwargs):
        return super().on_draw_decorator_canvas(*args, **kwargs)

    @log_call
    def destroy(self):
        self._called.clear()
        return super().destroy()