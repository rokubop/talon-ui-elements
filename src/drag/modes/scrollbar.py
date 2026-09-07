"""Dragging a scrollbar thumb.

Scrolling changes no layout, so this stays live: no outline, content follows
the thumb. Still a session, so one thing owns "a drag is happening".
"""

from talon.types import Point2d

from ..session import DragSession


class ScrollbarSession(DragSession):
    kind = "scrollbar"
    preview = False
    pause_renders = True

    def __init__(self, tree, node, axis: str, start_offset: float):
        super().__init__(tree)
        self.node = node
        self.node_id = node.id
        self.axis = axis
        self.start_offset = start_offset
        self._mouse_start = 0.0

    def begin(self, gpos: Point2d) -> bool:
        scrollable = self.tree.meta_state.scrollable.get(self.node_id)
        if not scrollable or not self.node.box_model:
            return False

        self.start_pos = gpos
        self._mouse_start = gpos.x if self.axis == "x" else gpos.y
        self.tree.meta_state.start_scrollbar_drag(
            self.node_id, self._mouse_start, self.start_offset, axis=self.axis
        )
        self.tree._scrollbar_show(self.node_id)
        self.tree.render_base_canvas()
        return True

    def move(self, gpos: Point2d) -> None:
        node = self.node
        scrollable = self.tree.meta_state.scrollable.get(self.node_id)
        if not (scrollable and node.box_model):
            return

        if self.axis == "x":
            thumb = node.box_model.scroll_bar_x_thumb_rect
            if not thumb:
                return
            mouse_delta = gpos.x - self._mouse_start
            view = scrollable.view_width
            content = scrollable.max_width
            thumb_travel = node.box_model.padding_size.width - thumb.width
        else:
            thumb = node.box_model.scroll_bar_thumb_rect
            if not thumb:
                return
            mouse_delta = gpos.y - self._mouse_start
            view = scrollable.view_height
            content = scrollable.max_height
            thumb_travel = node.box_model.padding_size.height - thumb.height

        content_travel = content - view
        if thumb_travel <= 0 or content_travel <= 0:
            return

        offset = self.start_offset - (mouse_delta / thumb_travel) * content_travel
        offset = max(view - content, min(0, offset))

        if self.axis == "x":
            scrollable.offset_x = offset
            scrollable.target_offset_x = offset
        else:
            scrollable.offset_y = offset
            scrollable.target_offset_y = offset
        self.tree.render_manager.render_scrollbar_dragging()

    def commit(self, gpos: Point2d) -> None:
        self.tree.meta_state.clear_scrollbar_drag()

    def cancel(self) -> None:
        self.commit(None)

    def settle(self) -> None:
        self.tree.render_base_canvas()
        self.tree._scrollbar_schedule_idle_hide(self.node_id)
