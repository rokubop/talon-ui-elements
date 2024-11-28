from talon.experimental.textarea import DarkThemeLabels, TextArea
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect
from dataclasses import dataclass
from ..constants import ELEMENT_ENUM_TYPE
from ..core.box_model import BoxModelLayout
from ..core.cursor import Cursor
from ..options import NodeInputTextOptions
from ..state_manager import state_manager
from .node import Node

@dataclass
class ChangeEvent:
    value: str
    id: str = None
    previous_value: str = None

class NodeInputText(Node):
    def __init__(self, options: NodeInputTextOptions = None):
        print(f"input options: {options}")
        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["input_text"],
            options=options
        )
        self.input = None
        self.options.width = self.options.width or round(self.options.font_size * 15)
        self.options.height = self.options.height or round(self.options.font_size * 2.2)
        self.options.background_color = self.options.background_color or "333333"
        self.color = self.options.color or "FFFFFF"
        self.value = self.options.value or ""
        if self.options.gap is None:
            self.options.gap = 16

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
        self.box_model = BoxModelLayout(
            cursor.virtual_x,
            cursor.virtual_y,
            self.options.margin,
            self.options.padding,
            self.options.border,
            self.options.width,
            self.options.height)

        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        c.paint.textsize = self.options.font_size
        self.box_model.accumulate_content_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, self.options.width, self.options.height))
        return self.box_model.margin_rect

    def grow_intrinsic_size(self, c: SkiaCanvas, cursor: Cursor):
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

        self.box_model.position_for_render(cursor, self.options.flex_direction, self.options.align_items, self.options.justify_content)

        self.render_background(c, cursor)

        cursor.move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)

        text_area_input = TextArea()
        text_area_input.theme = DarkThemeLabels(
            title_size=0,
            padding=0, # Keep this 0. Manage our own padding because this adds to the top hidden title as well
            text_size=self.options.font_size,
            title_bg=self.options.background_color,
            line_spacing=-8, # multiline text is too spaced out
            bg=self.options.background_color,
            fg=self.color,
        )
        text_area_input.value = state_manager.use_input_value(self)

        def on_change(new_value):
            prev_value = self.tree.meta_state.inputs.get(self.options.id)
            if new_value != prev_value:
                self.tree.meta_state.set_input_value(self.options.id, new_value)
                if self.options.on_change:
                    self.options.on_change(
                        ChangeEvent(
                            value=new_value,
                            id=self.options.id,
                            previous_value=prev_value
                        )
                    )
        text_area_input.register("label", on_change)
        text_area_input.rect = Rect(cursor.x, cursor.y, self.box_model.content_rect.width, self.box_model.content_rect.height)
        text_area_input.show()
        self.input = text_area_input

        # self.cursor_pre_draw_text = (cursor.x, cursor.y + self.text_line_height)

        # if render_now:
        #     if self.text_multiline:
        #         gap = self.options.gap or 16
        #         for i, line in enumerate(self.text_multiline):
        #             draw_text_simple(c, line, self.options, cursor.x, cursor.y + (self.text_line_height * (i + 1)) + (gap * i))
        #     else:
        #         draw_text_simple(c, self.text, self.options, cursor.x, cursor.y + self.text_line_height)

        return self.box_model.margin_rect

    def show(self):
        raise NotImplementedError(f"text cannot use .show() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")

    def hide(self):
        raise NotImplementedError(f"text cannot use .hide() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")