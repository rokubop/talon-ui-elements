from dataclasses import dataclass
from talon.experimental.textarea import DarkThemeLabels, TextArea
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect
from ..constants import ELEMENT_ENUM_TYPE, LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION, LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION
from ..box_model import BoxModelLayout
from ..cursor import Cursor
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
        self.interactive = True
        self.options.width = self.options.width or round(self.options.font_size * 15)
        self.options.height = self.options.height or round(self.options.font_size * 2.2)
        self.options.background_color = self.options.background_color or "333333"
        self.color = self.options.color or "FFFFFF"
        self.value = self.options.value or ""
        if self.options.gap is None:
            self.options.gap = 16

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
        # defer show to the tree, because the last to
        # show will be the focused element
        # text_area_input.show()
        self.input = text_area_input

        return self.box_model.margin_rect