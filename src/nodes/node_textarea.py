from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.paint import Paint
from talon.types import Rect
from .node import Node
from ..box_model import BoxModelV2
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_INPUT_BACKGROUND_COLOR
from ..interfaces import RenderTransforms
from ..properties import NodeTextareaProperties
from ..fonts import get_typeface
from .node_input_text import _binary_search_cursor


def wrap_lines(text, max_width, measure_text):
    """Wrap text into visual lines that fit within max_width.
    Returns list of (line_text, start_index) tuples where start_index
    is the character offset in the original text."""
    raw_lines = text.split("\n")
    wrapped = []
    abs_pos = 0

    for raw_line in raw_lines:
        if not raw_line:
            wrapped.append(("", abs_pos))
            abs_pos += 1  # skip past \n
            continue

        words = raw_line.split(" ")
        buf = []
        buf_start = abs_pos

        for word in words:
            candidate = " ".join(buf + [word])
            width = measure_text(candidate)[1].width

            if buf and width > max_width:
                wrapped.append((" ".join(buf), buf_start))
                buf_start = abs_pos
                buf = [word]
            else:
                buf.append(word)

            abs_pos += len(word) + 1  # +1 for space or upcoming \n

        # Last word over-counted by 1 (no trailing space), but abs_pos
        # already accounts for the \n separator, so it works out.
        if buf:
            wrapped.append((" ".join(buf), buf_start))

    # The last raw_line's \n was over-counted if text doesn't end with \n,
    # but that's fine since abs_pos isn't used after the loop.

    return wrapped


class NodeTextarea(Node):
    def __init__(self, properties: NodeTextareaProperties = None):
        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["textarea"],
            properties=properties
        )
        self.interactive = True
        self.properties.width = self.properties.width or round(self.properties.font_size * 20)
        self.properties.background_color = self.properties.background_color or DEFAULT_INPUT_BACKGROUND_COLOR
        self.properties.color = self.properties.color or "FFFFFF"
        self.properties.value = str(self.properties.value) if self.properties.value else ""
        if self.properties.gap is None:
            self.properties.gap = 4
        self._cached_paint = None
        self._cached_wrap_text = None
        self._cached_wrap_width = None
        self._cached_wrap_result = None

    def _get_paint(self):
        if self._cached_paint is None:
            paint = Paint()
            paint.textsize = self.properties.font_size
            paint.antialias = True
            if self.properties.font_family:
                typeface = get_typeface(self.properties.font_family)
                if typeface:
                    paint.typeface = typeface
            self._cached_paint = paint
        return self._cached_paint

    def _make_paint(self):
        return self._get_paint()

    def _get_wrapped_lines(self, text, max_width, paint):
        """Cached wrap_lines — only recalculates when text or width changes."""
        if text == self._cached_wrap_text and max_width == self._cached_wrap_width:
            return self._cached_wrap_result
        self._cached_wrap_text = text
        self._cached_wrap_width = max_width
        self._cached_wrap_result = wrap_lines(text, max_width, paint.measure_text)
        return self._cached_wrap_result

    def _get_line_height(self, paint):
        return paint.measure_text("X")[1].height + (self.properties.gap or 4)

    def _calc_height_from_rows(self, paint):
        line_h = self._get_line_height(paint)
        padding_top = self.properties.padding.top or 0
        padding_bottom = self.properties.padding.bottom or 0
        return round(line_h * self.properties.rows + padding_top + padding_bottom)

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        if not self.properties.height:
            paint = self._make_paint()
            self.properties.height = self._calc_height_from_rows(paint)

        self.box_model = BoxModelV2(
            self.properties,
            clip_nodes=self.clip_nodes,
            relative_positional_node=self.relative_positional_node
        )
        return self.box_model.intrinsic_margin_size

    def v2_build_render_list(self):
        self.tree.append_to_render_list(
            node=self,
            draw=self.v2_render
        )

    def v2_render_decorator(self, c, transforms: RenderTransforms = None):
        self._render_textarea(c, transforms)

    def v2_render(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self._setup_custom_input()
        self.tree.meta_state.add_decoration_render(self.id)
        self._render_textarea(c, transforms)

    def _setup_custom_input(self):
        from ..platform.custom_input import setup_custom_input
        setup_custom_input(self, multiline=True)

    def _get_cursor_pos_from_click(self, click_x: float, click_y: float) -> int:
        from ..platform.custom_input import custom_input_manager

        state = custom_input_manager.get_state(self.id)
        if not state or not self.box_model:
            return 0

        paint = self._make_paint()
        line_h = self._get_line_height(paint)
        content_width = self.box_model.content_size.width
        top_left = self.box_model.content_children_pos

        text = state.text or ""
        lines = self._get_wrapped_lines(text, content_width, paint)

        relative_y = click_y - top_left.y + state.scroll_offset
        line_idx = max(0, min(int(relative_y / line_h), len(lines) - 1))

        line_text, line_start = lines[line_idx]
        relative_x = click_x - top_left.x

        return line_start + _binary_search_cursor(line_text, relative_x, paint)

    def set_cursor_from_click(self, click_x: float, click_y: float = None, click_count: int = 1):
        from ..platform.custom_input import custom_input_manager

        state = custom_input_manager.get_state(self.id)
        if not state:
            return

        text = state.text or ""

        if click_count == 3:
            state.selection_start = 0
            state.cursor_pos = len(text)
        elif click_count == 2:
            pos = self._get_cursor_pos_from_click(click_x, click_y or 0)
            start = pos
            while start > 0 and text[start - 1] not in (' ', '\n'):
                start -= 1
            end = pos
            while end < len(text) and text[end] not in (' ', '\n'):
                end += 1
            state.selection_start = start
            state.cursor_pos = end
        else:
            pos = self._get_cursor_pos_from_click(click_x, click_y or 0)
            state.cursor_pos = pos
            state.selection_start = pos

        custom_input_manager._reset_blink()
        custom_input_manager._render()

    def update_selection_from_drag(self, click_x: float, click_y: float = None):
        from ..platform.custom_input import custom_input_manager

        state = custom_input_manager.get_state(self.id)
        if not state:
            return

        state.cursor_pos = self._get_cursor_pos_from_click(click_x, click_y or 0)
        custom_input_manager._reset_blink()
        custom_input_manager._render()

    def _cursor_to_line_col(self, cursor_pos, lines):
        for i, (line_text, line_start) in enumerate(lines):
            line_end = line_start + len(line_text)
            if cursor_pos <= line_end:
                return i, cursor_pos - line_start
        if lines:
            last_text, last_start = lines[-1]
            return len(lines) - 1, len(last_text)
        return 0, 0

    def _render_textarea(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        from ..platform.custom_input import custom_input_manager

        if not self.box_model:
            return

        top_left_pos = self.box_model.content_children_pos.copy()
        if transforms and transforms.offset:
            top_left_pos.x += transforms.offset.x
            top_left_pos.y += transforms.offset.y
        content_width = self.box_model.content_size.width
        content_height = self.box_model.content_size.height

        self.v2_render_background(c, transforms)
        self.v2_render_borders(c, transforms)

        state = custom_input_manager.get_state(self.id)
        if not state:
            return

        is_focused = custom_input_manager.is_focused(self.id)

        paint = self._make_paint()
        line_h = self._get_line_height(paint)
        char_height = paint.measure_text("X")[1].height

        text = state.text or ""
        lines = self._get_wrapped_lines(text, content_width, paint) if text else [("", 0)]

        # Find cursor line and update scroll offset
        cursor_line, cursor_col = self._cursor_to_line_col(state.cursor_pos, lines)
        cursor_y_in_content = cursor_line * line_h

        if cursor_y_in_content - state.scroll_offset + line_h > content_height:
            state.scroll_offset = cursor_y_in_content + line_h - content_height
        if cursor_y_in_content - state.scroll_offset < 0:
            state.scroll_offset = cursor_y_in_content
        if state.scroll_offset < 0:
            state.scroll_offset = 0

        total_height = len(lines) * line_h
        max_scroll = max(0, total_height - content_height)
        if state.scroll_offset > max_scroll:
            state.scroll_offset = max_scroll

        # Clip to content area
        clip_rect = Rect(top_left_pos.x, top_left_pos.y, content_width, content_height)
        c.save()
        c.clip_rect(clip_rect)

        # Selection highlight
        if is_focused and state.has_selection:
            sel_start, sel_end = state.selection_range
            sel_paint = Paint()
            sel_paint.color = self.properties.selection_color
            sel_paint.style = sel_paint.Style.FILL

            for i, (line_text, line_start) in enumerate(lines):
                line_end = line_start + len(line_text)
                if sel_end <= line_start or sel_start >= line_end + 1:
                    continue

                local_start = max(0, sel_start - line_start)
                local_end = min(len(line_text), sel_end - line_start)

                x_start = top_left_pos.x + (paint.measure_text(line_text[:local_start])[1].width if local_start > 0 else 0)
                sel_text = line_text[local_start:local_end]
                sel_width = paint.measure_text(sel_text)[1].width if sel_text else 0

                # If selection extends past this line into next, extend to content width
                if sel_end > line_end and local_end == len(line_text):
                    sel_width = content_width - (x_start - top_left_pos.x)

                y_pos = top_left_pos.y + i * line_h - state.scroll_offset
                c.draw_rect(Rect(
                    x_start,
                    y_pos,
                    sel_width,
                    char_height + 4
                ), sel_paint)

        # Draw text or placeholder
        if text:
            paint.style = paint.Style.FILL
            paint.color = self.properties.color
            for i, (line_text, _) in enumerate(lines):
                if line_text:
                    y = top_left_pos.y + i * line_h + char_height - state.scroll_offset
                    c.draw_text(line_text, top_left_pos.x, y, paint)
        elif self.properties.placeholder and not is_focused:
            paint.style = paint.Style.FILL
            paint.color = self.properties.placeholder_color
            c.draw_text(self.properties.placeholder, top_left_pos.x, top_left_pos.y + char_height, paint)

        # Cursor
        if is_focused and state.cursor_visible:
            cursor_text = lines[cursor_line][0][:cursor_col] if lines else ""
            cursor_x = top_left_pos.x + (paint.measure_text(cursor_text)[1].width if cursor_text else 0)
            cursor_y = top_left_pos.y + cursor_line * line_h - state.scroll_offset

            cursor_paint = Paint()
            cursor_paint.color = self.properties.cursor_color or self.properties.color
            cursor_paint.stroke_width = 1.5
            cursor_paint.style = cursor_paint.Style.STROKE

            c.draw_line(cursor_x, cursor_y, cursor_x, cursor_y + char_height + 4, cursor_paint)

        c.restore()
