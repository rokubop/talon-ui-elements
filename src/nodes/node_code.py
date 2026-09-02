from talon.skia.paint import Paint
from talon.types import Rect
from .node_text import NodeText
from ..properties import NodeCodeProperties
from ..syntax import (
    tokenize, tokenize_line, resolve_theme, TOKEN_TEXT,
    TOKEN_DIFF_ADD, TOKEN_DIFF_ADD_BG,
    TOKEN_DIFF_REMOVE, TOKEN_DIFF_REMOVE_BG,
    TOKEN_DIFF_HUNK, TOKEN_DIFF_HUNK_BG,
    TOKEN_LINE_NUMBER,
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
        self.line_numbers = bool(properties.line_numbers)
        self.line_number_start = properties.line_number_start or 1
        self.gutter_width = 0
        self.row_line_numbers = []

    def _compute_lines(self, paint):
        super()._compute_lines(paint)
        self._compute_line_numbers()
        self.gutter_width = self._measure_gutter(paint)
        self.text_width += self.gutter_width

    def _compute_line_numbers(self):
        """Row -> line number. None where a row is a wrapped continuation."""
        if not self.line_numbers:
            self.row_line_numbers = []
            return
        rows = self.text_multiline or [(self.text, 0)]
        numbers = []
        n = self.line_number_start
        for _, pos in rows:
            if pos == 0 or self.text[pos - 1:pos] == "\n":
                numbers.append(n)
                n += 1
            else:
                numbers.append(None)
        self.row_line_numbers = numbers

    def _measure_gutter(self, paint):
        if not self.row_line_numbers:
            return 0
        last = max(
            (n for n in self.row_line_numbers if n is not None),
            default=self.line_number_start,
        )
        # monospace, so one char width covers every digit
        return paint.measure_text("0")[0] * (len(str(last)) + 2)

    def _draw_line_number(self, c, paint, row, x, y):
        if row >= len(self.row_line_numbers):
            return
        number = self.row_line_numbers[row]
        if number is None:
            return
        label = str(number)
        paint.color = self.theme.get(TOKEN_LINE_NUMBER, "6A6A6A")
        char_width = paint.measure_text("0")[0]
        # right aligned, one char of air before the code
        c.draw_text(label, x + self.gutter_width - char_width * (len(label) + 1), y, paint)

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
            content_width -= self.gutter_width
            half_gap = gap / 2
            rect_y = y - line_height - half_gap
            rect_height = line_height + half_gap * 2 if not is_last else line_height + half_gap
            c.draw_rect(Rect(x, rect_y, content_width, rect_height), bg_paint)

    def _draw_text_lines(self, c, color, top_left):
        gap = self._get_line_gap()
        default_color = color or self.properties.color or "D4D4D4"
        paint = self._make_code_paint()
        c.paint.antialias = True
        code_x = top_left.x + self.gutter_width

        if self.text_multiline:
            num_lines = len(self.text_multiline)
            for i, (line_text, _) in enumerate(self.text_multiline):
                y = top_left.y + (self.text_line_height + gap) * i + self.text_line_height
                self._draw_line_number(c, paint, i, top_left.x, y)
                if not line_text:
                    continue

                if self.diff:
                    prefix, content, line_type = _parse_diff_prefix(line_text)
                    is_last = i == num_lines - 1
                    self._draw_diff_line_bg(c, line_type, code_x, y, self.text_line_height, gap, is_last)
                    text_color, _ = self._get_diff_colors(line_type)

                    x = code_x
                    if prefix and line_type != "hunk":
                        paint.color = text_color or default_color
                        c.draw_text(prefix, x, y, paint)
                        x += paint.measure_text(prefix)[0]

                    if content:
                        self._draw_tokenized_line(c, paint, content, x, y, default_color)
                    elif line_type == "hunk":
                        paint.color = text_color
                        c.draw_text(prefix, code_x, y, paint)
                else:
                    pre_tokens = (
                        self.tokenized_lines[i]
                        if i < len(self.tokenized_lines) else None
                    )
                    self._draw_tokenized_line(c, paint, line_text, code_x, y, default_color, tokens=pre_tokens)
        else:
            y = top_left.y + self.text_line_height
            self._draw_line_number(c, paint, 0, top_left.x, y)
            if self.diff:
                prefix, content, line_type = _parse_diff_prefix(self.text)
                self._draw_diff_line_bg(c, line_type, code_x, y, self.text_line_height, gap, True)
                text_color, _ = self._get_diff_colors(line_type)
                x = code_x
                if prefix and line_type != "hunk":
                    paint.color = text_color or default_color
                    c.draw_text(prefix, x, y, paint)
                    x += paint.measure_text(prefix)[0]
                if content:
                    self._draw_tokenized_line(c, paint, content, x, y, default_color)
                elif line_type == "hunk":
                    paint.color = text_color
                    c.draw_text(prefix, code_x, y, paint)
            else:
                pre_tokens = (
                    self.tokenized_lines[0]
                    if self.tokenized_lines else None
                )
                self._draw_tokenized_line(c, paint, self.text, code_x, y, default_color, tokens=pre_tokens)

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
