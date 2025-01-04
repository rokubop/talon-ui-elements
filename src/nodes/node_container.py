from itertools import cycle
from itertools import cycle
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from ..constants import ELEMENT_ENUM_TYPE, NODE_ENUM_TYPE
from ..box_model import BoxModelLayout
from ..cursor import Cursor
from ..interfaces import NodeContainerType
from ..properties import Properties
from .node import Node

class NodeContainer(Node, NodeContainerType):
    def __init__(self, element_type, properties: Properties = None):
        super().__init__(element_type=element_type, properties=properties)
        self.scroll_y = 0
        self.scroll_y_percentage = 0
        self.is_uniform_border = True
        self.justify_between_gaps = None
        self.debug_number = 0
        self.debug_color = "red"
        self.debug_colors = iter(cycle(["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]))

    def set_scroll_y(self, delta: int):
        """Adjust the scroll position based on input (e.g., mouse scroll)."""
        self.scroll_y += delta

        max_top_scroll_y = 0
        max_bottom_scroll_y = self.properties.height

        if self.scroll_y < max_top_scroll_y:
            self.scroll_y = max_top_scroll_y
        elif self.scroll_y > max_bottom_scroll_y:
            self.scroll_y = max_bottom_scroll_y

        if self.properties.height > 0:
            self.scroll_y_percentage = self.scroll_y / self.properties.height
        else:
            self.scroll_y_percentage = 0

    def set_justify_between_gaps(self):
        if self.properties.justify_content == "space_between":
            total_children_width = None
            total_children_height = None

            if self.properties.flex_direction == "row":
                total_children_width = sum(child.box_model.margin_rect.width for child in self.children_nodes)
                available_space = self.box_model.content_rect.width - total_children_width
            else:
                total_children_height = sum(child.box_model.margin_rect.height for child in self.children_nodes)
                available_space = self.box_model.content_rect.height - total_children_height

            gaps = available_space / (len(self.children_nodes) - 1) if len(self.children_nodes) > 1 else 0
            self.justify_between_gaps = gaps

    def virtual_gap_between_elements(self, node, i):
        gap = self.properties.gap or 0

        if self.properties.gap is None and node.element_type == ELEMENT_ENUM_TYPE["text"] and \
                self.children_nodes[i - 1].element_type == ELEMENT_ENUM_TYPE["text"] \
                and not self.properties.justify_content == "space_between":
            if self.tree.render_version == 1:
                gap = 16
            elif self.tree.render_version == 2 and self.properties.flex_direction == "column":
                gap = 16

        return gap

    def virtual_render_child(self, c: SkiaCanvas, cursor: Cursor, child: Node, i: int, move_after_last_child = True):
        gap = self.virtual_gap_between_elements(child, i)
        a_cursor = Point2d(cursor.virtual_x, cursor.virtual_y)
        rect = child.virtual_render(c, cursor)

        cursor.virtual_move_to(a_cursor.x, a_cursor.y)
        if move_after_last_child or i != len(self.children_nodes) - 1:
            if self.properties.flex_direction == "column":
                cursor.virtual_move_to(cursor.virtual_x, cursor.virtual_y + rect.height + gap)
            elif self.properties.flex_direction == "row":
                cursor.virtual_move_to(cursor.virtual_x + rect.width + gap, cursor.virtual_y)

        self.box_model.accumulate_content_dimensions(rect)

    def grow_intrinsic_size(self, c: SkiaCanvas, cursor: Cursor):
        growable_counter_axis = []
        growable_primary_axis = []
        growable_primary_axis_flex = []

        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        last_cursor = Point2d(cursor.virtual_x, cursor.virtual_y)

        self.set_justify_between_gaps()

        # Intristic sizing phase
        all_growable_counter_axis = self.properties.align_items == "stretch" or \
            (self.properties.flex_direction == "row" and \
             isinstance(self.properties.height, str) and "%" in self.properties.height) or \
            (self.properties.flex_direction == "column" and \
             isinstance(self.properties.width, str) and "%" in self.properties.width)

        for i, child in enumerate(self.children_nodes):
            # if child.node_type != "leaf":
            if all_growable_counter_axis or child.properties.align_self == "stretch" or \
                    (self.properties.flex_direction == "row" and \
                    isinstance(child.properties.height, str) and "%" in child.properties.height) or \
                    (self.properties.flex_direction == "column" and \
                    isinstance(child.properties.width, str) and "%" in child.properties.width):
                growable_counter_axis.append(child)

            if self.properties.flex_direction == "row" and isinstance(child.properties.width, str) and "%" in child.properties.width:
                child.flex_evaluated = self.normalize_to_flex(child.properties.width)
            elif self.properties.flex_direction == "column" and isinstance(child.properties.height, str) and "%" in child.properties.height:
                child.flex_evaluated = self.normalize_to_flex(child.properties.height)

            if child.properties.flex or child.flex_evaluated:
                growable_primary_axis_flex.append(child)

        # Second pass grow children
        if growable_counter_axis:
            for i, child in enumerate(growable_counter_axis):
                if child.node_type != NODE_ENUM_TYPE["leaf"]:
                    if self.properties.align_items == "stretch":
                        if self.properties.flex_direction == "row" and not child.box_model.fixed_height:
                            child.box_model.accumulate_outer_dimensions_height(self.box_model.content_rect.height)
                        elif self.properties.flex_direction == "column" and not child.box_model.fixed_width:
                            child.box_model.accumulate_outer_dimensions_width(self.box_model.content_rect.width)

        if growable_primary_axis_flex:
            remaining_width = self.box_model.content_rect.width - self.box_model.content_children_rect.width
            remaining_height = self.box_model.content_rect.height - self.box_model.content_children_rect.height
            flex_weights = self.calculate_justify_flex_weights(growable_primary_axis_flex)

            for i, child in enumerate(growable_primary_axis_flex):
                if self.properties.flex_direction == "row":
                    additional_width = remaining_width * flex_weights[i]
                    child.box_model.accumulate_outer_dimensions_width(child.box_model.margin_rect.width + additional_width)
                elif self.properties.flex_direction == "column":
                    additional_height = remaining_height * flex_weights[i]
                    child.box_model.accumulate_outer_dimensions_height(child.box_model.margin_rect.height + additional_height)

        for i, child in enumerate(self.children_nodes):
            child.grow_intrinsic_size(c, cursor)

        cursor.virtual_move_to(last_cursor.x, last_cursor.y)

        return self.box_model.margin_rect

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        resolved_width = self.properties.width
        resolved_height = self.properties.height

        # resolve in next block
        if self.properties.width == "100%":
            resolved_width = 0
        if self.properties.height == "100%":
            resolved_height = 0

        if self.parent_node and self.parent_node.box_model:
            if self.parent_node.properties.align_items == "stretch":
                if self.parent_node.properties.flex_direction == "row" and not resolved_height:
                    resolved_height = self.parent_node.box_model.content_rect.height
                elif self.parent_node.properties.flex_direction == "column" and not resolved_width:
                    resolved_width = self.parent_node.box_model.content_rect.width

        if self.tree.redistribute_box_model:
            self.box_model.redistribute_from_rect(
                Rect(cursor.virtual_x, cursor.virtual_y, resolved_width, resolved_height)
            )
        else:
            self.box_model = BoxModelLayout(
                cursor.virtual_x,
                cursor.virtual_y,
                self.properties.margin,
                self.properties.padding,
                self.properties.border,
                width=resolved_width,
                height=resolved_height,
                fixed_width=bool(self.properties.width and not isinstance(self.properties.width, str)),
                fixed_height=bool(self.properties.height and not isinstance(self.properties.height, str)),
                min_width=self.properties.min_width,
                min_height=self.properties.min_height,
                max_width=self.properties.max_width,
                max_height=self.properties.max_height)
        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        last_cursor = Point2d(cursor.virtual_x, cursor.virtual_y)

        # Intristic sizing phase
        if self.children_nodes:
            for i, child in enumerate(self.children_nodes):
                self.virtual_render_child(c, cursor, child, i, move_after_last_child=True)
        else:
            # fixes issue with empty divs with no children collapsing to 0 width or height
            self.box_model.accumulate_content_dimensions(Rect(cursor.virtual_x, cursor.virtual_y, 0, 0))

        cursor.virtual_move_to(last_cursor.x, last_cursor.y)

        return self.box_model.margin_rect

    def normalize_to_flex(self, percentage):
        if percentage and isinstance(percentage, str) and "%" in percentage:
            return float(percentage.replace("%", "")) / 100
        return 0

    def calculate_justify_flex_weights(self, flex_children):
        flex_values = []

        for child in flex_children:
            if child.properties.flex:
                flex_values.append(child.properties.flex)
            elif child.flex_evaluated:
                flex_values.append(child.flex_evaluated)

        total_flex = sum(flex_values)

        return [flex / total_flex for flex in flex_values]

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
            inner_rect = self.box_model.padding_rect
            if self.is_uniform_border:
                border_width = border_spacing.left
                c.paint.color = self.properties.border_color
                c.paint.style = c.paint.Style.STROKE
                c.paint.stroke_width = border_width

                bordered_rect = Rect(
                    inner_rect.x - border_width / 2,
                    inner_rect.y - border_width / 2,
                    inner_rect.width + border_width,
                    inner_rect.height + border_width,
                )

                if self.properties.border_radius:
                    c.draw_rrect(RoundRect.from_rect(bordered_rect, x=self.properties.border_radius + border_width / 2, y=self.properties.border_radius + border_width / 2))
                else:
                    c.draw_rect(bordered_rect)
            else:
                c.paint.color = self.properties.border_color
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
        if self.properties.background_color:
            c.paint.color = self.properties.background_color
            if self.properties.border_radius and self.is_uniform_border:
                c.draw_rrect(RoundRect.from_rect(inner_rect, x=self.properties.border_radius, y=self.properties.border_radius))
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
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + self.box_model.content_children_rect.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + self.box_model.content_children_rect.height)
        else:
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x + self.box_model.content_children_rect.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x + self.box_model.content_children_rect.width, cursor.y)

    def move_cursor_to_top_left_child_based_on_align_axis(self, cursor: Cursor, child):
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y - child.box_model.margin_rect.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y - child.box_model.margin_rect.height)

        elif self.properties.flex_direction == "column":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x - child.box_model.margin_rect.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x - child.box_model.margin_rect.width, cursor.y)

    def move_cursor_from_top_left_child_to_next_child_along_align_axis(self, cursor: Cursor, child, rect: Rect, gap = 0):
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + child.box_model.margin_rect.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + child.box_model.margin_rect.height)
            cursor.move_to(cursor.x + rect.width + gap, cursor.y)
        else:
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x + child.box_model.margin_rect.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x + child.box_model.margin_rect.width, cursor.y)
            cursor.move_to(cursor.x, cursor.y + rect.height + gap)

    def gap_between_elements(self, node, i):
        gap = self.justify_between_gaps or self.properties.gap or 0

        if not gap and node.element_type == ELEMENT_ENUM_TYPE["text"] and \
                self.children_nodes[i + 1].element_type == ELEMENT_ENUM_TYPE["text"] and \
                not node.properties.flex and not self.children_nodes[i + 1].properties.flex and \
                not self.properties.justify_content == "space_between":
            if self.tree.render_version == 1:
                gap = 16
            elif self.tree.render_version == 2 and self.properties.flex_direction == "column":
                gap = 16

        return gap

    def render(self, c: SkiaCanvas, cursor: Cursor, scroll_region_key: int = None):
        if view_state := self.debugger(c, cursor, True):
            return view_state

        if self.tree.draggable_node_delta_pos and self.tree.draggable_node == self:
            self.box_model.move_delta(
                self.tree.draggable_node_delta_pos.x,
                self.tree.draggable_node_delta_pos.y,
                self.properties.flex_direction,
                self.properties.align_items,
                self.properties.justify_content
            )
        else:
            self.box_model.position_for_render(
                cursor,
                self.properties.flex_direction,
                self.properties.align_items,
                self.properties.justify_content
            )

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

            gap = self.gap_between_elements(child, i)
            self.move_cursor_from_top_left_child_to_next_child_along_align_axis(cursor, child, rect, gap)
            # self.debugger(c, cursor)

        # if view_state := self.debugger(c, cursor, True):
        #     return view_state

        cursor.move_to(last_cursor.x, last_cursor.y)
        # self.debugger(c, cursor)

        # self.adjust_for_scroll_y_end(c)
        # self.crop_scrollable_region_end(c)

        return self.box_model.margin_rect