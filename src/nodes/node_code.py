from talon.skia.paint import Paint
from talon.types import Rect
from .node_text import NodeText
from ..properties import NodeCodeProperties
from ..syntax import (
    tokenize, tokenize_line, resolve_theme, TOKEN_TEXT,
    TOKEN_DIFF_ADD, TOKEN_DIFF_ADD_BG,
    TOKEN_DIFF_REMOVE, TOKEN_DIFF_REMOVE_BG,
    TOKEN_DIFF_HUNK, TOKEN_DIFF_HUNK_BG,
)


def _parse_diff_prefix(line):
    """Return (prefix, content, line_type) for a diff line."""
    if line.startswith("@@"):
        return line, "", "hunk"
    if line.startswith("+"):
        return "+", line[1:], "add"
    if line.startswith("-"):
        return "-", line[1:], "remove"
    if line.startswith(" "):
        return " ", line[1:], "context"
    return "", line, "context"


class NodeCode(NodeText):
    def __init__(self, text: str, properties: NodeCodeProperties = None):
        super().__init__(
            element_type="code",
            text=text,
            properties=properties,
        )
        self.language = properties.language or "python"
        self.theme = resolve_theme(properties.theme)
        self.diff = properties.diff
        # Pre-tokenize the whole text up front so multi-line constructs
        # (triple-quoted strings, eventually multi-line comments) get
        # tokenized with cross-line state. Indexed by line number; used by
        # _draw_text_lines for the non-diff path.
        self.tokenized_lines = (
            tokenize(text, self.language) if text and not self.diff else []
        )

    def _make_code_paint(self):
        paint = self._make_paint()
        paint.style = paint.Style.FILL
        return paint

    def _get_diff_colors(self, line_type):
        """Return (text_color, bg_color) for a diff line type."""
        if line_type == "add":
            return self.theme.get(TOKEN_DIFF_ADD, "A9DC76"), self.theme.get(TOKEN_DIFF_ADD_BG, "2EA04330")
        if line_type == "remove":
            return self.theme.get(TOKEN_DIFF_REMOVE, "FF6188"), self.theme.get(TOKEN_DIFF_REMOVE_BG, "F8514930")
        if line_type == "hunk":
            return self.theme.get(TOKEN_DIFF_HUNK, "78DCE8"), self.theme.get(TOKEN_DIFF_HUNK_BG, "78DCE820")
        return None, None

    def _draw_diff_line_bg(self, c, line_type, x, y, line_height, gap, is_last):
        """Draw background highlight for a diff line."""
        _, bg_color = self._get_diff_colors(line_type)

        if bg_color:
            bg_paint = Paint()
            bg_paint.color = bg_color
            bg_paint.style = bg_paint.Style.FILL
            content_width = self.box_model.content_size.width if self.box_model else 400
            half_gap = gap / 2
            rect_y = y - line_height - half_gap
            rect_height = line_height + half_gap * 2 if not is_last else line_height + half_gap
            c.draw_rect(Rect(x, rect_y, content_width, rect_height), bg_paint)

    def _draw_text_lines(self, c, color, top_left):
        gap = self._get_line_gap()
        default_color = color or self.properties.color or "D4D4D4"
        paint = self._make_code_paint()
        c.paint.antialias = True

        if self.text_multiline:
            num_lines = len(self.text_multiline)
            for i, (line_text, _) in enumerate(self.text_multiline):
                if not line_text:
                    continue
                y = top_left.y + (self.text_line_height + gap) * i + self.text_line_height

                if self.diff:
                    prefix, content, line_type = _parse_diff_prefix(line_text)
                    is_last = i == num_lines - 1
                    self._draw_diff_line_bg(c, line_type, top_left.x, y, self.text_line_height, gap, is_last)
                    text_color, _ = self._get_diff_colors(line_type)

                    x = top_left.x
                    if prefix and line_type != "hunk":
                        paint.color = text_color or default_color
                        c.draw_text(prefix, x, y, paint)
                        x += paint.measure_text(prefix)[0]

                    if content:
                        self._draw_tokenized_line(c, paint, content, x, y, default_color)
                    elif line_type == "hunk":
                        paint.color = text_color
                        c.draw_text(prefix, top_left.x, y, paint)
                else:
                    pre_tokens = (
                        self.tokenized_lines[i]
                        if i < len(self.tokenized_lines) else None
                    )
                    self._draw_tokenized_line(c, paint, line_text, top_left.x, y, default_color, tokens=pre_tokens)
        else:
            y = top_left.y + self.text_line_height
            if self.diff:
                prefix, content, line_type = _parse_diff_prefix(self.text)
                self._draw_diff_line_bg(c, line_type, top_left.x, y, self.text_line_height, gap, True)
                text_color, _ = self._get_diff_colors(line_type)
                x = top_left.x
                if prefix and line_type != "hunk":
                    paint.color = text_color or default_color
                    c.draw_text(prefix, x, y, paint)
                    x += paint.measure_text(prefix)[0]
                if content:
                    self._draw_tokenized_line(c, paint, content, x, y, default_color)
                elif line_type == "hunk":
                    paint.color = text_color
                    c.draw_text(prefix, top_left.x, y, paint)
            else:
                pre_tokens = (
                    self.tokenized_lines[0]
                    if self.tokenized_lines else None
                )
                self._draw_tokenized_line(c, paint, self.text, top_left.x, y, default_color, tokens=pre_tokens)

    def _draw_tokenized_line(self, c, paint, line_text, x, y, default_color, tokens=None):
        """Draw a single line with syntax coloring. `tokens` may be passed
        when the caller has already computed cross-line tokenization (so
        triple-quoted string state carries across lines)."""
        if tokens is None:
            tokens = tokenize_line(line_text, self.language)

        for token_text, token_type in tokens:
            if not token_text:
                continue
            paint.color = self.theme.get(token_type, self.theme.get(TOKEN_TEXT, default_color))
            c.draw_text(token_text, x, y, paint)
            x += paint.measure_text(token_text)[0]
