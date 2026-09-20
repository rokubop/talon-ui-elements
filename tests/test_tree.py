from ..src.core.store import store
from ..src.entry import render_ui
from .test_helpers import test_module, it, spy
from ..src.core.state_manager import state_manager
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


def highlight_test_ui():
    screen, div, text = actions.user.ui_elements(["screen", "div", "text"])
    return screen()[
        div(id="key_x", highlight_style={"background_color": "FF0000"})[
            text("x")
        ]
    ]

def inert_highlight_test_ui():
    screen, div = actions.user.ui_elements(["screen", "div"])
    return screen()[
        div(id="paints", border_color="4a5270",
            highlight_style={"border_color": "6db3ff"}, on_click=lambda e: None),
        div(id="inert", border_color="4a5270",
            highlight_style={"border_color": "4a5270"}, on_click=lambda e: None),
    ]

@test_module
class HighlightTests:
    def test_unhighlight_survives_a_render_walk(self, done):
        mock_tree = render_ui(highlight_test_ui, test_mode=True)
        def check(tree=mock_tree):
            state_manager.highlight("key_x")
            it("should highlight by id", expect=True,
                actual="key_x" in tree.meta_state.highlighted)

            # What a base render looks like between clearing its node map and
            # the walk re-registering it. An unhighlight landing here used to
            # resolve to no tree at all and leave the element lit for good.
            tree.meta_state.clear_nodes()
            state_manager.unhighlight("key_x")
            it("should unhighlight mid render walk", expect=False,
                actual="key_x" in tree.meta_state.highlighted)

            tree.destroy()
            done()
        cron.after("50ms", check)

    def test_inert_highlight_style_keeps_the_overlay(self, done):
        mock_tree = render_ui(inert_highlight_test_ui, test_mode=True)
        def check(tree=mock_tree):
            renders = tree.meta_state.decoration_renders
            it("should decoration render a style that paints", expect=True,
                actual="paints" in renders)
            # Declaring a style that matches the resting style used to opt the
            # node out of the overlay and leave it with no highlight at all.
            it("should not decoration render an inert style", expect=False,
                actual="inert" in renders)

            tree.destroy()
            done()
        cron.after("50ms", check)
