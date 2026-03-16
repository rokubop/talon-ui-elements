from talon import app, cron
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.paint import Paint
from talon.types import Rect
from .node import Node
from ..box_model import BoxModelV2
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_INPUT_BACKGROUND_COLOR
from ..interfaces import RenderTransforms
from ..properties import NodeInputTextProperties
from ..fonts import get_typeface

from ..text_utils import binary_search_cursor as _binary_search_cursor

class NodeInputText(Node):
    def __init__(self, properties: NodeInputTextProperties = None):
        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["input_text"],
            properties=properties
        )
        self.interactive = True
        self.properties.width = self.properties.width or round(self.properties.font_size * 15)
        if not self.properties.height:
            has_pad = any(
                k in self.properties._explicitly_set
                for k in ('padding', 'padding_top', 'padding_bottom')
            )
            if has_pad:
                text_height = round(self.properties.font_size * 1.4)
                pad = self.properties.padding
                self.properties.height = text_height + pad.top + pad.bottom
            else:
                self.properties.height = round(self.properties.font_size * 2.2)
        self.properties.background_color = self.properties.background_color or DEFAULT_INPUT_BACKGROUND_COLOR
        self.properties.color = self.properties.color or "FFFFFF"
        self.properties.value = str(self.properties.value) if self.properties.value else ""
        if self.properties.gap is None:
            self.properties.gap = 16
        self._cached_paint = None

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

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
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
        self._render_custom_input_text(c, transforms)

    def v2_render(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_render_background(c, transforms)
        self.v2_render_borders(c, transforms)

        self._setup_custom_input()
        self.tree.meta_state.add_decoration_render(self.id)
        self._render_custom_input_text(c, transforms)

    def _setup_custom_input(self):
        from ..platform.custom_input import setup_custom_input
        setup_custom_input(self)

    def _get_cursor_index_from_x(self, click_x: float) -> int:
        """Convert an x-coordinate to a character index in the text."""
        from ..platform.custom_input import custom_input_manager

        state = custom_input_manager.get_state(self.id)
        if not state or not self.box_model:
            return 0

        paint = self._get_paint()
        content_x = self.box_model.content_children_pos.x
        relative_x = click_x - content_x - state.scroll_offset
        text = state.text or ""

        return _binary_search_cursor(text, relative_x, paint)

    def set_cursor_from_click(self, click_x: float, click_count: int = 1):
        """Position cursor at the character closest to click_x."""
        from ..platform.custom_input import custom_input_manager

        state = custom_input_manager.get_state(self.id)
        if not state:
            return

        text = state.text or ""

        if click_count == 3:
            state.selection_start = 0
            state.cursor_pos = len(text)
        elif click_count == 2:
            pos = self._get_cursor_index_from_x(click_x)
            # Select word under cursor
            start = pos
            while start > 0 and text[start - 1] != ' ':
                start -= 1
            end = pos
            while end < len(text) and text[end] != ' ':
                end += 1
            state.selection_start = start
            state.cursor_pos = end
        else:
            pos = self._get_cursor_index_from_x(click_x)
            state.cursor_pos = pos
            state.selection_start = pos

        custom_input_manager._reset_blink()
        custom_input_manager._render()

    def update_selection_from_drag(self, click_x: float):
        """Update cursor position during drag selection."""
        from ..platform.custom_input import custom_input_manager

        state = custom_input_manager.get_state(self.id)
        if not state:
            return

        state.cursor_pos = self._get_cursor_index_from_x(click_x)
        custom_input_manager._reset_blink()
        custom_input_manager._render()

    def _render_custom_input_text(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        """Draw text, cursor, and selection on canvas."""
        from ..platform.custom_input import custom_input_manager

        if not self.box_model:
            return

        top_left_pos = self.box_model.content_children_pos.copy()
        if transforms and transforms.offset:
            top_left_pos.x += transforms.offset.x
            top_left_pos.y += transforms.offset.y
        content_width = self.box_model.content_size.width
        content_height = self.box_model.content_size.height

        # Re-draw background to clear previous text
        self.v2_render_background(c, transforms)
        self.v2_render_borders(c, transforms)

        state = custom_input_manager.get_state(self.id)
        if not state:
            return

        is_focused = custom_input_manager.is_focused(self.id)

        paint = self._get_paint()

        text = state.text or ""
        metrics = paint.measure_text("X")
        char_height = metrics[1].height
        text_y = top_left_pos.y + (content_height + char_height) / 2

        # Update scroll offset to keep cursor in view
        text_before_cursor = text[:state.cursor_pos]
        cursor_x_in_text = paint.measure_text(text_before_cursor)[0] if text_before_cursor else 0
        padding = 2
        if cursor_x_in_text + state.scroll_offset > content_width - padding:
            state.scroll_offset = content_width - padding - cursor_x_in_text
        if cursor_x_in_text + state.scroll_offset < padding:
            state.scroll_offset = padding - cursor_x_in_text
        total_text_width = paint.measure_text(text)[0] if text else 0
        if total_text_width + state.scroll_offset < content_width - padding and state.scroll_offset < 0:
            state.scroll_offset = min(0, content_width - padding - total_text_width)
        if state.scroll_offset > 0:
            state.scroll_offset = 0

        # Clip to content area
        clip_rect = Rect(top_left_pos.x, top_left_pos.y, content_width, content_height)
        c.save()
        c.clip_rect(clip_rect)

        text_x = top_left_pos.x + state.scroll_offset

        # Selection highlight
        if is_focused and state.has_selection:
            sel_start, sel_end = state.selection_range
            text_before_sel = text[:sel_start]
            text_in_sel = text[sel_start:sel_end]

            x_sel_start = text_x + (paint.measure_text(text_before_sel)[0] if text_before_sel else 0)
            sel_width = paint.measure_text(text_in_sel)[0] if text_in_sel else 0

            sel_paint = Paint()
            sel_paint.color = self.properties.selection_color
            sel_paint.style = sel_paint.Style.FILL
            c.draw_rect(Rect(
                x_sel_start,
                top_left_pos.y + (content_height - char_height) / 2 - 2,
                sel_width,
                char_height + 4
            ), sel_paint)

        # Text or placeholder
        if text:
            paint.style = paint.Style.FILL
            paint.color = self.properties.color
            c.draw_text(text, text_x, text_y, paint)
        elif self.properties.placeholder and not is_focused:
            paint.style = paint.Style.FILL
            paint.color = self.properties.placeholder_color
            c.draw_text(self.properties.placeholder, top_left_pos.x, text_y, paint)

        # Cursor
        if is_focused and state.cursor_visible:
            cursor_x = text_x + cursor_x_in_text

            cursor_paint = Paint()
            cursor_paint.color = self.properties.cursor_color or self.properties.color
            cursor_paint.stroke_width = 1.5
            cursor_paint.style = cursor_paint.Style.STROKE

            cursor_top = top_left_pos.y + (content_height - char_height) / 2 - 2
            cursor_bottom = cursor_top + char_height + 4
            c.draw_line(cursor_x, cursor_top, cursor_x, cursor_bottom, cursor_paint)

        c.restore()
