from typing import Union
import uuid
from ..box_model import BoxModelLayout
from ..constants import (
    ELEMENT_ENUM_TYPE,
    NODE_TYPE_MAP,
    LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION,
    LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION,
    CASCADED_PROPERTIES
)
from ..interfaces import NodeType, NodeEnumType, ElementEnumType, TreeType
from ..properties import Properties
from ..utils import sanitize_string

class Node(NodeType):
    def __init__(self,
            element_type: ElementEnumType,
            properties: Properties = None,
        ):
        self.properties: Properties = properties or Properties()
        self.cascaded_properties = set()
        self.guid: str = uuid.uuid4().hex
        self.id: str = sanitize_string(self.properties.id) if self.properties.id else None
        self.key: str = self.properties.key
        self.node_type: NodeEnumType = NODE_TYPE_MAP[element_type]
        self.element_type: ElementEnumType = element_type
        self.flex_evaluated: Union[int, float] = None
        self.box_model: BoxModelLayout = None
        self.tree: TreeType
        self.children_nodes = []
        self.constraint_nodes = []
        self.parent_node = None
        self.is_dirty: bool = False
        self.interactive = False
        self.root_node = None
        self.depth: int = None
        self.add_properties_to_cascade(properties)

    def add_child(self, node):
        if isinstance(node, tuple):
            for n in node:
                if n:
                    self.check_invalid_child(n)
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

    def destroy(self):
        pass

    def show(self):
        raise NotImplementedError(f"DeprecationWarning: {self.element_type} cannot use .show(). {LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION}")

    def hide(self):
        raise NotImplementedError(f"DeprecationWarning: {self.element_type} cannot use .hide(). {LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION}")

    def check_invalid_child(self, c):
        if isinstance(c, str):
            raise TypeError(
                "Invalid child type: str. Use `ui_elements` `text` element."
            )