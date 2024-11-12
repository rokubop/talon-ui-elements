from abc import ABC
from typing import List, Literal, Optional
from ..options import UIOptions
from ..core.box_model import BoxModelLayout
from ..node_manager import node_manager
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
        self.box_model: BoxModelLayout = None
        self.children_nodes: List['Node'] = []
        self.parent_node: Optional['Node'] = None
        self.is_dirty: bool = False
        self.reactive_state_keys: List[str] = []
        self.root_node = None
        self.depth: int = None

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