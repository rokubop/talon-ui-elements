from itertools import cycle
from itertools import cycle
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from ..constants import ELEMENT_ENUM_TYPE, NODE_ENUM_TYPE
from ..box_model import BoxModelLayout, BoxModelV2
from ..cursor import Cursor
from ..interfaces import NodeContainerType, Size2d, NodeType
from ..properties import Properties
from .node import Node
from typing import List

class NodeContainer(Node, NodeContainerType):
    def __init__(self, element_type, properties: Properties = None):
        super().__init__(element_type=element_type, properties=properties)
        self.justify_between_gaps = None
        self.debug_number = 0
        self.debug_color = "red"
        self.debug_colors = iter(cycle(["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]))

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
        rect, intrinsic_rect = child.virtual_render(c, cursor)

        cursor.virtual_move_to(a_cursor.x, a_cursor.y)
        if move_after_last_child or i != len(self.children_nodes) - 1:
            if self.properties.flex_direction == "column":
                cursor.virtual_move_to(cursor.virtual_x, cursor.virtual_y + rect.height + gap)
            elif self.properties.flex_direction == "row":
                cursor.virtual_move_to(cursor.virtual_x + rect.width + gap, cursor.virtual_y)

        self.box_model.accumulate_intrinsic_content_dimensions(intrinsic_rect)
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
                            child.box_model.accumulate_intrinsic_outer_dimensions_height(self.box_model.content_rect.height)
                            child.box_model.accumulate_outer_dimensions_height(self.box_model.content_rect.height)
                        elif self.properties.flex_direction == "column" and not child.box_model.fixed_width:
                            child.box_model.accumulate_intrinsic_outer_dimensions_width(self.box_model.content_rect.width)
                            child.box_model.accumulate_outer_dimensions_width(self.box_model.content_rect.width)

        if growable_primary_axis_flex:
            remaining_width = self.box_model.content_rect.width - self.box_model.content_children_rect.width
            remaining_height = self.box_model.content_rect.height - self.box_model.content_children_rect.height
            flex_weights = self.calculate_justify_flex_weights(growable_primary_axis_flex)

            for i, child in enumerate(growable_primary_axis_flex):
                if self.properties.flex_direction == "row":
                    additional_width = remaining_width * flex_weights[i]
                    child.box_model.accumulate_intrinsic_outer_dimensions_width(child.box_model.margin_rect.width + additional_width)
                    child.box_model.accumulate_outer_dimensions_width(child.box_model.margin_rect.width + additional_width)
                elif self.properties.flex_direction == "column":
                    additional_height = remaining_height * flex_weights[i]
                    child.box_model.accumulate_intrinsic_outer_dimensions_height(child.box_model.margin_rect.height + additional_height)
                    child.box_model.accumulate_outer_dimensions_height(child.box_model.margin_rect.height + additional_height)

        for i, child in enumerate(self.children_nodes):
            child.grow_intrinsic_size(c, cursor)

        cursor.virtual_move_to(last_cursor.x, last_cursor.y)

        return self.box_model.margin_rect

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        """
        First step in the layout process. Calculates the intrinsic size.
        Determines natural width/height based on content or user-defined size.
        """
        children_accumulated_size = Size2d(0, 0)
        is_row = self.properties.flex_direction == "row"
        primary_axis = "width" if is_row else "height"
        secondary_axis = "height" if is_row else "width"

        if self.children_nodes:
            for i, child in enumerate(self.children_nodes):
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
            for i, child in enumerate(self.children_nodes):
                if i != len(self.children_nodes) - 1:
                    gap = self.gap_between_elements(child, i, fixed_gap)
                    setattr(
                        children_accumulated_size,
                        primary_axis,
                        getattr(children_accumulated_size, primary_axis) + gap
                    )

        self.box_model_v2 = BoxModelV2(
            self.properties,
            children_accumulated_size,
            self.clip_nodes
        )

        return self.box_model_v2.intrinsic_margin_size

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

        for i, child in enumerate(self.children_nodes):
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
                if self.properties.flex_direction == "row" and not child.box_model_v2.fixed_height:
                    child.box_model_v2.grow_calculated_height_to(self.box_model_v2.calculated_content_size.height)
                elif self.properties.flex_direction == "column" and not child.box_model_v2.fixed_width:
                    child.box_model_v2.grow_calculated_width_to(self.box_model_v2.calculated_content_size.width)

            # Consider: shouldn't this just grow content children to the growth we did above?
            # Regardless of stretch or not.
            # if self.properties.align_items == "stretch":
            if self.properties.flex_direction == "row":
                self.box_model_v2.maximize_content_children_height()
            elif self.properties.flex_direction == "column":
                self.box_model_v2.maximize_content_children_width()

        # Grow justification / primary axis
        if growable_primary_axis_flex:
            flex_direction = self.properties.flex_direction
            if flex_direction == "row":
                remaining = self.box_model_v2.calculated_content_size.width - self.box_model_v2.calculated_content_children_size.width
                grow_function = lambda child, size: child.box_model_v2.grow_calculated_width_by(size)
            elif flex_direction == "column":
                remaining = self.box_model_v2.calculated_content_size.height - self.box_model_v2.calculated_content_children_size.height
                grow_function = lambda child, size: child.box_model_v2.grow_calculated_height_by(size)

            if remaining > 0:
                flex_weights = self.calculate_justify_flex_weights(growable_primary_axis_flex)
                for i, child in enumerate(growable_primary_axis_flex):
                    additional_size = remaining * flex_weights[i]
                    grow_function(child, additional_size)
                if flex_direction == "row":
                    self.box_model_v2.maximize_content_children_width()
                elif flex_direction == "column":
                    self.box_model_v2.maximize_content_children_height()

        for child in self.children_nodes:
            child.v2_grow_size()

    def v2_constrain_size(self, available_size: Size2d = None) -> bool:
        content_constraint_size = self.box_model_v2.constrain_size(available_size, self.properties.overflow)
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
                    getattr(child.box_model_v2.margin_size, secondary_axis)
                )
            )

            # total all the item lengths for primary axis
            setattr(
                children_accumulated_size,
                primary_axis,
                getattr(children_accumulated_size, primary_axis) + getattr(child.box_model_v2.margin_size, primary_axis)
            )

        if content_constraint_size:
            new_available_size = content_constraint_size.copy()

            for child in self.children_nodes:
                child.v2_constrain_size(new_available_size)
                if self.properties.flex_direction == "row" and new_available_size.width != None:
                    new_available_size.width = max(0, new_available_size.width - child.box_model_v2.calculated_margin_size.width)
                elif self.properties.flex_direction == "column" and new_available_size.height != None:
                    new_available_size.height = max(0, new_available_size.height - child.box_model_v2.calculated_margin_size.height)
                accumulate(child)
        else:
            for child in self.children_nodes:
                child.v2_constrain_size()
                accumulate(child)

        fixed_gap = self.determine_intrinsic_fixed_gap()
        for i, child in enumerate(self.children_nodes):
            if i != len(self.children_nodes) - 1:
                gap = self.gap_between_elements(child, i, fixed_gap)
                setattr(
                    children_accumulated_size,
                    primary_axis,
                    getattr(children_accumulated_size, primary_axis) + gap
                )

        self.box_model_v2.shrink_content_children_size(children_accumulated_size)

        # return True if content_constraint_size else False

    def v2_layout(self, cursor: Cursor) -> Size2d:
        # if self.properties.id == "body" or self.properties.id == "drag":
        #     c.paint.style = c.paint.Style.STROKE
        #     c.paint.color = "green"
        #     c.draw_circle(cursor.x, cursor.y, 40)
        self.v2_drag_offset(cursor)
        self.box_model_v2.position_for_render(
            cursor,
            self.properties.flex_direction,
            self.properties.align_items,
            self.properties.justify_content
        )

        scrollable = self.tree.meta_state.scrollable.get(self.id, None)
        if scrollable:
            self.box_model_v2.adjust_scroll_y(scrollable.offset_y)
            # cursor.offset(0, -scrollable.offset_y)

        # if self.properties.id == "body" or self.properties.id == "drag":
        #     c.paint.style = c.paint.Style.STROKE
        #     c.paint.color = "blue"
        #     c.draw_circle(cursor.x, cursor.y, 20)

        # print(f"NodeContainer - Layout: {getattr(self, 'id', None)} {self.box_model_v2.margin_pos}")

        self.v2_move_cursor_to_align_axis_before_children_render(cursor)

        # if self.properties.is_scrollable() and self.id in self.tree.meta_state.scrollable:
        #     scroll_offset = self.tree.meta_state.scrollable[self.id]
        #     cursor.offset(scroll_offset.offset_x, scroll_offset.offset_y)
            # print('cursor old', cursor.x, cursor.y)
            # print('offsetting', scroll_offset.offset_x, scroll_offset.offset_y)
            # print('cursor new', cursor.x, cursor.y)

        # if self.properties.id == "body" or self.properties.id == "drag":
        #     c.paint.color = "red"
        #     c.paint.style = c.paint.Style.STROKE
        #     c.draw_circle(cursor.x, cursor.y, 20)

        last_cursor = Point2d(cursor.x, cursor.y)
        fixed_gap = self.determine_layout_fixed_gap()
        for i, child in enumerate(self.children_nodes):
            self.v2_move_cursor_to_top_left_child_based_on_align_axis(cursor, child)

            # if self.properties.id == "body" or self.properties.id == "drag":
            #     c.paint.style = c.paint.Style.STROKE
            #     c.paint.color = "yellow"
            #     c.draw_circle(cursor.x, cursor.y, 20)

            child_last_cursor = Point2d(cursor.x, cursor.y)
            size = child.v2_layout(cursor)
            cursor.move_to(child_last_cursor.x, child_last_cursor.y)

            if i == len(self.children_nodes) - 1:
                break

            gap = self.gap_between_elements(child, i, fixed_gap)
            self.v2_move_cursor_from_top_left_child_to_next_child_along_align_axis(cursor, child, size, gap)
            # self.tree.current_canvas.paint.color = "red"
            # self.tree.current_canvas.draw_circle(cursor.x, cursor.y, 3)

        cursor.move_to(last_cursor.x, last_cursor.y)
        return self.box_model_v2.margin_size

    def v2_render(self, c):
        self.v2_render_borders(c)
        self.v2_crop_start(c)
        self.v2_render_background(c)
        for child in self.children_nodes:
            child.v2_render(c)
        self.v2_crop_end(c)

    def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
        resolved_width = self.properties.width
        resolved_height = self.properties.height

        # resolve in next blockyou do need the cursor the for engines excising
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
                max_height=self.properties.max_height,
                overflow=self.properties.overflow,
                constraint_nodes=self.constraint_nodes)
        cursor.virtual_move_to(self.box_model.content_children_rect.x, self.box_model.content_children_rect.y)
        last_cursor = Point2d(cursor.virtual_x, cursor.virtual_y)

        # Intristic sizing phase
        if self.children_nodes:
            for i, child in enumerate(self.children_nodes):
                self.virtual_render_child(c, cursor, child, i, move_after_last_child=True)
        else:
            # fixes issue with empty divs with no children collapsing to 0 width or height
            rect = Rect(cursor.virtual_x, cursor.virtual_y, 0, 0)
            self.box_model.accumulate_intrinsic_content_dimensions(rect)
            self.box_model.accumulate_content_dimensions(rect)

        cursor.virtual_move_to(last_cursor.x, last_cursor.y)

        return self.box_model.margin_rect, self.box_model.intrinsic_margin_rect

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
            inner_rect = self.box_model.scroll_box_rect if self.box_model.scrollable else self.box_model.padding_rect
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
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model.adjust_scroll_y(self.tree.meta_state.scrollable[self.id].offset_y, c)

    def adjust_for_scroll_y_end(self, c: SkiaCanvas):
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model.adjust_scroll_y(-self.tree.meta_state.scrollable[self.id].offset_y, c)

    def v2_adjust_for_scroll_y_start(self, c: SkiaCanvas):
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model_v2.adjust_scroll_y(self.tree.meta_state.scrollable[self.id].offset_y, c)

    def v2_adjust_for_scroll_y_end(self, c: SkiaCanvas):
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model_v2.adjust_scroll_y(-self.tree.meta_state.scrollable[self.id].offset_y, c)

    def crop_scrollable_region_start(self, c: SkiaCanvas):
        if self.box_model.scrollable and self.box_model.scroll_box_rect:
            c.save()
            c.clip_rect(self.box_model.scroll_box_rect)

    def crop_scrollable_region_end(self, c: SkiaCanvas):
        if self.box_model.scrollable and self.box_model.scroll_box_rect:
            c.restore()

    def v2_crop_start(self, c: SkiaCanvas):
        if self.properties.overflow.scrollable or (self.box_model_v2.overflow.is_boundary and \
                (self.box_model_v2.overflow_size.width or \
                self.box_model_v2.overflow_size.height)):
            c.save()
            c.clip_rect(self.box_model_v2.padding_rect)

    def v2_crop_end(self, c: SkiaCanvas):
        if self.properties.overflow.scrollable or (self.box_model_v2.overflow.is_boundary and \
                (self.box_model_v2.overflow_size.width or \
                self.box_model_v2.overflow_size.height)):
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
        cursor.move_to(self.box_model_v2.content_children_pos.x, self.box_model_v2.content_children_pos.y)
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + self.box_model_v2.content_children_size.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + self.box_model_v2.content_children_size.height)
        else:
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x + self.box_model_v2.content_children_size.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x + self.box_model_v2.content_children_size.width, cursor.y)

    def v2_move_cursor_to_top_left_child_based_on_align_axis(self, cursor: Cursor, child):
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y - child.box_model_v2.margin_size.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y - child.box_model_v2.margin_size.height)
        elif self.properties.flex_direction == "column":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x - child.box_model_v2.margin_size.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x - child.box_model_v2.margin_size.width, cursor.y)

    def v2_move_cursor_from_top_left_child_to_next_child_along_align_axis(self, cursor: Cursor, child, size: Rect, gap = 0):
        if self.properties.flex_direction == "row":
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x, cursor.y + child.box_model_v2.margin_size.height // 2)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x, cursor.y + child.box_model_v2.margin_size.height)
            cursor.move_to(cursor.x + size.width + gap, cursor.y)
        else:
            if self.properties.align_items == "center":
                cursor.move_to(cursor.x + child.box_model_v2.margin_size.width // 2, cursor.y)
            elif self.properties.align_items == "flex_end":
                cursor.move_to(cursor.x + child.box_model_v2.margin_size.width, cursor.y)
            cursor.move_to(cursor.x, cursor.y + size.height + gap)

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

    def gap_between_elements(self, node, i, fixed_gap = 0):
        gap = fixed_gap

        if not gap and node.element_type == ELEMENT_ENUM_TYPE["text"] and \
                self.children_nodes[i + 1].element_type == ELEMENT_ENUM_TYPE["text"] and \
                not node.properties.flex and not self.children_nodes[i + 1].properties.flex and \
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

            if self.properties.flex_direction == "row":
                total_children_width = sum(child.box_model_v2.margin_size.width for child in self.children_nodes)
                available_space = self.box_model_v2.content_size.width - total_children_width
            else:
                total_children_height = sum(child.box_model_v2.margin_size.height for child in self.children_nodes)
                available_space = self.box_model_v2.content_size.height - total_children_height

            fixed_gap = available_space / (len(self.children_nodes) - 1) if len(self.children_nodes) > 1 else 0
        return fixed_gap

    # def render(self, c: SkiaCanvas, cursor: Cursor):
    #     if view_state := self.debugger(c, cursor, True):
    #         return view_state

    #     if self.tree.draggable_node_delta_pos and self.tree.draggable_node == self:
    #         self.box_model.move_delta(
    #             self.tree.draggable_node_delta_pos.x,
    #             self.tree.draggable_node_delta_pos.y,
    #             self.properties.flex_direction,
    #             self.properties.align_items,
    #             self.properties.justify_content
    #         )
    #     else:
    #         self.box_model.position_for_render(
    #             cursor,
    #             self.properties.flex_direction,
    #             self.properties.align_items,
    #             self.properties.justify_content
    #         )

    #     # self.debugger(c, cursor)
    #     self.render_borders(c, cursor)
    #     self.crop_scrollable_region_start(c)
    #     self.adjust_for_scroll_y_start(c)
    #     self.render_background(c, cursor)
    #     # if view_state := self.debugger(c, cursor, True):
    #     #     return view_state
    #     self.move_cursor_to_align_axis_before_children_render(cursor)
    #     # self.debugger(c, cursor)

    #     last_cursor = Point2d(cursor.x, cursor.y)
    #     for i, child in enumerate(self.children_nodes):
    #         if self.debugger_should_continue(c, cursor):
    #             continue

    #         self.move_cursor_to_top_left_child_based_on_align_axis(cursor, child)
    #         # self.debugger(c, cursor, new_color=True)

    #         child_last_cursor = Point2d(cursor.x, cursor.y)
    #         rect = child.render(c, cursor)
    #         cursor.move_to(child_last_cursor.x, child_last_cursor.y)

    #         if i == len(self.children_nodes) - 1:
    #             break

    #         # if self.debugger_should_continue(c, cursor):
    #         #     continue

    #         gap = self.gap_between_elements(child, i)
    #         self.move_cursor_from_top_left_child_to_next_child_along_align_axis(cursor, child, rect, gap)

    #         # self.debugger(c, cursor)

    #     # if view_state := self.debugger(c, cursor, True):
    #     #     return view_state

    #     cursor.move_to(last_cursor.x, last_cursor.y)
    #     # self.debugger(c, cursor)

        # self.adjust_for_scroll_y_end(c)
        self.crop_scrollable_region_end(c)

        return self.box_model.margin_rect