from ..src.core.store import store
from ..src.entry import render_ui
from .test_helpers import test_module, it, spy
from talon import actions, cron

def test_ui():
    screen, div, text = actions.user.ui_elements(["screen", "div", "text"])
    return screen()[
        div()[
            text("Hello world!")
        ]
    ]

@test_module
class TreeTests:
    def test_tree_init(self, done):
        mock_tree = render_ui(test_ui, test_mode=True)
        cron.after("50ms", lambda tree=mock_tree: (
            print("tree.called", tree.called),
            it("should populate tree to the store", expect=True, actual=tree in store.trees),
            it("should call render_base_canvas", expect=1, actual=tree.called_times("render_base_canvas")),
            it("should call render_decorator_canvas", expect=1, actual=tree.called_times("render_decorator_canvas")),
            it("should call on_draw_base_canvas", expect=1, actual=tree.called_times("on_draw_base_canvas")),
            it("should call on_draw_decorator_canvas", expect=1, actual=tree.called_times("on_draw_decorator_canvas")),
            it("should call draw_blockable_canvases", expect=1, actual=tree.called_times("draw_blockable_canvases")),
            cron.after("500ms", lambda tree=tree: (
                tree.destroy(),
                it("should not have the tree in the store", expect=False, actual=tree in store.trees),
                done()
            ))
        ))