from abc import ABC, abstractmethod
from typing import List, Literal, Optional
from .options import UIOptions
from .core.box_model import BoxModelLayout
from .state import state
import uuid

NodeType = Literal['root', 'node', 'leaf']
ElementType = Literal['button', 'text', 'div', 'input', 'screen', 'window']

NODE_TYPE_MAP = {
    'button': 'leaf',
    'text': 'leaf',
    'div': 'node',
    'input': 'leaf',
    'screen': 'root',
    'window': 'root',
}

class Node(ABC):
    def __init__(self,
            element_type: ElementType,
            options: UIOptions = None,
        ):
        self.options: UIOptions = options or UIOptions()
        self.guid: str = uuid.uuid4().hex
        self.id: str = self.options.id
        self.key: str = self.options.key
        self.node_type: NodeType = NODE_TYPE_MAP[element_type]
        self.element_type: ElementType = element_type
        self.builder_node: Node = self if self.node_type == 'root' else None
        self.box_model: BoxModelLayout = None
        self.children_nodes: List['Node'] = []
        self.parent_node: Optional['Node'] = None
        self.is_dirty: bool = False
        self.reactive_state_keys: List[str] = []
        self.depth: int = 0
        state.nodes[self.guid] = self

    def add_child(self, node):
        if isinstance(node, tuple):
            for n in node:
                if n:
                    self.check_invalid_child(n)
                    self.children_nodes.append(n)
                    n.parent_node = self
                    n.depth = self.depth + 1
                    n.builder_node = self.builder_node
        elif node:
            self.check_invalid_child(node)
            self.children_nodes.append(node)
            node.parent_node = self
            node.depth = self.depth + 1
            node.builder_node = self.builder_node

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

    def destroy(self):
        if self.node_type == 'root':
            state.builders.pop(self.guid, None)

        state.nodes.pop(self.guid, None)

        if self.children_nodes:
            for node in list(self.children_nodes):
                node.destroy()

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