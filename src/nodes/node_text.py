from talon import clip
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.paint import Paint
from talon.types import Rect
from typing import Literal
from .node import Node
from ..box_model import BoxModelV2
from ..core.state_manager import state_manager
from ..interfaces import Size2d, RenderTransforms
from ..constants import DEFAULT_COLOR
from ..properties import NodeTextProperties
from ..fonts import (
    apply_text_rendering,
    resolve_font,
    line_height_cache,
    text_width_cache,
    TEXT_WIDTH_CACHE_MAX,
)
from ..text_utils import binary_search_cursor, wrap_lines
from ..utils import draw_text_simple

ElementType = Literal['button', 'text', 'link']

class NodeText(Node):
    def __init__(self, element_type, text: str, properties: NodeTextProperties = None):
        super().__init__(
            element_type=element_type,
            properties=properties
        )
        self.text = str(text)
        self.cursor_pre_draw_text = (0, 0)
        self.text_multiline = None
        self.text_width = 0
        self.text_line_height = 0
        self.text_body_height = 0
        self._sel_start = None
        self._sel_end = None
        self._selecting = False

        if element_type == "button" or element_type == "link":
            self.on_click = self.properties.on_click or (lambda: None)
            self.is_hovering = False
            self.disabled = self.properties.disabled or False
            self.interactive = not self.disabled
            self.focusable = self.interactive

    @property
    def own_id(self):
        return self.id and not self.properties.for_id

    @property
    def selectable(self):
        return getattr(self.properties, 'selectable', False)

    def _font_cache_key(self):
        return (
            self.properties.font_size,
            self.properties.font_family,
            self.properties.font_weight,
            self.properties.font_style,
        )

    def _make_paint(self):
        paint = Paint()
        paint.textsize = self.properties.font_size
        # c.draw_text uses the paint passed to it, not c.paint, so the
        # canvas-level antialias flag never reaches text.
        apply_text_rendering(paint)
        font = resolve_font(
            self.properties.font_family,
            self.properties.font_weight,
            self.properties.font_style,
        )
        if font.typeface:
            paint.typeface = font.typeface
        # embolden and skew_x are synthesized and look visibly weaker than a
        # real face -- only apply them for what the loaded face doesn't have.
        paint.font.embolden = font.synthetic_bold
        if font.synthetic_italic:
            paint.font.skew_x = -0.25
        return paint

    def _measure_line_height(self, paint):
        """Measure line height without embolden for consistent sizing."""
        key = self._font_cache_key()
        cached = line_height_cache.get(key)
        if cached is not None:
            return cached
        was_bold = paint.font.embolden
        paint.font.embolden = False
        try:
            line_height = paint.measure_text("X")[1].height
        finally:
            paint.font.embolden = was_bold
        line_height_cache[key] = line_height
        return line_height

    def _get_line_gap(self):
        if self.properties.gap is not None:
            return self.properties.gap
        return round(self.text_line_height * 1.0)

    def _wrap_inset(self):
        """Content-box width that text can't wrap into. NodeCode reserves its
        line-number gutter here."""
        return 0

    def _compute_lines(self, paint):
        """Compute multiline layout. Sets text_multiline, text_width, text_body_height."""
        text = self.text
        gap = self._get_line_gap()
        has_newlines = "\n" in text
        container_width = self.properties.width or self.properties.max_width
        if isinstance(container_width, (int, float)):
            container_width -= self._wrap_inset()

        if has_newlines and container_width and isinstance(container_width, (int, float)):
            self.text_multiline = wrap_lines(text, container_width, paint.measure_text)
        elif has_newlines:
            raw_lines = text.split("\n")
            lines = []
            pos = 0
            for line in raw_lines:
                lines.append((line, pos))
                pos += len(line) + 1
            self.text_multiline = lines
        elif container_width and isinstance(container_width, (int, float)):
            single_width = paint.measure_text(text)[0] if text else 0
            if single_width > container_width:
                self.text_multiline = wrap_lines(text, container_width, paint.measure_text)
            else:
                self.text_multiline = None
        else:
            self.text_multiline = None

        if self.text_multiline:
            widths = [paint.measure_text(line or " ")[0] for line, _ in self.text_multiline]
            self.text_width = max(widths) if widths else 0
            num_lines = len(self.text_multiline)
            self.text_body_height = self.text_line_height * num_lines + gap * max(0, num_lines - 1)
        else:
            # Single line - append sentinel to accurately measure leading/trailing spaces
            if text:
                key = (self._font_cache_key(), text)
                cached = text_width_cache.get(key)
                if cached is None:
                    width_with_sentinel = paint.measure_text(text + "|")[0]
                    sentinel_width = paint.measure_text("|")[0]
                    cached = width_with_sentinel - sentinel_width
                    if len(text_width_cache) >= TEXT_WIDTH_CACHE_MAX:
                        text_width_cache.clear()
                    text_width_cache[key] = cached
                self.text_width = cached
            else:
                self.text_width = 0
            self.text_body_height = self.text_line_height

    def v2_constrain_size(self, available_size=None):
        self.box_model.constrain_size(available_size, self.properties.overflow)

        # Skip re-wrap if text already has explicit width or white_space is nowrap
        if self.properties.width or self.properties.max_width:
            return
        if self.properties.white_space == "nowrap":
            return

        inset = self._wrap_inset()
        constrained_width = self.box_model.content_size.width
        if constrained_width and constrained_width < self.text_width:
            paint = self._make_paint()
            old_height = self.text_body_height
            gap = self._get_line_gap()

            self.text_multiline = wrap_lines(self.text, constrained_width - inset, paint.measure_text)

            if self.text_multiline:
                widths = [paint.measure_text(line or " ")[0] for line, _ in self.text_multiline]
                self.text_width = (max(widths) if widths else 0) + inset
                num_lines = len(self.text_multiline)
                self.text_body_height = self.text_line_height * num_lines + gap * max(0, num_lines - 1)

            height_delta = self.text_body_height - old_height
            if height_delta > 0:
                self.box_model.content_children_size.height += height_delta
                self.box_model.content_size.height += height_delta
                self.box_model.padding_size.height += height_delta
                self.box_model.border_size.height += height_delta
                self.box_model.margin_size.height += height_delta

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        if self.element_type == "text" and self.own_id and not self.selectable:
            self.text = str(state_manager.use_text_mutation(self))

        paint = self._make_paint()
        self.text_line_height = self._measure_line_height(paint)
        self._compute_lines(paint)

        self.box_model = BoxModelV2(
            self.properties,
            Size2d(self.text_width, self.text_body_height),
            self.clip_nodes,
            self.relative_positional_node
        )
        return self.box_model.intrinsic_margin_size

    def _get_text_top_left(self, transforms=None):
        if transforms and transforms.offset:
            top_left = self.box_model.content_children_pos.copy()
            top_left.x += transforms.offset.x
            top_left.y += transforms.offset.y
        else:
            top_left = self.box_model.content_children_pos

        available_width = self.box_model.content_size.width - self.box_model.content_children_size.width
        if self.properties.text_align == "center":
            top_left.x += available_width // 2
        elif self.properties.text_align == "right":
            top_left.x += available_width

        return top_left

    def _render_selection(self, c, paint, top_left):
        if self._sel_start is None or self._sel_end is None:
            return
        sel_start = min(self._sel_start, self._sel_end)
        sel_end = max(self._sel_start, self._sel_end)
        if sel_start == sel_end:
            return

        sel_paint = Paint()
        sel_paint.color = getattr(self.properties, 'selection_color', '4488FF88')
        sel_paint.style = sel_paint.Style.FILL
        gap = self._get_line_gap()

        if self.text_multiline:
            for i, (line_text, line_start) in enumerate(self.text_multiline):
                line_end = line_start + len(line_text)
                if sel_end <= line_start or sel_start >= line_end + 1:
                    continue

                local_start = max(0, sel_start - line_start)
                local_end = min(len(line_text), sel_end - line_start)

                x_start = top_left.x + (paint.measure_text(line_text[:local_start])[0] if local_start > 0 else 0)
                sel_text = line_text[local_start:local_end]
                sel_width = paint.measure_text(sel_text)[0] if sel_text else 0

                if sel_end > line_end and local_end == len(line_text):
                    content_width = self.box_model.content_size.width
                    sel_width = content_width - (x_start - top_left.x)

                y_pos = top_left.y + i * (self.text_line_height + gap)
                is_last_selected = (i == len(self.text_multiline) - 1) or sel_end <= line_end + 1
                sel_height = self.text_line_height + 4 if is_last_selected else self.text_line_height + gap
                c.draw_rect(Rect(x_start, y_pos, sel_width, sel_height), sel_paint)
        else:
            local_start = max(0, sel_start)
            local_end = min(len(self.text), sel_end)
            x_start = top_left.x + (paint.measure_text(self.text[:local_start])[0] if local_start > 0 else 0)
            sel_text = self.text[local_start:local_end]
            sel_width = paint.measure_text(sel_text)[0] if sel_text else 0
            c.draw_rect(Rect(x_start, top_left.y, sel_width, self.text_line_height + 4), sel_paint)

    def _draw_text_lines(self, c, color, top_left):
        gap = self._get_line_gap()
        if self.text_multiline:
            for i, (line_text, _) in enumerate(self.text_multiline):
                if line_text:
                    y = top_left.y + (self.text_line_height + gap) * i + self.text_line_height
                    draw_text_simple(c, line_text, color, self.properties, top_left.x, y)
        else:
            draw_text_simple(c, self.text, color, self.properties, top_left.x, top_left.y + self.text_line_height)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.v2_render
            )

    def v2_render_decorator(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_render_borders(c, transforms)
        self.v2_render_background(c, transforms)
        top_left = self._get_text_top_left(transforms)
        self.cursor_pre_draw_text = (top_left.x, top_left.y + self.text_line_height)
        color = self.resolve_render_property("color") or self.properties.color or DEFAULT_COLOR

        if self._sel_start is not None and self._sel_end is not None:
            paint = self._make_paint()
            self._render_selection(c, paint, top_left)

        self._draw_text_lines(c, color, top_left)

    def v2_render(self, c, transforms: RenderTransforms = None):
        render_now = not self.uses_decoration_render
        if self.own_id and self.element_type == "text" and not self.selectable:
            render_now = False

        self.v2_render_borders(c, transforms)
        self.v2_render_background(c, transforms)
        top_left = self._get_text_top_left(transforms)
        self.cursor_pre_draw_text = (top_left.x, top_left.y + self.text_line_height)

        if render_now:
            if self._sel_start is not None and self._sel_end is not None:
                paint = self._make_paint()
                self._render_selection(c, paint, top_left)
            self._draw_text_lines(c, self.properties.color, top_left)

    # --- Selection methods ---

    def _get_char_index_from_pos(self, click_x, click_y):
        """Convert mouse position to character index in self.text."""
        if not self.box_model:
            return 0

        paint = self._make_paint()
        top_left = self.box_model.content_children_pos
        relative_y = click_y - top_left.y

        if relative_y < 0:
            return 0

        if self.text_multiline:
            gap = self._get_line_gap()
            line_h = self.text_line_height + gap
            total_h = line_h * len(self.text_multiline)
            if relative_y >= total_h:
                return len(self.text)
            line_idx = int(relative_y / line_h)
            line_idx = max(0, min(line_idx, len(self.text_multiline) - 1))
            line_text, line_start = self.text_multiline[line_idx]
            relative_x = click_x - top_left.x
            return line_start + binary_search_cursor(line_text, relative_x, paint)
        else:
            if relative_y >= self.text_line_height:
                return len(self.text)
            relative_x = click_x - top_left.x
            return binary_search_cursor(self.text, relative_x, paint)

    def set_selection_from_click(self, click_x, click_y, click_count=1):
        text = self.text
        if click_count == 3:
            self._sel_start = 0
            self._sel_end = len(text)
        elif click_count == 2:
            pos = self._get_char_index_from_pos(click_x, click_y)
            start = pos
            while start > 0 and text[start - 1] not in (' ', '\n'):
                start -= 1
            end = pos
            while end < len(text) and text[end] not in (' ', '\n'):
                end += 1
            self._sel_start = start
            self._sel_end = end
        else:
            pos = self._get_char_index_from_pos(click_x, click_y)
            self._sel_start = pos
            self._sel_end = pos
        self._selecting = True
        self._trigger_selection_render()

    def update_selection_from_drag(self, click_x, click_y=None):
        if click_y is None:
            click_y = self.box_model.content_children_pos.y if self.box_model else 0
        self._sel_end = self._get_char_index_from_pos(click_x, click_y)
        self._trigger_selection_render()

    def finalize_selection(self):
        self._selecting = False

    def copy_selection(self):
        if self._sel_start is not None and self._sel_end is not None:
            sel_start = min(self._sel_start, self._sel_end)
            sel_end = max(self._sel_start, self._sel_end)
            if sel_start != sel_end:
                try:
                    clip.set_text(self.text[sel_start:sel_end])
                except Exception:
                    pass

    def clear_selection(self):
        if self._sel_start is not None or self._sel_end is not None:
            self._sel_start = None
            self._sel_end = None
            if self.uses_decoration_render and self.tree:
                self.uses_decoration_render = False
                self.tree.meta_state.decoration_renders.pop(self.id, None)
                self.tree.refresh_decorator_canvas()

    def _trigger_selection_render(self):
        if self.tree:
            if not self.uses_decoration_render:
                self.uses_decoration_render = True
                self.tree.meta_state.add_decoration_render(self.id)
            self.tree.refresh_decorator_canvas()
