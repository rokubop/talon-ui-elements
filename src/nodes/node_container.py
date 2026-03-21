from itertools import cycle
from typing import List
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from .node import Node
from ..border_radius import draw_manual_rounded_rect_path
from ..box_model import BoxModelV2
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_SCROLL_BAR_TRACK_COLOR, DEFAULT_SCROLL_BAR_THUMB_COLOR
from ..cursor import Cursor
from ..interfaces import NodeContainerType, Size2d, NodeType, RenderItem, RenderTransforms
from ..properties import Properties
from ..utils import adjust_color_alpha

class NodeContainer(Node, NodeContainerType):
    def __init__(self, element_type, properties: Properties = None):
        super().__init__(element_type=element_type, properties=properties)
        if self.properties.on_click:
            self.on_click = self.properties.on_click
            self.interactive = True
            self.is_hovering = False
        self.justify_between_gaps = None
        self.wrap_lines = None
        self.wrap_line_secondary_sizes = None
        self.debug_number = 0
        self.debug_color = "red"
        self.debug_colors = iter(cycle(["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]))

    @property
    def is_flex_wrap(self):
        fw = self.properties.flex_wrap
        return fw is True or fw == "wrap"

    def render_scroll_bar(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        scrollable = self.tree.meta_state.scrollable.get(self.id, None)
        if not scrollable:
            return

        # Y scrollbar
        if self.box_model.scroll_bar_thumb_rect:
            scroll_bar_track_rect = self.box_model.scroll_bar_track_rect.copy()
            scroll_bar_thumb_rect = self.box_model.scroll_bar_thumb_rect.copy()

            if transforms and transforms.offset:
                scroll_bar_track_rect.x += transforms.offset.x
                scroll_bar_track_rect.y += transforms.offset.y
                scroll_bar_thumb_rect.x += transforms.offset.x
                scroll_bar_thumb_rect.y += transforms.offset.y

            c.paint.style = c.paint.Style.FILL
            c.paint.color = DEFAULT_SCROLL_BAR_TRACK_COLOR
            c.draw_rect(scroll_bar_track_rect)

            thumb_color = DEFAULT_SCROLL_BAR_THUMB_COLOR
            if self.tree.meta_state.is_scrollbar_dragging(self.id) and self.tree.meta_state.scrollbar_dragging_axis == "y":
                thumb_color = adjust_color_alpha(thumb_color, 30)
            elif self.tree.meta_state.is_scrollbar_hovered(self.id, axis="y"):
                thumb_color = adjust_color_alpha(thumb_color, 15)

            c.paint.color = thumb_color
            c.draw_rect(scroll_bar_thumb_rect)

        # X scrollbar
        if self.box_model.scroll_bar_x_thumb_rect:
            scroll_bar_x_track_rect = self.box_model.scroll_bar_x_track_rect.copy()
            scroll_bar_x_thumb_rect = self.box_model.scroll_bar_x_thumb_rect.copy()

            if transforms and transforms.offset:
                scroll_bar_x_track_rect.x += transforms.offset.x
                scroll_bar_x_track_rect.y += transforms.offset.y
                scroll_bar_x_thumb_rect.x += transforms.offset.x
                scroll_bar_x_thumb_rect.y += transforms.offset.y

            c.paint.style = c.paint.Style.FILL
            c.paint.color = DEFAULT_SCROLL_BAR_TRACK_COLOR
            c.draw_rect(scroll_bar_x_track_rect)

            thumb_color = DEFAULT_SCROLL_BAR_THUMB_COLOR
            if self.tree.meta_state.is_scrollbar_dragging(self.id) and self.tree.meta_state.scrollbar_dragging_axis == "x":
                thumb_color = adjust_color_alpha(thumb_color, 30)
            elif self.tree.meta_state.is_scrollbar_hovered(self.id, axis="x"):
                thumb_color = adjust_color_alpha(thumb_color, 15)

            c.paint.color = thumb_color
            c.draw_rect(scroll_bar_x_thumb_rect)

    def v2_measure_children_intrinsic_size(self, c: SkiaCanvas) -> Size2d:
        children_accumulated_size = Size2d(0, 0)
        is_row = self.properties.flex_direction == "row"
        primary_axis = "width" if is_row else "height"
        secondary_axis = "height" if is_row else "width"
        participating_children_nodes = self.participating_children_nodes

        if participating_children_nodes:
            child_sizes = []
            for i, child in enumerate(participating_children_nodes):
                margin_size = child.v2_measure_intrinsic_size(c)
                child_sizes.append(margin_size)

            fixed_gap = self.determine_intrinsic_fixed_gap()

            # Flex wrap: split into lines if explicit primary size is known
            if self.is_flex_wrap:
                explicit_primary = self.properties.width if is_row else self.properties.height
                if explicit_primary and isinstance(explicit_primary, (int, float)) and explicit_primary > 0:
                    props = self.properties
                    pad = props.padding
                    border = props.border
                    pad_start = pad.left if is_row else pad.top
                    pad_end = pad.right if is_row else pad.bottom
                    border_start = border.left if is_row else border.top
                    border_end = border.right if is_row else border.bottom
                    available_primary = explicit_primary - pad_start - pad_end - border_start - border_end

                    lines = []
                    current_line = []
                    current_line_primary = 0

                    for i, size in enumerate(child_sizes):
                        child_primary = getattr(size, primary_axis)
                        gap = fixed_gap if current_line else 0

                        if current_line and current_line_primary + gap + child_primary > available_primary:
                            lines.append(current_line)
                            current_line = [(i, size)]
                            current_line_primary = child_primary
                        else:
                            current_line_primary += gap + child_primary
                            current_line.append((i, size))

                    if current_line:
                        lines.append(current_line)

                    max_line_primary = 0
                    total_secondary = 0
                    for line in lines:
                        line_primary = sum(getattr(s, primary_axis) for _, s in line)
                        line_primary += fixed_gap * max(0, len(line) - 1)
                        max_line_primary = max(max_line_primary, line_primary)

                        line_secondary = max(getattr(s, secondary_axis) for _, s in line)
                        total_secondary += line_secondary

                    if len(lines) > 1:
                        total_secondary += fixed_gap * (len(lines) - 1)

                    setattr(children_accumulated_size, primary_axis, max_line_primary)
                    setattr(children_accumulated_size, secondary_axis, total_secondary)
                    return children_accumulated_size

            # Standard single-line accumulation
            for i, size in enumerate(child_sizes):
                setattr(
                    children_accumulated_size,
                    secondary_axis,
                    max(
                        getattr(children_accumulated_size, secondary_axis),
                        getattr(size, secondary_axis)
                    )
                )
                setattr(
                    children_accumulated_size,
                    primary_axis,
                    getattr(children_accumulated_size, primary_axis) + getattr(size, primary_axis)
                )

            for i, child in enumerate(participating_children_nodes):
                if i != len(participating_children_nodes) - 1:
                    gap = self.gap_between_elements(child, i, fixed_gap)
                    setattr(
                        children_accumulated_size,
                        primary_axis,
                        getattr(children_accumulated_size, primary_axis) + gap
                    )

        return children_accumulated_size

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        """
        First step in the layout process. Calculates the intrinsic size.
        Determines natural width/height based on content or user-defined size.
        """
        children_accumulated_size = self.v2_measure_children_intrinsic_size(c)

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

        # Wrapped layout: skip counter-axis stretch and primary flex growth.
        # Children keep their intrinsic sizes; constraint phase handles line-breaking.
        if self.is_flex_wrap:
            for child in self.participating_children_nodes:
                child.box_model.resolve_max_percent(self.box_model.calculated_content_size)
                child.v2_grow_size()
            return

        for i, child in enumerate(self.participating_children_nodes):
            if (all_growable_counter_axis and not self._child_has_cross_axis_auto_margin(child)) or child.properties.align_self == "stretch" or \
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
                    target = self.box_model.calculated_content_size.height
                    if child.box_model.height_percent:
                        pct = float(child.box_model.height_percent.replace("%", "")) / 100
                        target = target * pct
                    grow_content = not child.properties.overflow.scrollable_y
                    child.box_model.grow_calculated_height_to(target, grow_content)
                elif self.properties.flex_direction == "column" and not child.box_model.fixed_width:
                    target = self.box_model.calculated_content_size.width
                    if child.box_model.width_percent:
                        pct = float(child.box_model.width_percent.replace("%", "")) / 100
                        target = target * pct
                    grow_content = not child.properties.overflow.scrollable_x
                    child.box_model.grow_calculated_width_to(target, grow_content)

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
                    # Cap percentage-based children to their percentage of parent
                    if child.flex_evaluated and not child.properties.flex and child.box_model and child.box_model.margin_size:
                        pct_str = child.properties.height if flex_direction == "column" else child.properties.width
                        if isinstance(pct_str, str) and "%" in pct_str:
                            pct = float(pct_str.replace("%", "")) / 100
                            parent_size = self.box_model.calculated_content_size.height if flex_direction == "column" else self.box_model.calculated_content_size.width
                            current_size = child.box_model.margin_size.height if flex_direction == "column" else child.box_model.margin_size.width
                            max_additional = parent_size * pct - current_size
                            additional_size = min(additional_size, max(0, max_additional))
                    grow_function(child, additional_size)
                if flex_direction == "row":
                    self.box_model.maximize_content_children_width()
                elif flex_direction == "column":
                    self.box_model.maximize_content_children_height()

        for child in self.participating_children_nodes:
            child.box_model.resolve_max_percent(self.box_model.calculated_content_size)
            child.v2_grow_size()

    def v2_constrain_size(self, available_size: Size2d = None) -> bool:
        content_constraint_size = self.box_model.constrain_size(available_size, self.properties.overflow)
        children_accumulated_size = Size2d(0, 0)
        is_row = self.properties.flex_direction == "row"
        primary_axis = "width" if is_row else "height"
        secondary_axis = "height" if is_row else "width"

        if not self.participating_children_nodes:
            self.wrap_lines = None
            return

        participating_children_nodes = self.participating_children_nodes

        # Flex wrap: split children into lines based on available primary axis space
        if self.is_flex_wrap and content_constraint_size:
            available_primary = getattr(content_constraint_size, primary_axis)
            if available_primary is not None:
                fixed_gap = self.determine_intrinsic_fixed_gap()
                lines = []
                current_line = []
                current_line_primary = 0

                for child in participating_children_nodes:
                    child.v2_constrain_size(content_constraint_size.copy())
                    child_primary = getattr(child.box_model.margin_size, primary_axis)
                    gap = fixed_gap if current_line else 0

                    if current_line and current_line_primary + gap + child_primary > available_primary:
                        lines.append(current_line)
                        current_line = [child]
                        current_line_primary = child_primary
                    else:
                        current_line_primary += gap + child_primary
                        current_line.append(child)

                if current_line:
                    lines.append(current_line)

                self.wrap_lines = lines

                # Calculate per-line secondary sizes and totals
                self.wrap_line_secondary_sizes = []
                max_primary = 0
                total_secondary = 0
                for line in lines:
                    line_primary = sum(getattr(c.box_model.margin_size, primary_axis) for c in line)
                    line_primary += fixed_gap * max(0, len(line) - 1)
                    max_primary = max(max_primary, line_primary)

                    line_secondary = max(getattr(c.box_model.margin_size, secondary_axis) for c in line)
                    self.wrap_line_secondary_sizes.append(line_secondary)
                    total_secondary += line_secondary

                if len(lines) > 1:
                    total_secondary += fixed_gap * (len(lines) - 1)

                # Grow container secondary axis if wrapped content is taller
                current_secondary = getattr(self.box_model.content_children_size, secondary_axis)
                if total_secondary > current_secondary:
                    diff = total_secondary - current_secondary
                    if is_row:
                        self.box_model.margin_size.height += diff
                        self.box_model.border_size.height += diff
                        self.box_model.padding_size.height += diff
                        self.box_model.content_size.height += diff
                        self.box_model.grow_calculated_height_by(diff)
                    else:
                        self.box_model.margin_size.width += diff
                        self.box_model.border_size.width += diff
                        self.box_model.padding_size.width += diff
                        self.box_model.content_size.width += diff
                        self.box_model.grow_calculated_width_by(diff)

                setattr(self.box_model.content_children_size, primary_axis, max_primary)
                setattr(self.box_model.content_children_size, secondary_axis, total_secondary)
                return

        self.wrap_lines = None

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

        if content_constraint_size:
            new_available_size = content_constraint_size.copy()

            # Reserve space for non-flex children so flex children don't consume
            # all available space. Without this, a flex child with large intrinsic
            # content (e.g. scrollable text) would constrain to the full available
            # height, leaving 0 for non-flex siblings like a bottom bar.
            # Track remaining unprocessed non-flex intrinsic size so we don't
            # double-subtract for non-flex children already consumed from available.
            available_primary = getattr(new_available_size, primary_axis)
            remaining_non_flex_intrinsic = 0
            if available_primary is not None:
                for child in participating_children_nodes:
                    if not child.properties.flex:
                        remaining_non_flex_intrinsic += getattr(
                            child.box_model.intrinsic_margin_size, primary_axis
                        )

            for child in participating_children_nodes:
                child_available = new_available_size
                # Resolve primary-axis percentage to a concrete constraint
                pct_prop = child.properties.width if is_row else child.properties.height
                if isinstance(pct_prop, str) and "%" in pct_prop:
                    pct = float(pct_prop.replace("%", "")) / 100
                    parent_primary = getattr(content_constraint_size, primary_axis)
                    if parent_primary is not None:
                        child_available = new_available_size.copy()
                        setattr(child_available, primary_axis, int(parent_primary * pct))
                elif child.properties.flex and available_primary is not None:
                    # Cap flex child's available space to leave room for
                    # not-yet-processed non-flex siblings
                    current_available = getattr(new_available_size, primary_axis)
                    if current_available is not None and remaining_non_flex_intrinsic > 0:
                        flex_available = max(0, current_available - remaining_non_flex_intrinsic)
                        child_available = new_available_size.copy()
                        setattr(child_available, primary_axis, flex_available)

                if child.properties.flex_shrink == 0:
                    no_shrink_size = child_available.copy()
                    if is_row:
                        no_shrink_size.width = None
                    else:
                        no_shrink_size.height = None
                    child.v2_constrain_size(no_shrink_size)
                else:
                    child.v2_constrain_size(child_available)
                if is_row and new_available_size.width != None:
                    new_available_size.width = max(0, new_available_size.width - child.box_model.margin_size.width)
                elif not is_row and new_available_size.height != None:
                    new_available_size.height = max(0, new_available_size.height - child.box_model.margin_size.height)
                # Decrement remaining reservation as non-flex children are processed
                if not child.properties.flex and available_primary is not None:
                    remaining_non_flex_intrinsic = max(0,
                        remaining_non_flex_intrinsic - getattr(
                            child.box_model.margin_size, primary_axis
                        ))
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

        scrollable = self.tree.meta_state.scrollable.get(self.id, None) if self.tree else None
        if scrollable:
            scrollable.reevaluate(self)
            self.box_model.adjust_scroll_y(scrollable.offset_y)
            self.box_model.adjust_scroll_x(scrollable.offset_x)

        last_cursor = Point2d(cursor.x, cursor.y)

        if self.wrap_lines:
            is_row = self.properties.flex_direction == "row"
            gap = self.properties.gap or 0
            line_x = self.box_model.content_pos.x
            line_y = self.box_model.content_pos.y

            self.box_model.shift_relative_position(cursor)

            for line_idx, line in enumerate(self.wrap_lines):
                cursor.move_to(line_x, line_y)

                for i, child in enumerate(line):
                    child_cursor = Point2d(cursor.x, cursor.y)
                    size = child.v2_layout(cursor)
                    cursor.move_to(child_cursor.x, child_cursor.y)

                    if i < len(line) - 1:
                        if is_row:
                            cursor.move_to(cursor.x + size.width + gap, cursor.y)
                        else:
                            cursor.move_to(cursor.x, cursor.y + size.height + gap)

                if line_idx < len(self.wrap_lines) - 1:
                    line_secondary = self.wrap_line_secondary_sizes[line_idx]
                    if is_row:
                        line_y += line_secondary + gap
                    else:
                        line_x += line_secondary + gap
        else:
            self.v2_move_cursor_to_align_axis_before_children_render(cursor)

            self.box_model.shift_relative_position(cursor)
            auto_margin_offsets = self._resolve_auto_margins()
            fixed_gap = self.determine_layout_fixed_gap()
            is_row = self.properties.flex_direction == "row"
            for i, child in enumerate(self.participating_children_nodes):
                self.v2_move_cursor_to_top_left_child_based_on_align_axis(cursor, child)

                # Apply auto margin offsets before positioning
                if auto_margin_offsets and i in auto_margin_offsets:
                    main_offset, cross_offset, _ = auto_margin_offsets[i]
                    if is_row:
                        cursor.move_to(cursor.x + main_offset, cursor.y + cross_offset)
                    else:
                        cursor.move_to(cursor.x + cross_offset, cursor.y + main_offset)

                child_last_cursor = Point2d(cursor.x, cursor.y)
                size = child.v2_layout(cursor)
                cursor.move_to(child_last_cursor.x, child_last_cursor.y)

                if i == len(self.participating_children_nodes) - 1:
                    break

                # Apply auto margin advance after positioning (for auto_right/auto_bottom)
                if auto_margin_offsets and i in auto_margin_offsets:
                    _, _, main_advance = auto_margin_offsets[i]
                    if is_row:
                        cursor.move_to(cursor.x + main_advance, cursor.y)
                    else:
                        cursor.move_to(cursor.x, cursor.y + main_advance)

                gap = self.gap_between_elements(child, i, fixed_gap)
                self.v2_move_cursor_from_top_left_child_to_next_child_along_align_axis(cursor, child, size, gap)

        cursor.move_to(last_cursor.x, last_cursor.y)
        return self.box_model.margin_size

    def draw_start(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_render_drop_shadow(c, transforms)
        self.v2_render_borders(c, transforms)
        self.v2_crop_start(c, transforms)
        self.v2_render_background(c, transforms)

    def draw_end(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_crop_end(c, transforms)
        self.render_scroll_bar(c, transforms)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(
                node=self,
                draw=self.draw_start
            )

            for child in self.get_children_nodes():
                child.v2_build_render_list()

            self.tree.append_to_render_list(
                node=self,
                draw=self.draw_end
            )

    def v2_render_decorator(self, c, transforms: RenderTransforms = None):
        if self.tree:
            self.v2_render_borders(c, transforms)
            self.v2_render_background(c, transforms)
            for child in self.get_children_nodes():
                child.v2_render_decorator(c, transforms)

    def v2_render(self, c, transforms: RenderTransforms = None):
        if self.tree:
            self.v2_render_borders(c, transforms)
            self.v2_crop_start(c, transforms)
            self.v2_render_background(c, transforms)
            for child in self.get_children_nodes():
                child.v2_render(c, transforms)
            self.v2_crop_end(c, transforms)
            self.render_scroll_bar(c, transforms)

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

    def v2_adjust_for_scroll_x_start(self):
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model.adjust_scroll_x(self.tree.meta_state.scrollable[self.id].offset_x)

    def v2_adjust_for_scroll_x_end(self):
        if self.tree.meta_state.scrollable.get(self.id, None):
            self.box_model.adjust_scroll_x(-self.tree.meta_state.scrollable[self.id].offset_x)

    def v2_crop_start(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        """Apply all clipping regions (ancestors + self) from pre-computed cache."""
        if not self.clip_regions_cache:
            return

        for rect, border_radius in self.clip_regions_cache:
            c.save()

            if transforms and transforms.offset:
                rect = rect.copy()
                rect.x += transforms.offset.x
                rect.y += transforms.offset.y

            if border_radius:
                self._clip_with_border_radius(c, rect, border_radius)
            else:
                c.clip_rect(rect)

    def v2_crop_end(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        """Restore all clipping regions from cache."""
        if self.clip_regions_cache:
            for _ in range(len(self.clip_regions_cache)):
                c.restore()

    def _clip_with_border_radius(self, c: SkiaCanvas, rect: Rect, border_radius):
        """Clip canvas to a rounded rectangle boundary"""
        if border_radius.is_uniform():
            c.clip_rrect(RoundRect.from_rect(rect, x=border_radius.top_left, y=border_radius.top_left))
        else:
            path = draw_manual_rounded_rect_path(rect, border_radius)
            c.clip_path(path)

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

    def _child_has_cross_axis_auto_margin(self, child):
        """Check if child has auto margin on the cross axis."""
        margin = child.properties.margin
        if not margin.has_auto:
            return False
        if self.properties.flex_direction == "row":
            return margin.auto_top or margin.auto_bottom
        return margin.auto_left or margin.auto_right

    def v2_move_cursor_to_top_left_child_based_on_align_axis(self, cursor: Cursor, child):
        # Skip align_items adjustment for children with cross-axis auto margins.
        # Reset cursor to content_pos on the cross axis so auto margins resolve
        # relative to the full content area, not the aligned content_children area.
        if self._child_has_cross_axis_auto_margin(child):
            if self.properties.flex_direction == "row":
                cursor.move_to(cursor.x, self.box_model.content_pos.y)
            elif self.properties.flex_direction == "column":
                cursor.move_to(self.box_model.content_pos.x, cursor.y)
            return

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
        if self._child_has_cross_axis_auto_margin(child):
            # Restore cursor to aligned position for next sibling
            align = self.properties.align_items
            if self.properties.flex_direction == "row":
                # Reset cross axis to aligned base position
                base_y = self.box_model.content_children_pos.y
                if align == "center":
                    base_y += self.box_model.content_children_size.height // 2
                elif align == "flex_end":
                    base_y += self.box_model.content_children_size.height
                cursor.move_to(cursor.x + size.width + gap, base_y)
            else:
                base_x = self.box_model.content_children_pos.x
                if align == "center":
                    base_x += self.box_model.content_children_size.width // 2
                elif align == "flex_end":
                    base_x += self.box_model.content_children_size.width
                cursor.move_to(base_x, cursor.y + size.height + gap)
            return

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

    def _resolve_auto_margins(self):
        """Resolve auto margins for children. Returns a dict of child index -> (main_offset, cross_offset)
        or None if no children have auto margins."""
        children = self.participating_children_nodes
        if not children:
            return None

        has_any_auto = False
        for child in children:
            if child.properties.margin.has_auto:
                has_any_auto = True
                break
        if not has_any_auto:
            return None

        is_row = self.properties.flex_direction == "row"
        content_main = self.box_model.content_size.width if is_row else self.box_model.content_size.height
        content_cross = self.box_model.content_size.height if is_row else self.box_model.content_size.width

        # Calculate total consumed main-axis space (children + gaps)
        fixed_gap = self.determine_layout_fixed_gap()
        total_children_main = 0
        total_main_auto_count = 0
        for i, child in enumerate(children):
            total_children_main += child.box_model.margin_size.width if is_row else child.box_model.margin_size.height
            if i < len(children) - 1:
                total_children_main += self.gap_between_elements(child, i, fixed_gap)
            margin = child.properties.margin
            if is_row:
                if margin.auto_left:
                    total_main_auto_count += 1
                if margin.auto_right:
                    total_main_auto_count += 1
            else:
                if margin.auto_top:
                    total_main_auto_count += 1
                if margin.auto_bottom:
                    total_main_auto_count += 1

        remaining_main = max(0, content_main - total_children_main)
        per_main_auto = remaining_main / total_main_auto_count if total_main_auto_count > 0 else 0

        offsets = {}
        for i, child in enumerate(children):
            margin = child.properties.margin
            if not margin.has_auto:
                continue

            main_offset = 0
            cross_offset = 0

            # Main axis auto margins
            if is_row:
                if margin.auto_left:
                    main_offset += per_main_auto
                # auto_right shifts subsequent children, not this one's position
                # but we need to track it for cursor advancement
            else:
                if margin.auto_top:
                    main_offset += per_main_auto

            # Cross axis auto margins
            child_cross = child.box_model.margin_size.height if is_row else child.box_model.margin_size.width
            remaining_cross = max(0, content_cross - child_cross)
            if is_row:
                if margin.auto_top and margin.auto_bottom:
                    cross_offset = remaining_cross / 2
                elif margin.auto_top:
                    cross_offset = remaining_cross
                # auto_bottom only: no offset needed (already at top)
            else:
                if margin.auto_left and margin.auto_right:
                    cross_offset = remaining_cross / 2
                elif margin.auto_left:
                    cross_offset = remaining_cross
                # auto_right only: no offset needed (already at left)

            # Calculate total main advance extra (for cursor movement after this child)
            main_advance = 0
            if is_row and margin.auto_right:
                main_advance = per_main_auto
            elif not is_row and margin.auto_bottom:
                main_advance = per_main_auto

            offsets[i] = (int(main_offset), int(cross_offset), int(main_advance))

        return offsets

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