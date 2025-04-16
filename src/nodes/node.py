from typing import Union, Optional
from talon.types import Rect, Point2d
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
import uuid
from ..box_model import BoxModelV2
from ..constants import (
    ELEMENT_ENUM_TYPE,
    NODE_TYPE_MAP,
    LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION,
    LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION,
    CASCADED_PROPERTIES
)
from .component import Component
from ..cursor import Cursor
from ..interfaces import (
    ComponentType,
    NodeType,
    NodeEnumType,
    ElementEnumType,
    TreeType,
    Size2d
)
from ..properties import Properties
from ..utils import sanitize_string
from ..state_manager import state_manager
import weakref

class Node(NodeType):
    def __init__(self,
            element_type: ElementEnumType,
            properties: Properties = None,
        ):
        self.properties: Properties = properties or Properties()
        self.cascaded_properties = set()
        self.guid: str = uuid.uuid4().hex
        self.id: str = sanitize_string(self.properties.id) if self.properties.id else None
        self.is_uniform_border = True
        self.key: str = self.properties.key
        self.node_type: NodeEnumType = NODE_TYPE_MAP[element_type]
        self.element_type: ElementEnumType = element_type
        self.flex_evaluated: Union[int, float] = None
        self.children_nodes = []
        self.is_dirty: bool = False
        self.interactive = False
        self.root_node = None
        self.depth: int = None
        self.z_subindex: int = 0
        self.participates_in_layout: bool = self.properties.position not in ("absolute", "fixed")
        self.box_model: BoxModelV2 = None
        self.node_index_path: list[int] = []
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
        return [node for node in self.children_nodes if node.participates_in_layout]

    @property
    def non_participating_children_nodes(self) -> list[NodeType]:
        return [node for node in self.children_nodes if not node.participates_in_layout]

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
        if self.children_nodes:
            for node in self.children_nodes:
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
                    # Talon's TextArea doesn't support opacity
                    set_opacity = True
                if not self.properties.is_user_set(prop):
                    self.properties.update_property(prop, getattr(parent_node.properties, prop))
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
        if getattr(self.properties, "draggable", None) and getattr(self.tree, "draggable_node_delta_pos", None):
            return
            # This can be improved in the future to support multi-node dragging
            # with meta state
            # top_left_offset = state_manager.get_drag_relative_offset()
            # start_mouse_pos = state_manager.get_mousedown_start_pos()
            # offset = self.tree.render_manager.current_render_task.metadata.get("offset", None)
            # render_mouse_pos = start_mouse_pos + offset
            # top_left = render_mouse_pos - top_left_offset
            # print(f"v2_drag_offset top_left_offset: {top_left_offset}")
            # print(f"v2_drag_offset start_mouse_pos: {start_mouse_pos}")
            # print(f"v2_drag_offset offset: {offset}")
            # print(f"v2_drag_offset render_mouse_pos: {render_mouse_pos}")
            # print(f"v2_drag_offset top_left: {top_left}")

            # cursor.x += offset.x
            # cursor.y += offset.y

            # cursor.x = top_left.x
            # cursor.y = top_left.y

    def _v2_no_reposition(self, offset = None):
        pass

    def v2_reposition(self, offset = None):
        # if getattr(self.properties, "draggable", None):
        #     print('reposition', offset)
        if self.tree.render_manager.is_drag_end() and self.properties.draggable:
            # top_left_offset = state_manager.get_drag_relative_offset()
            # start_mouse_pos = state_manager.get_mousedown_start_pos()
            offset = self.tree.render_manager.current_render_task.metadata.get("mouse_start_offset", None)
            print('offset', offset)
            # print(f"v2_reposition top_left_offset: {top_left_offset}")
            # print(f"v2_reposition start_mouse_pos: {start_mouse_pos}")
            # print(f"v2_reposition offset: {offset}")
            # render_mouse_pos = start_mouse_pos + offset
            # top_left = render_mouse_pos - top_left_offset

            old_pos = self.box_model.margin_pos
            new_pos = self.box_model.margin_pos + offset
            self.box_model.set_top_left(new_pos)
            offset = new_pos - old_pos
        elif offset and self.box_model:
            self.box_model.reposition(offset)
        for child in self.children_nodes:
            child.v2_reposition(offset)

    def v2_scroll_layout(self, offset: Point2d = None):
        node_offset = offset
        if self.properties.is_scrollable() and self.id in self.tree.meta_state.scrollable:
            new_offset = Point2d(
                self.tree.meta_state.scrollable[self.id].offset_x,
                self.tree.meta_state.scrollable[self.id].offset_y
            )
            node_offset = new_offset if not node_offset else node_offset + new_offset
            for child in self.children_nodes:
                child.v2_reposition(node_offset)

        for child in self.children_nodes:
            child.v2_scroll_layout(node_offset)

    def v2_render_borders(self, c: SkiaCanvas):
        self.is_uniform_border = True
        border_spacing = self.box_model.border_spacing
        has_border = border_spacing.left or border_spacing.top or border_spacing.right or border_spacing.bottom
        if has_border:
            self.is_uniform_border = border_spacing.left == border_spacing.top == border_spacing.right == border_spacing.bottom
            # inner_rect = self.box_model.scroll_box_rect if self.box_model.scrollable else self.box_model.padding_rect
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

    def v2_render_background(self, c: SkiaCanvas):
        if self.properties.background_color:
            c.paint.style = c.paint.Style.FILL
            c.paint.color = self.properties.background_color

            # inner_rect = self.box_model.scroll_box_rect if self.box_model.scrollable else self.box_model.padding_rect
            inner_rect = self.box_model.padding_rect

            if self.properties.border_radius and self.is_uniform_border:
                c.draw_rrect(RoundRect.from_rect(inner_rect, x=self.properties.border_radius, y=self.properties.border_radius))
            else:
                c.draw_rect(inner_rect)

    def draw_start(self, c: SkiaCanvas):
        self.v2_render_background(c)
        self.v2_render_borders(c)

    def v2_build_render_list(self):
        self.tree.append_to_render_list(self, self.draw_start)
        for child in self.children_nodes:
            child.v2_build_render_list()

    def v2_render(self, c: SkiaCanvas):
        self.v2_render_background(c)
        self.v2_render_borders(c)

        for child in self.children_nodes:
            child.v2_render(c)

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