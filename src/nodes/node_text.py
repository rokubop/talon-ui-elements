import re
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.paint import Paint
from typing import Literal
from .node import Node
from ..box_model import BoxModelV2
from ..core.state_manager import state_manager
from ..interfaces import Size2d, RenderTransforms
from ..properties import NodeTextProperties
from ..fonts import get_typeface
from ..utils import draw_text_simple

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

ElementType = Literal['button', 'text', 'link']

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

        if element_type == "button" or element_type == "link":
            self.on_click = self.properties.on_click or (lambda: None)
            self.is_hovering = False
            self.interactive = True

    @property
    def own_id(self):
        return self.id and not self.properties.for_id

    def v2_measure_and_account_for_multiline(self, paint: Paint):
        # text_cleansed = re.sub(r'\s{2,}', ' ', self.text)
        text_cleansed = re.sub(r"\s", "x", self.text)

        # start/end spaces not counted by c.paint.measure_text, so fill them in
        # if text_cleansed.startswith(" "):
        #     text_cleansed = "x" + text_cleansed[1:]
        # if text_cleansed.endswith(" "):
        #     text_cleansed = text_cleansed[:-1] + "x"
        self.text_width = paint.measure_text(text_cleansed)[1].width
        self.text_line_height = paint.measure_text("X")[1].height
        self.text_body_height = self.text_line_height

        if (self.properties.width or self.properties.max_width) and self.text_width > self.properties.width:
            self.text_multiline = split_lines(text_cleansed, self.box_model.content_size.width, paint.measure_text)
            gap = self.properties.gap or 16
            self.text_body_height = self.text_line_height * len(self.text_multiline) + gap * (len(self.text_multiline) - 1)

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        """
        First step in the layout process. Calculates the intrinsic size.
        Basically naturally how much width/height based on content or
        user defined width/height it takes up.
        """
        # TODO: remove mutation from measure phase
        if self.element_type == "text" and self.own_id:
            self.text = str(state_manager.use_text_mutation(self))

        paint = Paint()
        paint.textsize = self.properties.font_size
        if self.properties.font_family:
            typeface = get_typeface(self.properties.font_family)
            if typeface:
                paint.typeface = typeface

        paint.font.embolden = True if self.properties.font_weight == "bold" else False

        self.v2_measure_and_account_for_multiline(paint)
        self.box_model = BoxModelV2(
            self.properties,
            Size2d(self.text_width, self.text_body_height),
            self.clip_nodes,
            self.relative_positional_node
        )
        return self.box_model.intrinsic_margin_size

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.v2_render
            )

    def v2_render_decorator(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_render_borders(c, transforms)
        self.v2_render_background(c, transforms)

        # This should be in layout phase
        text_top_left = self.box_model.content_children_pos.copy()
        available_width = self.box_model.content_size.width - self.box_model.content_children_size.width

        if self.properties.text_align == "center":
            text_top_left.x += available_width // 2
        elif self.properties.text_align == "right":
            text_top_left.x += available_width

        if transforms and transforms.offset:
            text_top_left.x += transforms.offset.x
            text_top_left.y += transforms.offset.y

        self.cursor_pre_draw_text = (text_top_left.x, text_top_left.y + self.text_line_height)
        color = self.resolve_render_property("color")

        if self.text_multiline:
            gap = self.properties.gap or 16
            for i, line in enumerate(self.text_multiline):
                draw_text_simple(c, line, color, self.properties, text_top_left.x, text_top_left.y + (self.text_line_height * (i + 1)) + (gap * i))
        else:
            draw_text_simple(c, self.text, color, self.properties, text_top_left.x, text_top_left.y + self.text_line_height)

    def v2_render(self, c, transforms: RenderTransforms = None):
        render_now = not self.uses_decoration_render
        if self.own_id and self.element_type == "text":
            render_now = False

        self.v2_render_borders(c, transforms)
        self.v2_render_background(c, transforms)

        # This should be in layout phase
        text_top_left = self.box_model.content_children_pos.copy()
        available_width = self.box_model.content_size.width - self.box_model.content_children_size.width
        if self.properties.text_align == "center":
            text_top_left.x += available_width // 2
        elif self.properties.text_align == "right":
            text_top_left.x += available_width

        self.cursor_pre_draw_text = (text_top_left.x, text_top_left.y + self.text_line_height)

        if render_now:
            if self.text_multiline:
                gap = self.properties.gap or 16
                for i, line in enumerate(self.text_multiline):
                    draw_text_simple(c, line, self.properties.color, self.properties, text_top_left.x, text_top_left.y + (self.text_line_height * (i + 1)) + (gap * i))
            else:
                draw_text_simple(c, self.text, self.properties.color, self.properties, text_top_left.x, text_top_left.y + self.text_line_height)
