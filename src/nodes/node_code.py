from .node_text import NodeText
from ..properties import NodeCodeProperties
from ..syntax import tokenize_line, resolve_theme, TOKEN_TEXT


class NodeCode(NodeText):
    def __init__(self, text: str, properties: NodeCodeProperties = None):
        super().__init__(
            element_type="code",
            text=text,
            properties=properties,
        )
        self.language = properties.language or "python"
        self.theme = resolve_theme(properties.theme)

    def _make_code_paint(self):
        paint = self._make_paint()
        paint.style = paint.Style.FILL
        return paint

    def _draw_text_lines(self, c, color, top_left):
        gap = self._get_line_gap()
        default_color = color or self.properties.color or "D4D4D4"
        paint = self._make_code_paint()
        c.paint.antialias = True

        if self.text_multiline:
            for i, (line_text, _) in enumerate(self.text_multiline):
                if not line_text:
                    continue
                y = top_left.y + (self.text_line_height + gap) * i + self.text_line_height
                self._draw_tokenized_line(c, paint, line_text, top_left.x, y, default_color)
        else:
            y = top_left.y + self.text_line_height
            self._draw_tokenized_line(c, paint, self.text, top_left.x, y, default_color)

    def _draw_tokenized_line(self, c, paint, line_text, x, y, default_color):
        """Draw a single line with syntax coloring."""
        tokens = tokenize_line(line_text, self.language)

        for token_text, token_type in tokens:
            if not token_text:
                continue
            paint.color = self.theme.get(token_type, self.theme.get(TOKEN_TEXT, default_color))
            c.draw_text(token_text, x, y, paint)
            x += paint.measure_text(token_text)[0]
