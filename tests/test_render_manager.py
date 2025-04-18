from ..src.render_manager import RenderManager
from .test_helpers import test_module, test

class MockTree():
    def __init__(self):
        pass

mock_tree = MockTree()

@test_module
def render_manager_tests():
    rm = RenderManager(mock_tree)
    test("starts with empty queue", expect=[], actual=rm.queue)