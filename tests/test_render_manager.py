from ..src.render_manager import RenderManager, RenderCause
from .test_helpers import test_module, it, spy
from talon import actions
from typing import Any

class MockCanvas():
    def __init__(self):
        self.rendered = False

    def freeze(self):
        self.rendered = True

class MockTree():
    def __init__(self):
        self.canvas_decorator = MockCanvas()
        self.called: list[tuple[str, Any]] = []

    def render_base_canvas(self):
        self.called.append(("render_base_canvas", []))

    def render(self, *args):
        self.called.append(("render", args))

@test_module
class RenderManagerTests:
    def test_empty_queue(self):
        render_manager = RenderManager(MockTree())
        it("should start with empty queue", expect=[], actual=list(render_manager.queue))

    def test_stage_change(self):
        tree = MockTree()
        render_manager = RenderManager(tree)
        on_start = spy()
        on_end = spy()
        render_manager.schedule_state_change(on_start, on_end)

        it("should have state change in the queue",
           expect=RenderCause.STATE_CHANGE,
           actual=render_manager.current_render_task.cause,
        )

        actions.sleep("20ms")

        it("should start a state change",
           expect=True,
           actual=on_start.called
        )
        it("should finish a state change",
           expect=True,
           actual=on_end.called
        )