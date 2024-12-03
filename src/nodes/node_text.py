from typing import Literal
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect
from ..box_model import BoxModelLayout
from ..cursor import Cursor
from ..properties import NodeTextProperties
from ..state_manager import state_manager
from ..utils import draw_text_simple
from .node import Node
import re

def split_lines(text, max_width, measure_text):
    lines = []
    line = []
    line_width = 0
    for word in text.split(" "):
        word_width = measure_text(word)[1].width
        if line_width + word_width > max_width:
            lines.append(" ".join(line))
            line = [word]
            line_width = word_width
        else:
            line.append(word)
            line_width += word_width
    lines.append(" ".join(line))
    return lines

class TextBlock():
    def __init__(self, value):
        self.value = str(value)
        self.value_cleansed = re.sub(r'\s{2,}', ' ', self.value)
        self.value_multi_line = []
        self.min_width = 0
        self.max_width = 0
        self.line_height = 0
        self.body_height = 0

    def measure_min_width(self, c):
        for word in self.value.split(" "):
            width = c.paint.measure_text(word)[1].width
            if width > self.min_width:
                self.min_width = width

    def measure_max_width(self, c):
        c.paint.measure_text(self.value)[1].width if self.value else 0

    def measure_line_height(self, c):
        c.paint.measure_text("X")[1].height if self.value else 0

    def measure_body_height(self, c):
        c.paint.measure_text("X")[1].height if self.value else 0

    def update_value_simple(self, value):
        self.value = str(value)
        self.value_cleansed = re.sub(r'\s{2,}', ' ', self.value)

    # def measure_and_account_for_multiline(self, c: SkiaCanvas, cursor: Cursor):
    #     text_cleansed = re.sub(r'\s{2,}', ' ', self.text)

    #     # start/end spaces not counted by c.paint.measure_text, so fill them in
    #     if self.text.startswith(" "):
    #         text_cleansed = "x" + text_cleansed
    #     if self.text.endswith(" "):
    #         text_cleansed = "x" + text_cleansed
    #     self.text_width = c.paint.measure_text(text_cleansed)[1].width
    #     self.text_line_height = c.paint.measure_text("X")[1].height
    #     self.text_body_height = self.text_line_height

    #     if (self.properties.width or self.properties.max_width) and self.text_width > self.box_model.content_width:
    #         self.text_multiline = split_lines(text_cleansed, self.box_model.content_width, c.paint.measure_text)
    #         gap = self.properties.gap or 16
    #         self.text_body_height = self.text_line_height * len(self.text_multiline) + gap * (len(self.text_multiline) - 1)

    def update_value_with_reevaluation(self, c, value):
        self.update_value_simple(value)
        self.measure_min_width(c)
        self.measure_max_width(c)
        self.measure_height(c)
        self.measure_body_height(c)

    def __str__(self):
        return self.value

ElementType = Literal['button', 'text']

class NodeText(Node):
    def __init__(self, element_type, text: str, properties: NodeTextProperties = None):
        super().__init__(
            element_type=element_type,
            properties=properties
        )
        # self.text = TextBlock(text)
        self.text = str(text)
        self.cursor_pre_draw_text = (0, 0)
        self.white_space = "normal"
        self.text_multiline = None
        self.text_width = 0
        self.text_line_height = 0
        self.text_body_height = 0

        if element_type == "button":
            self.on_click = self.properties.on_click or (lambda: None)
            self.is_hovering = False
            self.interactive = True

    def measure_and_account_for_multiline(self, c: SkiaCanvas, cursor: Cursor):
        text_cleansed = re.sub(r'\s{2,}', ' ', self.text)

        # start/end spaces not counted by c.paint.measure_text, so fill them in
        if text_cleansed.startswith(" "):
            text_cleansed = "x" + text_cleansed[1:]
        if text_cleansed.endswith(" "):
            text_cleansed = text_cleansed[:-1] + "x"
        self.text_width = c.paint.measure_text(text_cleansed)[1].width
        self.text_line_height = c.paint.measure_text("X")[1].height
        self.text_body_height = self.text_line_height

        if (self.properties.width or self.properties.max_width) and self.text_width > self.box_model.content_width:
            self.text_multiline = split_lines(text_cleansed, self.box_model.content_width, c.paint.measure_text)
            gap = self.properties.gap or 16
            self.text_body_height = self.text_line_height * len(self.text_multiline) + gap * (len(self.text_multiline) - 1)

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        self.box_model = BoxModelLayout(
            cursor.virtual_x,
            cursor.virtual_y,
            self.properties.margin,
            self.properties.padding,
            self.properties.border,
            self.properties.width,
            self.properties.height)

        if self.element_type == "text" and self.id:
            self.text = str(state_manager.use_text_mutation(self))

        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        c.paint.textsize = self.properties.font_size
        c.paint.font.embolden = True if self.properties.font_weight == "bold" else False

        self.measure_and_account_for_multiline(c, cursor)
        self.box_model.accumulate_content_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, self.text_width, self.text_body_height))
        return self.box_model.margin_rect

    def grow_intrinsic_size(self, c: SkiaCanvas, cursor: Cursor):
        return self.box_model.margin_rect

    def render_background(self, c: SkiaCanvas, cursor: Cursor):
        cursor.move_to(self.box_model.padding_rect.x, self.box_model.padding_rect.y)
        if self.properties.background_color:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.background_color

            if self.properties.border_radius:
                properties = RoundRect.from_rect(self.box_model.padding_rect, x=self.properties.border_radius, y=self.properties.border_radius)
                c.draw_rrect(properties)
            else:
                c.draw_rect(self.box_model.padding_rect)

    def render(self, c: SkiaCanvas, cursor: Cursor, scroll_region_key: int = None):
        global ids

        self.box_model.position_for_render(cursor, self.properties.flex_direction, self.properties.align_items, self.properties.justify_content)

        render_now = False if self.id and self.element_type == "text" else True

        self.render_background(c, cursor)

        cursor.move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)

        self.cursor_pre_draw_text = (cursor.x, cursor.y + self.text_line_height)

        if render_now:
            if self.text_multiline:
                gap = self.properties.gap or 16
                for i, line in enumerate(self.text_multiline):
                    draw_text_simple(c, line, self.properties, cursor.x, cursor.y + (self.text_line_height * (i + 1)) + (gap * i))
            else:
                draw_text_simple(c, self.text, self.properties, cursor.x, cursor.y + self.text_line_height)

        return self.box_model.margin_rect