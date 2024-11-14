from abc import ABC
from typing import List, Literal, Optional
from ..options import UIOptions
from ..core.box_model import BoxModelLayout
from ..node_manager import node_manager
from ..state_manager import state_manager
from ..interfaces import NodeType, NodeEnumType, ElementEnumType
import uuid

NODE_TYPE_MAP = {
    'button': 'leaf',
    'text': 'leaf',
    'div': 'node',
    'input': 'leaf',
    'screen': 'root',
    'window': 'root',
    'component': 'component'
}

class Node(NodeType):
    def __init__(self,
            element_type: ElementEnumType,
            options: UIOptions = None,
        ):
        self.options: UIOptions = options or UIOptions()
        self.guid: str = uuid.uuid4().hex
        self.id: str = self.options.id
        self.key: str = self.options.key
        self.node_type: NodeEnumType = NODE_TYPE_MAP[element_type]
        self.element_type: ElementEnumType = element_type
        self.box_model: BoxModelLayout = None
        self.children_nodes = []
        self.parent_node = None
        self.is_dirty: bool = False
        self.root_node = None
        self.depth: int = None
        self.component_node = state_manager.get_active_component_node()

    def add_child(self, node):
        if isinstance(node, tuple):
            for n in node:
                if n:
                    self.check_invalid_child(n)
                    self.children_nodes.append(n)
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

        if self.node_type == 'root':
            node_manager.init_node_hierarchy(self, self)

        return self

    def invalidate(self):
        self.is_dirty = True
        if self.children_nodes:
            for node in self.children_nodes:
                node.invalidate()

    def destroy(self):
        node_manager.remove_node(self)

    def show(self):
        raise NotImplementedError(f"{self.element_type} cannot use .show() directly.")

    def hide(self):
        raise NotImplementedError(f"{self.element_type} cannot use .hide() directly.")

    def check_invalid_child(self, c):
        if isinstance(c, str):
            raise TypeError(
                "Invalid child type: str. Use `ui_elements` `text` element."
            )

    # @abstractmethod
    # def render(self):
    #     pass

    # @abstractmethod
    # def virtual_render(self):
    #     pass