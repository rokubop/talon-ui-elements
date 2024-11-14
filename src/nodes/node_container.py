from itertools import cycle
from ..options import UIOptions
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia import RoundRect
from talon.types import Rect, Point2d
from itertools import cycle
from .node import Node
from ..core.box_model import BoxModelLayout
from ..core.cursor import Cursor
from ..interfaces import NodeContainerType

class NodeContainer(Node, NodeContainerType):
    def __init__(self, element_type, options: UIOptions = None):
        super().__init__(element_type=element_type, options=options)
        self.scroll_y = 0
        self.scroll_y_percentage = 0
        self.highlight_color = self.options.highlight_color or None
        self.is_uniform_border = True
        self.debug_number = 0
        self.debug_color = "red"
        self.debug_colors = iter(cycle(["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]))

    def set_scroll_y(self, delta: int):
        """Adjust the scroll position based on input (e.g., mouse scroll)."""
        self.scroll_y += delta

        max_top_scroll_y = 0
        max_bottom_scroll_y = self.options.height

        if self.scroll_y < max_top_scroll_y:
            self.scroll_y = max_top_scroll_y
        elif self.scroll_y > max_bottom_scroll_y:
            self.scroll_y = max_bottom_scroll_y

        if self.options.height > 0:
            self.scroll_y_percentage = self.scroll_y / self.options.height
        else:
            self.scroll_y_percentage = 0

    def virtual_render_child(self, c: SkiaCanvas, cursor: Cursor, child: Node, i: int, move_after_last_child = True):
        gap = self.options.gap or 0
        if self.options.gap is None and child.element_type == "text" and self.children_nodes[i - 1].element_type == "text":
            gap = 16
        a_cursor = Point2d(cursor.virtual_x, cursor.virtual_y)
        rect = child.virtual_render(c, cursor)
        cursor.virtual_move_to(a_cursor.x, a_cursor.y)
        if move_after_last_child or i != len(self.children_nodes) - 1:
            if self.options.flex_direction == "column":
                cursor.virtual_move_to(cursor.virtual_x, cursor.virtual_y + rect.height + gap)
            elif self.options.flex_direction == "row":
                cursor.virtual_move_to(cursor.virtual_x + rect.width + gap, cursor.virtual_y)
        self.box_model.accumulate_dimensions(rect)

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        # global unique_key
        # self.key = unique_key
        # unique_key += 1
        self.box_model = BoxModelLayout(cursor.virtual_x, cursor.virtual_y, self.options.margin, self.options.padding, self.options.border, self.options.width, self.options.height)
        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        last_cursor = Point2d(cursor.virtual_x, cursor.virtual_y)

        flex_children = []
        for i, child in enumerate(self.children_nodes):
            if child.options.flex:
                flex_children.append(child)
                continue
            self.virtual_render_child(c, cursor, child, i, move_after_last_child=True)

        if flex_children:
            flex_weights = self.calculate_flex_weights(flex_children)
            remaining_width = self.box_model.content_rect.width - self.box_model.content_children_rect.width
            remaining_height = self.box_model.content_rect.height - self.box_model.content_children_rect.height

            for i, child in enumerate(flex_children):
                if self.options.flex_direction == "row":
                    child.options.width = remaining_width * flex_weights[i]
                elif self.options.flex_direction == "column":
                    child.options.height = remaining_height * flex_weights[i]
                self.virtual_render_child(c, cursor, child, i, move_after_last_child=False)

        cursor.virtual_move_to(last_cursor.x, last_cursor.y)

        # if self.type != "root" and self.box_model.scrollable and self.options.height < self.box_model.padding_rect.height and self.key not in scrollable_regions:
        #     scrollable_regions[self.key] = {
        #         "scroll_box_rect": self.box_model.scroll_box_rect,
        #         "on_scroll_y": self.set_scroll_y,
        #     }

        return self.box_model.margin_rect

    def calculate_flex_weights(self, flex_children):
        total_flex = sum(child.options.flex for child in flex_children)
        return [child.options.flex / total_flex for child in flex_children]

    def draw_debug_number(self, c: SkiaCanvas, cursor: Cursor, new_color = False):
        if new_color:
            self.debug_color = next(self.debug_colors)

        c.paint.color = self.debug_color
        self.debug_number += 1

        c.draw_text(str(self.debug_number), cursor.x, cursor.y)

    def render_borders(self, c: SkiaCanvas, cursor: Cursor):
        cursor.move_to(self.box_model.border_rect.x, self.box_model.border_rect.y)
        self.is_uniform_border = True
        border_spacing = self.box_model.border_spacing
        has_border = border_spacing.left or border_spacing.top or border_spacing.right or border_spacing.bottom
        if has_border:
            self.is_uniform_border = border_spacing.left == border_spacing.top == border_spacing.right == border_spacing.bottom
            inner_rect = self.box_model.scroll_box_rect if self.box_model.scrollable else self.box_model.padding_rect
            if self.is_uniform_border:
                border_width = border_spacing.left
                c.paint.color = self.options.border_color
                c.paint.style = c.paint.Style.STROKE
                c.paint.stroke_width = border_width

                bordered_rect = Rect(
                    inner_rect.x - border_width / 2,
                    inner_rect.y - border_width / 2,
                    inner_rect.width + border_width,
                    inner_rect.height + border_width,
                )

                if self.options.border_radius:
                    c.draw_rrect(RoundRect.from_rect(bordered_rect, x=self.options.border_radius + border_width / 2, y=self.options.border_radius + border_width / 2))
                else:
                    c.draw_rect(bordered_rect)
            else:
                c.paint.color = self.options.border_color
                c.paint.style = c.paint.Style.STROKE
                b_rect, p_rect = self.box_model.border_rect, inner_rect
                if border_spacing.left:
                    c.paint.stroke_width = border_spacing.left
                    half = border_spacing.left / 2
                    c.draw_line(b_rect.x + half, p_rect.y, b_rect.x + half, p_rect.y + p_rect.height)
                if border_spacing.right:
                    c.paint.stroke_width = border_spacing.right
                    half = border_spacing.right / 2
                    c.draw_line(b_rect.x + b_rect.width - half, p_rect.y, b_rect.x + b_rect.width - half, p_rect.y + p_rect.height)
                if border_spacing.top:
                    c.paint.stroke_width = border_spacing.top
                    half = border_spacing.top / 2
                    c.draw_line(p_rect.x, b_rect.y + half, p_rect.x + p_rect.width, b_rect.y + half)
                if border_spacing.bottom:
                    c.paint.stroke_width = border_spacing.bottom
                    half = border_spacing.bottom / 2
                    c.draw_line(p_rect.x, b_rect.y + b_rect.height - half, p_rect.x + p_rect.width, b_rect.y + b_rect.height - half)

    def render_background(self, c: SkiaCanvas, cursor: Cursor):
        c.paint.style = c.paint.Style.FILL

        inner_rect = self.box_model.scroll_box_rect if self.box_model.scrollable else self.box_model.padding_rect

        cursor.move_to(inner_rect.x, inner_rect.y)
        if self.options.background_color:
            c.paint.color = self.options.background_color
            if self.options.border_radius and self.is_uniform_border:
                c.draw_rrect(RoundRect.from_rect(inner_rect, x=self.options.border_radius, y=self.options.border_radius))
            else:
                c.draw_rect(inner_rect)

    def adjust_for_scroll_y_start(self, c: SkiaCanvas):
        self.box_model.adjust_scroll_y(self.scroll_y, self.scroll_y_percentage, c)

    def adjust_for_scroll_y_end(self, c: SkiaCanvas):
        self.box_model.adjust_scroll_y(-self.scroll_y, self.scroll_y_percentage, c)

    def crop_scrollable_region_start(self, c: SkiaCanvas):
        if self.box_model.scrollable and self.box_model.scroll_box_rect:
            c.save()
            c.clip_rect(self.box_model.scroll_box_rect)

    def crop_scrollable_region_end(self, c: SkiaCanvas):
        if self.box_model.scrollable and self.box_model.scroll_box_rect:
            c.restore()

    def debugger_should_continue(self, c: SkiaCanvas, cursor: Cursor):
        pass
        # global debug_enabled, debug_current_step, render_step, debug_points, debug_numbers, debug_draw_step_by_step
        # if not debug_enabled:
        #     return False

        # has_continue = False
        # if debug_draw_step_by_step:
        #         render_step += 1
        #         if debug_current_step and render_step >= debug_current_step:
        #             has_continue = True
        # return has_continue

    def debugger(self, c: SkiaCanvas, cursor: Cursor, incrememnt_step: bool = False, new_color = False, is_breakpoint = True):
        pass
        # """Add circles and numbers and the ability to render step by step. Returns the current view state if it should be rendered."""
        # global debug_enabled, debug_current_step, render_step, debug_numbers, debug_points, debug_draw_step_by_step

        # if not debug_enabled:
        #     return None

        # if incrememnt_step and debug_draw_step_by_step:
        #     render_step += 1
        #     if debug_current_step and render_step >= debug_current_step:
        #         return self.box_model.margin_rect
        # if debug_points:
        #     c.paint.color = "red"
        #     c.draw_circle(cursor.x, cursor.y, 2)
        # if debug_numbers:
        #     self.draw_debug_number(c, cursor, new_color)

        # return None

    def move_cursor_to_align_axis_before_children_render(self, cursor: Cursor):
        cursor.move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        if self.options.flex_direction == "row":
            if self.options.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + self.box_model.content_children_rect.height // 2)
            elif self.options.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + self.box_model.content_children_rect.height)
        else:
            if self.options.align_items == "center":
                cursor.move_to(cursor.x + self.box_model.content_children_rect.width // 2, cursor.y)
            elif self.options.align_items == "flex_end":
                cursor.move_to(cursor.x + self.box_model.content_children_rect.width, cursor.y)

    def move_cursor_to_top_left_child_based_on_align_axis(self, cursor: Cursor, child):
        if self.options.flex_direction == "row":
            if self.options.align_items == "center":
                cursor.move_to(cursor.x, cursor.y - child.box_model.margin_rect.height // 2)
            elif self.options.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y - child.box_model.margin_rect.height)

        elif self.options.flex_direction == "column":
            if self.options.align_items == "center":
                cursor.move_to(cursor.x - child.box_model.margin_rect.width // 2, cursor.y)
            elif self.options.align_items == "flex_end":
                cursor.move_to(cursor.x - child.box_model.margin_rect.width, cursor.y)

    def move_cursor_from_top_left_child_to_next_child_along_align_axis(self, cursor: Cursor, child, rect: Rect, gap = 0):
        if self.options.flex_direction == "row":
            if self.options.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + child.box_model.margin_rect.height // 2)
            elif self.options.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + child.box_model.margin_rect.height)
            cursor.move_to(cursor.x + rect.width + gap, cursor.y)
        else:
            if self.options.align_items == "center":
                cursor.move_to(cursor.x + child.box_model.margin_rect.width // 2, cursor.y)
            elif self.options.align_items == "flex_end":
                cursor.move_to(cursor.x + child.box_model.margin_rect.width, cursor.y)
            cursor.move_to(cursor.x, cursor.y + rect.height + gap)

    def render(self, c: SkiaCanvas, cursor: Cursor, scroll_region_key: int = None):
        global ids

        if view_state := self.debugger(c, cursor, True):
            return view_state

        self.box_model.prepare_render(cursor, self.options.flex_direction, self.options.align_items, self.options.justify_content)

        # if self.id:
        #     ids[self.id] = {
        #         "box_model": self.box_model,
        #         "options": self.options,
        #         "root_id": root_options["id"],
        #         "scroll_region_key": scroll_region_key
        #     }

        # self.debugger(c, cursor)
        self.render_borders(c, cursor)
        self.adjust_for_scroll_y_start(c)
        self.crop_scrollable_region_start(c)
        self.render_background(c, cursor)
        # if view_state := self.debugger(c, cursor, True):
        #     return view_state
        self.move_cursor_to_align_axis_before_children_render(cursor)
        # self.debugger(c, cursor)

        last_cursor = Point2d(cursor.x, cursor.y)
        for i, child in enumerate(self.children_nodes):
            if self.debugger_should_continue(c, cursor):
                continue

            self.move_cursor_to_top_left_child_based_on_align_axis(cursor, child)
            # self.debugger(c, cursor, new_color=True)

            child_last_cursor = Point2d(cursor.x, cursor.y)
            scroll_region = self.key if self.box_model.scrollable else scroll_region_key
            rect = child.render(c, cursor, scroll_region)
            cursor.move_to(child_last_cursor.x, child_last_cursor.y)

            if i == len(self.children_nodes) - 1:
                break

            # if self.debugger_should_continue(c, cursor):
            #     continue

            gap = self.options.gap or 0
            if self.options.gap is None and child.element_type == "text" and self.children_nodes[i + 1].element_type == "text":
                gap = 16

            self.move_cursor_from_top_left_child_to_next_child_along_align_axis(cursor, child, rect, gap)
            # self.debugger(c, cursor)

        # if view_state := self.debugger(c, cursor, True):
        #     return view_state

        cursor.move_to(last_cursor.x, last_cursor.y)
        # self.debugger(c, cursor)

        self.adjust_for_scroll_y_end(c)
        self.crop_scrollable_region_end(c)

        return self.box_model.margin_rect

    def show(self):
        raise NotImplementedError(f"div cannot use .show() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")

    def hide(self):
        raise NotImplementedError(f"div cannot use .hide() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")