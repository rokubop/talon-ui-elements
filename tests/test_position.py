from talon import actions, cron
from ..src.entry import render_ui
from ..src.utils import scale_value
from .test_helpers import test_module, it

W, H = 100, 50

def position_test_ui():
    screen, div = actions.user.ui_elements(["screen", "div"])
    return screen()[
        div(id="flow", width=W, height=H, translate=(30, 40)),
        div(id="after_flow", width=W, height=H),
        div(id="bottom_right", anchor="bottom_right", width=W, height=H),
        div(id="center", anchor="center", width=W, height=H, translate=(10, -20)),
        div(id="top", anchor="top", width=W, height=H, translate=("-50%", 0)),
        div(id="self_aligned", position="absolute", justify_self="flex_end",
            align_self="center", width=W, height=H),
        # anchor wins over left, with a warning
        div(id="replaced", anchor="top_left", left=500, width=W, height=H),
    ]

@test_module
class PositionTests:
    def test_anchor_self_align_translate(self, done):
        mock_tree = render_ui(position_test_ui, test_mode=True)
        def check(tree=mock_tree):
            b = tree.root_node.boundary_rect
            rect = lambda id: tree.meta_state.id_to_node[id].box_model.border_rect
            w, h = rect("flow").width, rect("flow").height
            near = lambda a, e: abs(a - e) <= 1

            r = rect("flow")
            it("translate shifts a flow node", expect=True,
               actual=near(r.x, b.x + scale_value(30)) and near(r.y, b.y + scale_value(40)))
            it("translate leaves siblings in place", expect=True,
               actual=near(rect("after_flow").y, b.y + h))

            r = rect("bottom_right")
            it("anchor bottom_right", expect=True,
               actual=near(r.x + r.width, b.x + b.width) and near(r.y + r.height, b.y + b.height))

            r = rect("center")
            it("anchor center plus translate", expect=True,
               actual=near(r.x, b.x + (b.width - w) / 2 + scale_value(10))
               and near(r.y, b.y + (b.height - h) / 2 - scale_value(20)))

            r = rect("top")
            it("translate percent is of own size", expect=True,
               actual=near(r.x, b.x + (b.width - w) / 2 - w / 2) and near(r.y, b.y))

            r = rect("self_aligned")
            it("justify_self and align_self on an absolute node", expect=True,
               actual=near(r.x, b.x + b.width - w) and near(r.y, b.y + (b.height - h) / 2))

            r = rect("replaced")
            it("anchor replaces left", expect=True, actual=near(r.x, b.x))

            tree.destroy()
            done()
        cron.after("50ms", check)
