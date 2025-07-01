import uuid
import weakref
from typing import Union, Optional
from talon.types import Rect, Point2d
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.imagefilter import ImageFilter
from .component import Component
from ..box_model import BoxModelV2
from ..constants import (
    ELEMENT_ENUM_TYPE,
    NODE_TYPE_MAP,
    LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION,
    LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION,
    CASCADED_PROPERTIES
)
from ..core.state_manager import state_manager
from ..cursor import Cursor
from ..interfaces import (
    NodeType,
    NodeEnumType,
    ElementEnumType,
    TreeType,
    RenderTransforms,
    Size2d,
)
from ..properties import Properties
from ..utils import sanitize_string
import time

STYLE_MAP = {
    "highlight": "highlight_style",
    "disabled": "disabled_style",
    # "hover": "hover_style",
    # "focus": "focus_style",
    # "active": "active_style",
}

class Node(NodeType):
    def __init__(self,
            element_type: ElementEnumType,
            properties: Properties = None,
        ):
        self.properties: Properties = properties or Properties()
        self.cascaded_properties = set()
        self.guid: str = uuid.uuid4().hex
        self.class_name: str = None
        self.id: str = sanitize_string(self.properties.id) if self.properties.id else None
        self.is_uniform_border = True
        self.key: str = self.properties.key
        self.node_type: NodeEnumType = NODE_TYPE_MAP[element_type]
        self.element_type: ElementEnumType = element_type
        self.flex_evaluated: Union[int, float] = None
        self.children_nodes = []
        self.is_dirty: bool = False
        self.disabled: bool = self.properties.disabled or False
        self.interactive = False
        self.interactive_id: str = None
        self.is_svg: bool = False
        self.uses_decoration_render: bool = False
        self.root_node = None
        self.depth: int = None
        self.z_subindex: int = 0
        self.participates_in_layout: bool = self.properties.position not in ("absolute", "fixed")
        self.box_model: BoxModelV2 = None
        self.node_index_path: list[int] = []
        if self.node_type != "root":
            self.inherit_processing_style()
        self.add_properties_to_cascade(properties)

        # Use weakref to avoid circular references
        # Otherwise gc can't collect the objects
        self._tree: Optional[weakref.ReferenceType[TreeType]] = None
        self._parent_node: Optional[weakref.ReferenceType[NodeType]] = None
        self._constraint_nodes: list[weakref.ReferenceType[NodeType]] = []
        self.clip_nodes: list[weakref.ReferenceType[NodeType]] = []
        self.relative_positional_node: weakref.ReferenceType[NodeType] = None

        if self.properties.position == "fixed":
           self.v2_reposition = self._v2_no_reposition

        state_manager.increment_ref_count_nodes()

    def __del__(self):
        state_manager.decrement_ref_count_nodes()

    @property
    def tree(self) -> Optional[TreeType]:
        return self._tree() if self._tree else None

    @tree.setter
    def tree(self, value: TreeType):
        self._tree = weakref.ref(value) if value else None

    @property
    def parent_node(self) -> Optional[NodeType]:
        return self._parent_node() if self._parent_node else None

    @parent_node.setter
    def parent_node(self, value: NodeType):
        self._parent_node = weakref.ref(value) if value else None

    @property
    def constraint_nodes(self) -> list[NodeType]:
        return [node() for node in self._constraint_nodes if node() is not None]

    @property
    def participating_children_nodes(self) -> list[NodeType]:
        return [node for node in self.get_children_nodes() if node.participates_in_layout]

    @property
    def non_participating_children_nodes(self) -> list[NodeType]:
        return [node for node in self.get_children_nodes() if not node.participates_in_layout]

    def get_children_nodes(self) -> list[NodeType]:
        return self.children_nodes

    def add_constraint_node(self, node: NodeType):
        if node:
            self._constraint_nodes.append(weakref.ref(node))

    def remove_constraint_node(self, node: NodeType):
        self._constraint_nodes = [ref for ref in self._constraint_nodes if ref() != node]

    def clear_constraint_nodes(self):
        self._constraint_nodes.clear()

    def add_clip_node(self, node: NodeType):
        if node:
            self.clip_nodes.append(weakref.ref(node))

    def remove_clip_node(self, node: NodeType):
        self.clip_nodes = [ref for ref in self.clip_nodes if ref() != node]

    def clear_clip_nodes(self):
        self.clip_nodes.clear()

    def wrap_component(self, node: NodeType):
        if callable(node):
            node = Component(node)
        return node

    def get_active_variant(self):
        if self.properties.disabled:
            return "disabled", 1.0
        id = self.id or self.interactive_id
        meta_state = self.tree.meta_state

        if id in meta_state.highlighted:
            return "highlight", 1.0
        return None, 0

    def resolve_render_property(self, property_name: str):
        base = getattr(self.properties, property_name)
        variant, t = self.get_active_variant()
        if not variant or t == 0:
            return base

        style_key = STYLE_MAP.get(variant)
        style = getattr(self.properties, style_key, None)

        if not style or property_name not in style:
            return base

        override = style[property_name]

        # future interpolation logic
        # if t == 1.0:
        #     return override

        # if isinstance(base, str) and property_name.endswith("color"):
        #     return interpolate_color(base, override, t)
        # elif isinstance(base, (int, float)) and isinstance(override, (int, float)):
        #     return base + (override - base) * t
        # else:
        #     return override

        return override


    def add_child(self, node):
        if isinstance(node, tuple):
            for n in node:
                if n:
                    self.check_invalid_child(n)
                    n = self.wrap_component(n)
                    self.children_nodes.append(n)
                    if isinstance(n, tuple):
                        raise ValueError(
                            f"Trailing comma detected for ui_elements node. "
                            f"This can happen when a comma is mistakenly added after an element. "
                            f"Remove the trailing comma to fix this issue."
                        )
                    n.parent_node = self
        elif node:
            self.check_invalid_child(node)
            node = self.wrap_component(node)
            self.children_nodes.append(node)
            node.parent_node = self

    def __getitem__(self, children_nodes=None):
        if children_nodes is None:
            children_nodes = []

        if not isinstance(children_nodes, list):
            children_nodes = [children_nodes]

        for node in children_nodes:
            self.add_child(node)

        return self

    def invalidate(self):
        self.is_dirty = True
        children_nodes = self.get_children_nodes()
        if children_nodes:
            for node in children_nodes:
                node.invalidate()

    def add_properties_to_cascade(self, properties: Properties):
        for prop in CASCADED_PROPERTIES:
            if hasattr(properties, prop) and getattr(properties, prop):
                self.cascaded_properties.add(prop)

    def inherit_cascaded_properties(self, parent_node: NodeType):
        if parent_node.cascaded_properties:
            set_opacity = False

            for prop in parent_node.cascaded_properties:
                if prop == "opacity" and not self.element_type == ELEMENT_ENUM_TYPE['input_text']:
                    set_opacity = True
                if not self.properties.is_user_set(prop):
                    if prop == "highlight_style":
                        if self.is_svg:
                            self.properties.update_property(prop, {
                                "stroke": parent_node.properties.highlight_style.get("stroke", None) \
                                    or parent_node.properties.highlight_style.get("color", None),
                            })
                        else:
                            self.properties.update_property(prop, {
                                "color": parent_node.properties.highlight_style.get("color", None),
                            })
                    else:
                        self.properties.update_property(
                            prop,
                            getattr(parent_node.properties, prop),
                            explicitly_set=False
                        )
                    self.cascaded_properties.add(prop)

            if set_opacity:
                self.properties.update_colors_with_opacity()

    def is_fully_clipped_by_scroll(self):
        return False

    def v2_measure_intrinsic_size(self, c):
        self.box_model = BoxModelV2(
            self.properties, Size2d(0, 0),
            self.clip_nodes,
            relative_positional_node=self.relative_positional_node
        )
        return self.box_model.intrinsic_margin_size

    def v2_grow_size(self):
        pass

    def v2_constrain_size(self, available_size: Size2d = None):
        self.box_model.constrain_size(available_size, self.properties.overflow)

    def v2_layout(self, cursor: Cursor) -> Size2d:
        if not self.participates_in_layout:
            self.box_model.position_from_relative_parent(cursor)

        self.box_model.position_for_render(
            cursor,
            self.properties.flex_direction,
            self.properties.align_items,
            self.properties.justify_content
        )

        self.box_model.shift_relative_position(cursor)

        return self.box_model.margin_size

    def v2_drag_offset(self, cursor: Cursor):
        if getattr(self.properties, "draggable", None):
            offset = self.tree.meta_state.get_accumulated_drag_offset(self.id)
            cursor.x += offset.x
            cursor.y += offset.y

    def _v2_no_reposition(self, offset = None):
        pass

    def v2_reposition(self, offset = None):
        if self.tree and self.tree.render_manager.is_drag_end() and self.properties.draggable:
            offset = self.tree.render_manager.current_render_task.metadata.get("mousedown_start_offset", None)
            old_pos = self.box_model.margin_pos
            new_pos = self.box_model.margin_pos + offset
            self.box_model.set_top_left(new_pos)
            offset = new_pos - old_pos
        elif offset and self.box_model:
            self.box_model.reposition(offset)
        for child in self.get_children_nodes():
            child.v2_reposition(offset)

    def v2_scroll_layout(self, offset: Point2d = None):
        node_offset = offset
        if self.properties.is_scrollable() and self.id in self.tree.meta_state.scrollable:
            new_offset = Point2d(
                self.tree.meta_state.scrollable[self.id].offset_x,
                self.tree.meta_state.scrollable[self.id].offset_y
            )
            node_offset = new_offset if not node_offset else node_offset + new_offset
            for child in self.get_children_nodes():
                child.v2_reposition(node_offset)

        for child in self.get_children_nodes():
            child.v2_scroll_layout(node_offset)

    def v2_render_borders(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.is_uniform_border = True
        border_spacing = self.box_model.border_spacing
        has_border = border_spacing.left or border_spacing.top or border_spacing.right or border_spacing.bottom
        if has_border:
            self.is_uniform_border = border_spacing.left == border_spacing.top == border_spacing.right == border_spacing.bottom
            # inner_rect = self.box_model.scroll_box_rect if self.box_model.scrollable else self.box_model.padding_rect

            if transforms and transforms.offset:
                inner_rect = self.box_model.padding_rect.copy()
                inner_rect = Rect(
                    inner_rect.x + transforms.offset.x,
                    inner_rect.y + transforms.offset.y,
                    inner_rect.width,
                    inner_rect.height
                )
            else:
                inner_rect = self.box_model.padding_rect

            border_color = self.resolve_render_property("border_color")
            if self.is_uniform_border:
                border_width = border_spacing.left
                c.paint.color = border_color
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
                c.paint.color = border_color
                c.paint.style = c.paint.Style.STROKE
                b_rect, p_rect = self.box_model.border_rect, inner_rect

                if transforms and transforms.offset:
                    b_rect = Rect(
                        b_rect.x + transforms.offset.x,
                        b_rect.y + transforms.offset.y,
                        b_rect.width,
                        b_rect.height
                    )

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

    def v2_render_drop_shadow(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        if self.properties.drop_shadow:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.drop_shadow[4]

            c.paint.imagefilter = ImageFilter.drop_shadow(
                self.properties.drop_shadow[0],
                self.properties.drop_shadow[1],
                self.properties.drop_shadow[2],
                self.properties.drop_shadow[3],
                self.properties.drop_shadow[4],
            )

            inner_rect = self.box_model.padding_rect

            if transforms and transforms.offset:
                inner_rect = Rect(
                    inner_rect.x + transforms.offset.x,
                    inner_rect.y + transforms.offset.y,
                    inner_rect.width,
                    inner_rect.height
                )

            if self.properties.border_radius and self.is_uniform_border:
                c.draw_rrect(RoundRect.from_rect(inner_rect, x=self.properties.border_radius, y=self.properties.border_radius))
            else:
                c.draw_rect(inner_rect)
            c.paint.imagefilter = None

    def v2_render_background(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        background_color = self.resolve_render_property("background_color")
        if background_color:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = background_color

            inner_rect = self.box_model.padding_rect

            if transforms and transforms.offset:
                inner_rect = Rect(
                    inner_rect.x + transforms.offset.x,
                    inner_rect.y + transforms.offset.y,
                    inner_rect.width,
                    inner_rect.height
                )

            if self.properties.border_radius and self.is_uniform_border:
                c.draw_rrect(RoundRect.from_rect(inner_rect, x=self.properties.border_radius, y=self.properties.border_radius))
            else:
                c.draw_rect(inner_rect)

    def draw_start(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_render_background(c, transforms)
        self.v2_render_borders(c, transforms)

    def v2_build_render_list(self):
        if not self.uses_decoration_render:
            self.tree.append_to_render_list(self, self.draw_start)
            for child in self.get_children_nodes():
                child.v2_build_render_list()

    def v2_render_decorator(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_render_background(c, transforms)
        self.v2_render_borders(c, transforms)

        for child in self.get_children_nodes():
            child.v2_render_decorator(c, transforms)

    def v2_render(self, c: SkiaCanvas, transforms: RenderTransforms = None):
        self.v2_render_background(c, transforms)
        self.v2_render_borders(c, transforms)

        for child in self.get_children_nodes():
            child.v2_render(c, transforms)

    def destroy(self):
        for node in self.children_nodes:
            node.destroy()
        if self.box_model:
            self.box_model.gc()
        self.properties.gc()
        self.children_nodes.clear()
        self.clear_constraint_nodes()
        self.clear_clip_nodes()
        self.relative_positional_node = None
        self.parent_node = None
        self.tree = None

    def show(self):
        raise NotImplementedError(f"DeprecationWarning: {self.element_type} cannot use .show(). {LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION}")

    def hide(self):
        raise NotImplementedError(f"DeprecationWarning: {self.element_type} cannot use .hide(). {LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION}")

    def check_invalid_child(self, c):
        if isinstance(c, str):
            raise TypeError(
                "Invalid child type: str. Use `ui_elements` `text` element."
            )

    def inherit_processing_style(self):
        if style := state_manager.get_processing_style():
            if new_properties := style.get(self):
                self.properties.inherit_kwarg_properties(new_properties)