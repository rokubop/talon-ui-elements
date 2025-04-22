from itertools import cycle
from typing import List
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from .node import Node
from ..box_model import BoxModelV2
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_SCROLL_BAR_TRACK_COLOR, DEFAULT_SCROLL_BAR_THUMB_COLOR
from ..cursor import Cursor
from ..interfaces import NodeContainerType, Size2d, NodeType, RenderItem
from ..properties import Properties

class NodeContainer(Node, NodeContainerType):
    def __init__(self, element_type, properties: Properties = None):
        super().__init__(element_type=element_type, properties=properties)
        self.justify_between_gaps = None
        self.debug_number = 0
        self.debug_color = "red"
        self.debug_colors = iter(cycle(["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]))

    def render_scroll_bar(self, c: SkiaCanvas):
        scrollable = self.tree.meta_state.scrollable.get(self.id, None)
        if scrollable and self.box_model.scroll_bar_thumb_rect:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = DEFAULT_SCROLL_BAR_TRACK_COLOR
            c.draw_rect(self.box_model.scroll_bar_track_rect)
            c.paint.color = DEFAULT_SCROLL_BAR_THUMB_COLOR
            c.draw_rect(self.box_model.scroll_bar_thumb_rect)

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        """
        First step in the layout process. Calculates the intrinsic size.
        Determines natural width/height based on content or user-defined size.
        """
        children_accumulated_size = Size2d(0, 0)
        is_row = self.properties.flex_direction == "row"
        primary_axis = "width" if is_row else "height"
        secondary_axis = "height" if is_row else "width"
        participating_children_nodes = self.participating_children_nodes

        if participating_children_nodes:
            for i, child in enumerate(participating_children_nodes):
                margin_size = child.v2_measure_intrinsic_size(c)

                # find the single item with the maximum length for secondary axis
                setattr(
                    children_accumulated_size,
                    secondary_axis,
                    max(
                        getattr(children_accumulated_size, secondary_axis),
                        getattr(margin_size, secondary_axis)
                    )
                )

                # total all the item lengths for primary axis
                setattr(
                    children_accumulated_size,
                    primary_axis,
                    getattr(children_accumulated_size, primary_axis) + getattr(margin_size, primary_axis)
                )

            fixed_gap = self.determine_intrinsic_fixed_gap()
            for i, child in enumerate(participating_children_nodes):
                if i != len(participating_children_nodes) - 1:
                    gap = self.gap_between_elements(child, i, fixed_gap)
                    setattr(
                        children_accumulated_size,
                        primary_axis,
                        getattr(children_accumulated_size, primary_axis) + gap
                    )

        self.box_model = BoxModelV2(
            self.properties,
            children_accumulated_size,
            self.clip_nodes,
            self.relative_positional_node
        )

        return self.box_model.intrinsic_margin_size_with_bounding_constraints

    def v2_grow_size(self):
        growable_counter_axis: List[NodeType] = []
        growable_primary_axis_flex: List[NodeType] = []

        # Not perfect, but mostly works - glosses over specific child overrides
        all_growable_counter_axis = self.properties.align_items == "stretch"
            # Why was this part of our v1 implementation?
            # or \
            # (self.properties.flex_direction == "row" and \
            #  isinstance(self.properties.height, str) and "%" in self.properties.height) or \
            # (self.properties.flex_direction == "column" and \
            #  isinstance(self.properties.width, str) and "%" in self.properties.width)

        for i, child in enumerate(self.participating_children_nodes):
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

        # Grow items / counter axis
        if growable_counter_axis:
            for i, child in enumerate(growable_counter_axis):
                # Consider: growable_counter_axis should only contain things that really should be stretched
                if self.properties.flex_direction == "row" and not child.box_model.fixed_height:
                    child.box_model.grow_calculated_height_to(self.box_model.calculated_content_size.height)
                elif self.properties.flex_direction == "column" and not child.box_model.fixed_width:
                    child.box_model.grow_calculated_width_to(self.box_model.calculated_content_size.width)

            # Consider: shouldn't this just grow content children to the growth we did above?
            # Regardless of stretch or not.
            # if self.properties.align_items == "stretch":
            if self.properties.flex_direction == "row":
                self.box_model.maximize_content_children_height()
            elif self.properties.flex_direction == "column":
                self.box_model.maximize_content_children_width()

        # Grow justification / primary axis
        if growable_primary_axis_flex:
            flex_direction = self.properties.flex_direction
            if flex_direction == "row":
                remaining = self.box_model.calculated_content_size.width - self.box_model.calculated_content_children_size.width
                grow_function = lambda child, size: child.box_model.grow_calculated_width_by(size)
            elif flex_direction == "column":
                remaining = self.box_model.calculated_content_size.height - self.box_model.calculated_content_children_size.height
                grow_function = lambda child, size: child.box_model.grow_calculated_height_by(size)

            if remaining > 0:
                flex_weights = self.calculate_justify_flex_weights(growable_primary_axis_flex)
                for i, child in enumerate(growable_primary_axis_flex):
                    additional_size = remaining * flex_weights[i]
                    grow_function(child, additional_size)
                if flex_direction == "row":
                    self.box_model.maximize_content_children_width()
                elif flex_direction == "column":
                    self.box_model.maximize_content_children_height()

        for child in self.participating_children_nodes:
            child.v2_grow_size()

    def v2_constrain_size(self, available_size: Size2d = None) -> bool:
        content_constraint_size = self.box_model.constrain_size(available_size, self.properties.overflow)
        children_accumulated_size = Size2d(0, 0)
        is_row = self.properties.flex_direction == "row"
        primary_axis = "width" if is_row else "height"
        secondary_axis = "height" if is_row else "width"

        def accumulate(child: NodeType):
            # find the single item with the maximum length for secondary axis
            setattr(
                children_accumulated_size,
                secondary_axis,
                max(
                    getattr(children_accumulated_size, secondary_axis),
                    getattr(child.box_model.margin_size, secondary_axis)
                )
            )

            # total all the item lengths for primary axis
            setattr(
                children_accumulated_size,
                primary_axis,
                getattr(children_accumulated_size, primary_axis) + getattr(child.box_model.margin_size, primary_axis)
            )

        participating_children_nodes = self.participating_children_nodes

        if content_constraint_size:
            new_available_size = content_constraint_size.copy()

            for child in participating_children_nodes:
                child.v2_constrain_size(new_available_size)
                if self.properties.flex_direction == "row" and new_available_size.width != None:
                    new_available_size.width = max(0, new_available_size.width - child.box_model.margin_size.width)
                    # new_available_size.width = max(0, new_available_size.width - child.box_model.calculated_margin_size.width)
                elif self.properties.flex_direction == "column" and new_available_size.height != None:
                    new_available_size.height = max(0, new_available_size.height - child.box_model.margin_size.height)
                    # new_available_size.height = max(0, new_available_size.height - child.box_model.calculated_margin_size.height)
                accumulate(child)
        else:
            for child in participating_children_nodes:
                child.v2_constrain_size()
                accumulate(child)

        fixed_gap = self.determine_intrinsic_fixed_gap()
        for i, child in enumerate(participating_children_nodes):
            if i != len(participating_children_nodes) - 1:
                gap = self.gap_between_elements(child, i, fixed_gap)
                setattr(
                    children_accumulated_size,
                    primary_axis,
                    getattr(children_accumulated_size, primary_axis) + gap
                )

        self.box_model.shrink_content_children_size(children_accumulated_size)

    def v2_layout(self, cursor: Cursor) -> Size2d:
        if self.participates_in_layout:
            self.v2_drag_offset(cursor)
        else:
            self.box_model.position_from_relative_parent(cursor)

        self.box_model.position_for_render(
            cursor,
            self.properties.flex_direction,
            self.properties.align_items,
            self.properties.justify_content
        )

        scrollable = self.tree.meta_state.scrollable.get(self.id, None)
        if scrollable:
            self.box_model.adjust_scroll_y(scrollable.offset_y)

        self.v2_move_cursor_to_align_axis_before_children_render(cursor)

        last_cursor = Point2d(cursor.x, cursor.y)
        self.box_model.shift_relative_position(cursor)
        fixed_gap = self.determine_layout_fixed_gap()
        for i, child in enumerate(self.participating_children_nodes):
            self.v2_move_cursor_to_top_left_child_based_on_align_axis(cursor, child)

            child_last_cursor = Point2d(cursor.x, cursor.y)
            size = child.v2_layout(cursor)
            cursor.move_to(child_last_cursor.x, child_last_cursor.y)

            if i == len(self.participating_children_nodes) - 1:
                break

            gap = self.gap_between_elements(child, i, fixed_gap)
            self.v2_move_cursor_from_top_left_child_to_next_child_along_align_axis(cursor, child, size, gap)

        cursor.move_to(last_cursor.x, last_cursor.y)
        return self.box_model.margin_size

    def draw_start(self, c: SkiaCanvas):
        self.v2_render_borders(c),
        self.v2_crop_start(c),
        self.v2_render_background(c)

    def draw_end(self, c: SkiaCanvas):
        self.v2_crop_end(c),
        self.render_scroll_bar(c)

    def v2_build_render_list(self):
        self.tree.append_to_render_list(
            node=self,
            draw=self.draw_start
        )

        for child in self.children_nodes:
            child.v2_build_render_list()

        self.tree.append_to_render_list(
            node=self,
            draw=self.draw_end
        )

    def v2_render(self, c):
        if self.tree:
            self.v2_render_borders(c)
            self.v2_crop_start(c)
            self.v2_render_background(c)
            for child in self.children_nodes:
                child.v2_render(c)
            self.v2_crop_end(c)
            self.render_scroll_bar(c)

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

    def v2_adjust_for_scroll_y_start(self):
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model.adjust_scroll_y(self.tree.meta_state.scrollable[self.id].offset_y)

    def v2_adjust_for_scroll_y_end(self):
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model.adjust_scroll_y(-self.tree.meta_state.scrollable[self.id].offset_y)

    def v2_crop_start(self, c: SkiaCanvas):
        if self.properties.overflow.scrollable or (self.box_model.overflow.is_boundary and \
                (self.box_model.overflow_size.width or \
                self.box_model.overflow_size.height)):
            c.save()
            c.clip_rect(self.box_model.padding_rect)

    def v2_crop_end(self, c: SkiaCanvas):
        if self.properties.overflow.scrollable or (self.box_model.overflow.is_boundary and \
                (self.box_model.overflow_size.width or \
                self.box_model.overflow_size.height)):
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

    def v2_move_cursor_to_align_axis_before_children_render(self, cursor: Cursor):
        cursor.move_to(self.box_model.content_children_pos.x, self.box_model.content_children_pos.y)
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + self.box_model.content_children_size.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + self.box_model.content_children_size.height)
        else:
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x + self.box_model.content_children_size.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x + self.box_model.content_children_size.width, cursor.y)

    def v2_move_cursor_to_top_left_child_based_on_align_axis(self, cursor: Cursor, child):
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y - child.box_model.margin_size.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y - child.box_model.margin_size.height)
        elif self.properties.flex_direction == "column":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x - child.box_model.margin_size.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x - child.box_model.margin_size.width, cursor.y)

    def v2_move_cursor_from_top_left_child_to_next_child_along_align_axis(self, cursor: Cursor, child, size: Rect, gap = 0):
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + child.box_model.margin_size.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + child.box_model.margin_size.height)
            cursor.move_to(cursor.x + size.width + gap, cursor.y)
        else:
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x + child.box_model.margin_size.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x + child.box_model.margin_size.width, cursor.y)
            cursor.move_to(cursor.x, cursor.y + size.height + gap)

    def gap_between_elements(self, node, i, fixed_gap = 0):
        gap = fixed_gap
        participating_children_nodes = self.participating_children_nodes

        if not gap and node.element_type == ELEMENT_ENUM_TYPE["text"] and \
                participating_children_nodes[i + 1].element_type == ELEMENT_ENUM_TYPE["text"] and \
                not node.properties.flex and not participating_children_nodes[i + 1].properties.flex and \
                not self.properties.justify_content == "space_between":
            if self.tree.render_version == 1:
                gap = 16
            elif self.tree.render_version == 2 and self.properties.flex_direction == "column":
                gap = 16

        return gap

    def determine_intrinsic_fixed_gap(self):
        return self.properties.gap or 0

    def determine_layout_fixed_gap(self):
        fixed_gap = self.properties.gap or 0
        if self.properties.justify_content == "space_between":
            total_children_width = None
            total_children_height = None
            participating_children_nodes = self.participating_children_nodes

            if self.properties.flex_direction == "row":
                total_children_width = sum(child.box_model.margin_size.width for child in participating_children_nodes)
                available_space = self.box_model.content_size.width - total_children_width
            else:
                total_children_height = sum(child.box_model.margin_size.height for child in participating_children_nodes)
                available_space = self.box_model.content_size.height - total_children_height

            fixed_gap = available_space / (len(participating_children_nodes) - 1) if len(participating_children_nodes) > 1 else 0
        return fixed_gap