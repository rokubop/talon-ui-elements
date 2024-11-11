from dataclasses import dataclass
from ..options import UIOptions, UIOptionsDict
from ..core.box_model import BoxModelLayout
from ..core.cursor import Cursor
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia import RoundRect
from talon.types import Rect
from itertools import cycle
from .node import Node
from ..utils import draw_text_simple
from typing import Literal
from ..node_manager import node_manager

@dataclass
class NodeTextOptions(UIOptions):
    id: str = None
    font_size: int = 16
    font_weight: str = "normal"
    on_click: any = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class NodeTextOptionsDict(UIOptionsDict):
    id: str
    font_size: int
    font_weight: str

ElementType = Literal['button', 'text']

class NodeText(Node):
    def __init__(self, element_type, text: str, options: NodeTextOptions = None):
        super().__init__(
            element_type=element_type,
            options=options
        )
        self.text = str(text)
        self.text_width = None
        self.text_height = None

        if self.options.gap is None:
            self.options.gap = 16

        if element_type == "button":
            self.on_click = self.options.on_click or (lambda: None)
            self.is_hovering = False

    # def init_state(self, root_options: dict[str, any], scroll_region_key: int = None):
    #     global ids, state, buttons
    #     render_now = True
    #     # if self.id:
    #         # ids[self.id] = {
    #         #     "key": self.key,
    #         #     "box_model": self.box_model,
    #         #     "options": self.options,
    #         #     "root_id": root_options["id"],
    #         #     "scroll_region_key": scroll_region_key
    #         # }
    #         # if self.type == "button" and not buttons.get(self.id):
    #         #     buttons[self.id] = {
    #         #         "key": self.key,
    #         #         "root_id": root_options["id"],
    #         #         "is_hovering": False,
    #         #         "on_click": self.options.on_click or (lambda: None),
    #         #         "scroll_region_key": scroll_region_key
    #         #     }
    #         # if not state["text"].get(self.id):
    #         #     state["text"][self.id] = self.text
    #         # render_now = False
    #     return render_now

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        self.box_model = BoxModelLayout(cursor.virtual_x, cursor.virtual_y, self.options.margin, self.options.padding, self.options.border, self.options.width, self.options.height)
        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        c.paint.textsize = self.options.font_size
        c.paint.font.embolden = True if self.options.font_weight == "bold" else False
        self.text_width = c.paint.measure_text(self.text)[1].width
        self.text_height = c.paint.measure_text("E")[1].height
        self.box_model.accumulate_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, self.text_width, self.text_height))
        return self.box_model.margin_rect

    def render_background(self, c: SkiaCanvas, cursor: Cursor):
        cursor.move_to(self.box_model.padding_rect.x, self.box_model.padding_rect.y)
        if self.options.background_color:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.options.background_color

            if self.options.border_radius:
                options = RoundRect.from_rect(self.box_model.padding_rect, x=self.options.border_radius, y=self.options.border_radius)
                c.draw_rrect(options)
            else:
                c.draw_rect(self.box_model.padding_rect)

    def render(self, c: SkiaCanvas, cursor: Cursor, scroll_region_key: int = None):
        global ids

        self.box_model.prepare_render(cursor, self.options.flex_direction, self.options.align_items, self.options.justify_content)
        # render_now = self.init_state(scroll_region_key)
        render_now = True

        self.render_background(c, cursor)

        cursor.move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        if self.id:
            ids[self.id]["cursor"] = {
                "x": cursor.x,
                "y": cursor.y + self.text_height
            }

        if render_now:
            draw_text_simple(c, self.text, self.options, cursor.x, cursor.y + self.text_height)

        return self.box_model.margin_rect

    def show(self):
        raise NotImplementedError(f"text cannot use .show() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")

    def hide(self):
        raise NotImplementedError(f"text cannot use .hide() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")