from itertools import cycle
from itertools import cycle
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from ..core.box_model import BoxModelLayout
from ..core.cursor import Cursor
from ..interfaces import NodeContainerType
from ..options import UIOptions
from .node import Node


class NodeContainer(Node, NodeContainerType):
    def __init__(self, element_type, options: UIOptions = None):
        super().__init__(element_type=element_type, options=options)
        self.scroll_y = 0
        self.scroll_y_percentage = 0
        self.highlight_color = self.options.highlight_color or None
        self.is_uniform_border = True
        self.justify_between_gaps = None
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

    def set_justify_between_gaps(self):
        if self.options.justify_content == "space_between":
            total_children_width = None
            total_children_height = None

            if self.options.flex_direction == "row":
                total_children_width = sum(child.box_model.margin_rect.width for child in self.children_nodes)
                available_space = self.box_model.content_rect.width - total_children_width
            else:
                total_children_height = sum(child.box_model.margin_rect.height for child in self.children_nodes)
                available_space = self.box_model.content_rect.height - total_children_height

            print(f"total_children_width: {total_children_width}, total_children_height: {total_children_height}, available_space: {available_space}")
            gaps = available_space / (len(self.children_nodes) - 1) if len(self.children_nodes) > 1 else 0
            self.justify_between_gaps = gaps

    def set_children_align_items_stretch(self):
        print(f"align_items: {self.options.align_items}")
        if self.options.align_items == "stretch":
            print(f"box_model.content_rect: {self.box_model.content_rect}")
            for child in self.children_nodes:
                if child.node_type != "leaf":
                    if self.options.flex_direction == "row" and not child.options.height:
                        print(f"stretching height for {child.element_type} to {self.box_model.content_rect.height}")
                        child.options.height = self.box_model.content_rect.height
                    elif self.options.flex_direction == "column" and not child.options.width:
                        print(f"stretching width for {child.element_type} to {self.box_model.content_rect.width}")
                        child.options.width = self.box_model.content_rect.width

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
        self.box_model.accumulate_content_dimensions(rect)

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        # global unique_key
        # self.key = unique_key
        # unique_key += 1
        resolved_width = self.options.width
        resolved_height = self.options.height

        if self.options.width == "100%":
            resolved_width = self.parent_node.box_model.content_rect.width
        if self.options.height == "100%":
            resolved_height = self.parent_node.box_model.content_rect.height

        if self.parent_node and self.parent_node.box_model:
            if self.parent_node.options.align_items == "stretch":
                if self.parent_node.options.flex_direction == "row" and not resolved_height:
                    resolved_height = self.parent_node.box_model.content_rect.height
                elif self.parent_node.options.flex_direction == "column" and not resolved_width:
                    resolved_width = self.parent_node.box_model.content_rect.width

        self.box_model = BoxModelLayout(
            cursor.virtual_x,
            cursor.virtual_y,
            self.options.margin,
            self.options.padding,
            self.options.border,
            width=resolved_width,
            height=resolved_height,
            min_width=self.options.min_width,
            min_height=self.options.min_height,
            max_width=self.options.max_width,
            max_height=self.options.max_height)
        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        last_cursor = Point2d(cursor.virtual_x, cursor.virtual_y)

        growable_counter_axis = []
        growable_primary_axis = []

        # self.set_children_align_items_stretch()

        for i, child in enumerate(self.children_nodes):
            if self.options.align_items == "stretch" or child.options.align_self == "stretch" or \
                    (self.options.flex_direction == "row" and isinstance(child.options.height, str) and "%" in child.options.height) or \
                    (self.options.flex_direction == "column" and isinstance(child.options.width, str) and "%" in child.options.width):
                growable_counter_axis.append(child)

            if child.options.flex:
                growable_primary_axis.append(child)

            self.virtual_render_child(c, cursor, child, i, move_after_last_child=True)

        if growable_counter_axis:
            for i, child in enumerate(growable_counter_axis):
                if child.node_type != "leaf":
                    if self.options.flex_direction == "row" and not child.box_model.fixed_height:
                        child.box_model.accumulate_outer_dimensions_height(self.box_model.content_rect.height)
                    elif self.options.flex_direction == "column" and not child.box_model.fixed_width:
                        child.box_model.accumulate_outer_dimensions_width(self.box_model.content_rect.width)

        if growable_primary_axis:
            remaining_width = self.box_model.content_rect.width - self.box_model.content_children_rect.width
            remaining_height = self.box_model.content_rect.height - self.box_model.content_children_rect.height

            flex_weights = self.calculate_flex_weights(growable_primary_axis)

            for i, child in enumerate(growable_primary_axis):
                if self.options.flex_direction == "row":
                    child.box_model.accumulate_outer_dimensions_width(remaining_width * flex_weights[i])
                elif self.options.flex_direction == "column":
                    child.box_model.accumulate_outer_dimensions_height(remaining_height * flex_weights[i])

        # cursor.virtual_move_to(last_cursor.x, last_cursor.y)

        # if growable_counter_axis or growable_primary_axis:
        #     for i, child in enumerate(self.children_nodes):
        #         self.box_model.accumulate_content_dimensions(child.box_model.margin_rect)
                # self.virtual_render_child(c, cursor, child, i, move_after_last_child=True)
                    # child.virtual_render(c, cursor)
                # self.virtual_render_child(c, cursor, child, i, move_after_last_child=False)

        self.set_justify_between_gaps()

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
            # inner_rect = self.box_model.scroll_box_rect if self.box_model.scrollable else self.box_model.padding_rect
            inner_rect = self.box_model.padding_rect
            if self.is_uniform_border:
                border_width = border_spacing.left
                c.paint.color = self.options.border_color
                c.paint.style = c.paint.Style.STROKE
                c.paint.stroke_width = border_width

                print(f"border_width: {border_width}")
                print(f"self.box_model.padding_rect: {self.box_model.padding_rect}")
                print(f"inner_rect: {inner_rect}")
                print(f"border_spacing: {border_spacing}")

                bordered_rect = Rect(
                    inner_rect.x - border_width / 2,
                    inner_rect.y - border_width / 2,
                    inner_rect.width + border_width,
                    inner_rect.height + border_width,
                )

                if self.options.border_radius:
                    c.draw_rrect(RoundRect.from_rect(bordered_rect, x=self.options.border_radius + border_width / 2, y=self.options.border_radius + border_width / 2))
                else:
                    print(f"bordered_rect: {bordered_rect}")
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
        # self.adjust_for_scroll_y_start(c)
        # self.crop_scrollable_region_start(c)
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

            gap = self.justify_between_gaps or self.options.gap or 0
            if not gap and child.element_type == "text" and self.children_nodes[i + 1].element_type == "text" and not child.options.flex and not self.children_nodes[i + 1].options.flex:
                gap = 16

            self.move_cursor_from_top_left_child_to_next_child_along_align_axis(cursor, child, rect, gap)
            # self.debugger(c, cursor)

        # if view_state := self.debugger(c, cursor, True):
        #     return view_state

        cursor.move_to(last_cursor.x, last_cursor.y)
        # self.debugger(c, cursor)

        # self.adjust_for_scroll_y_end(c)
        # self.crop_scrollable_region_end(c)

        return self.box_model.margin_rect

    def show(self):
        raise NotImplementedError(f"div cannot use .show() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")

    def hide(self):
        raise NotImplementedError(f"div cannot use .hide() directly. Wrap it in a screen()[..] like this: \nmy_ui = None\n\n#show def\nglobal my_ui\n(screen, div, text) = actions.user.ui_elements(['screen', 'div', 'text'])\nmy_ui = screen()[\n  div()[\n    text('hello world')\n  ]\n]\nmy_ui.show()\n\n#hide def\nglobal my_ui\nmy_ui.hide()")