from ..src.render_manager import RenderManager
from .test_helpers import test_module, test

class MockCanvas():
    def __init__(self):
        self.rendered = False

    def freeze(self):
        self.rendered = True

class MockTree():
    def __init__(self):
        self.canvas_decorator = MockCanvas()

    def render_base_canvas(self):
        pass

    def render(self, *args):
        pass

@test_module
class RenderManagerTests:
    def test_empty_queue(self):
        rm = RenderManager(MockTree())
        test("starts with empty queue", expect=[], actual=list(rm.queue))

    def run(self):
        self.test_empty_queue()