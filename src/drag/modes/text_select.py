"""Dragging across text to select it.

Selection changes no layout, so this stays live too. The tree keeps the
click-count and focus work; the session only carries it to mouseup.
"""

from talon.types import Point2d

from ...constants import ELEMENT_ENUM_TYPE
from ..session import DragSession

_CARET_ELEMENTS = (
    ELEMENT_ENUM_TYPE["textarea"],
    ELEMENT_ENUM_TYPE["text"],
    ELEMENT_ENUM_TYPE["code"],
)


class TextSelectSession(DragSession):
    kind = "text_select"
    preview = False
    pause_renders = False

    def __init__(self, tree, node):
        super().__init__(tree)
        self.node = node

    def move(self, gpos: Point2d) -> None:
        if self.node.element_type in _CARET_ELEMENTS:
            self.node.update_selection_from_drag(gpos.x, click_y=gpos.y)
        else:
            self.node.update_selection_from_drag(gpos.x)

    def commit(self, gpos: Point2d) -> None:
        if hasattr(self.node, "finalize_selection"):
            self.node.finalize_selection()

    def cancel(self) -> None:
        if hasattr(self.node, "clear_selection"):
            self.node.clear_selection()
