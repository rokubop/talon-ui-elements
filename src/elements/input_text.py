from dataclasses import dataclass
from ..options import UIOptions, UIOptionsDict, UIInputTextOptions, UIInputTextOptionsDict
from ..box_model import BoxModelLayout
from ..cursor import Cursor
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia import RoundRect
from talon.types import Rect
from itertools import cycle

@dataclass
class UIInputTextOptions(UIOptions):
    id: str = None
    font_size: int = 16
    value: str = ""
    on_change: callable = None

    def __init__(self, **kwargs):
        kwargs['padding_left'] = max(
            kwargs.get('padding_left', 0),
            kwargs.get('padding', 0)
        ) + max(8, kwargs.get('border_radius', 0))
        kwargs['padding_right'] = max(
            kwargs.get('padding_right', 0),
            kwargs.get('padding', 0)
        ) + max(8, kwargs.get('border_radius', 0))
        super().__init__(**kwargs)

class UIInputTextOptionsDict(UIOptionsDict):
    id: str
    font_size: int
    value: str
    on_change: callable

class UIInputText:
    def __init__(self, options: UIInputTextOptions = None):
        self.options = options
        self.id = self.options.id
        self.key = None
        self.type = "input_text"
        self.text_height = None
        self.width = self.options.width or round(self.options.font_size * 15)
        self.height = self.options.height or round(self.options.font_size * 2.2)
        self.box_model = None
        self.options.background_color = self.options.background_color or "333333"
        self.color = self.options.color or "FFFFFF"
        self.debug_number = 0
        self.debug_color = "red"
        self.value = self.options.value or ""
        self.debug_colors = iter(cycle(["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]))

        if self.options.gap is None:
            self.options.gap = 16

    def draw_debug_number(self, c: SkiaCanvas, cursor: Cursor, new_color = False):
        if new_color:
            self.debug_color = next(self.debug_colors)

        c.paint.color = self.debug_color
        self.debug_number += 1

        c.draw_text(str(self.debug_number), cursor.x, cursor.y)

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        global unique_key
        self.key = unique_key
        unique_key += 1
        self.box_model = BoxModelLayout(cursor.virtual_x, cursor.virtual_y, self.options.margin, self.options.padding, self.options.border, self.options.width, self.options.height)
        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        c.paint.textsize = self.options.font_size
        self.box_model.accumulate_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, self.width, self.height))
        return self.box_model.margin_rect

    def render(self, c: SkiaCanvas, cursor: Cursor, builder_options: dict[str, any], scroll_region_key: int = None):
        global ids, inputs, debug_current_step, render_step, debug_points, debug_numbers, debug_draw_step_by_step

        if debug_draw_step_by_step:
            render_step += 1
            if debug_current_step and render_step >= debug_current_step:
                return self.box_model.margin_rect

        self.box_model.prepare_render(cursor, self.options.flex_direction, self.options.align_items, self.options.justify_content)

        if self.id:
            ids[self.id] = {
                "box_model": self.box_model,
                "options": self.options,
                "builder_id": builder_options["id"],
                "scroll_region_key": scroll_region_key
            }
        cursor.move_to(self.box_model.padding_rect.x, self.box_model.padding_rect.y)

        if debug_points:
            c.paint.color = "red"
            c.draw_circle(cursor.x, cursor.y, 2)
        if debug_draw_step_by_step:
            render_step += 1
            if debug_current_step and render_step >= debug_current_step:
                return self.box_model.margin_rect
        if debug_numbers:
            self.draw_debug_number(c, cursor)

        if self.options.background_color:
            c.paint.color = self.options.background_color

            if self.options.border_radius:
                options = RoundRect.from_rect(self.box_model.padding_rect, x=self.options.border_radius, y=self.options.border_radius)
                c.draw_rrect(options)
            else:
                c.draw_rect(self.box_model.padding_rect)

        cursor.move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        if self.id:
            ids[self.id]["cursor"] = {
                "x": cursor.x,
                "y": cursor.y + self.height
            }

        text_area = TextArea()
        text_area.theme = DarkThemeLabels(
            title_size=0,
            padding=0, # Keep this 0. Manage our own padding because this adds to the top hidden title as well
            text_size=self.options.font_size,
            title_bg=self.options.background_color,
            line_spacing=-8, # multiline text is too spaced out
            bg=self.options.background_color,
            fg=self.color,
        )
        if self.options.value:
            text_area.value = self.options.value
        if self.options.on_change:
            def on_change(value):
                if value != self.value:
                    self.value = value
                    self.options.on_change(value)
            text_area.register("label", on_change)
        text_area.rect = Rect(cursor.x, cursor.y, self.box_model.content_rect.width, self.box_model.content_rect.height)
        text_area.show()
        inputs[self.id] = text_area

        # if debug_points:
        #     c.paint.color = "red"
        #     c.draw_circle(cursor.x, cursor.y, 2)
        # if debug_draw_step_by_step:
        #     render_step += 1
        #     if debug_current_step and render_step >= debug_current_step:
        #         return self.box_model.margin_rect
        # if debug_numbers:
        #     self.draw_debug_number(c, cursor)

        return self.box_model.margin_rect

    def show(self):
        raise NotImplementedError(f"text cannot use .show() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")

    def hide(self):
        raise NotImplementedError(f"text cannot use .hide() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")
