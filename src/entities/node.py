import uuid
from ..constants import NODE_TYPE_MAP
from ..core.box_model import BoxModelLayout
from ..interfaces import NodeType, NodeEnumType, ElementEnumType, TreeType
from ..options import UIOptions

class Node(NodeType):
    def __init__(self,
            element_type: ElementEnumType,
            options: UIOptions = None,
        ):
        self.options: UIOptions = options or UIOptions()
        self.guid: str = uuid.uuid4().hex
        print(f"element type: {element_type}")
        print(f"node options: {vars(self.options)}")
        self.id: str = self.options.id
        self.key: str = self.options.key
        self.node_type: NodeEnumType = NODE_TYPE_MAP[element_type]
        self.element_type: ElementEnumType = element_type
        self.box_model: BoxModelLayout = None
        self.tree: TreeType
        self.children_nodes = []
        self.constraint_nodes = []
        self.parent_node = None
        self.is_dirty: bool = False
        self.root_node = None
        self.depth: int = None

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

    def destroy(self):
        pass

    def show(self):
        raise NotImplementedError(f"{self.element_type} cannot use .show() directly.")

    def hide(self):
        raise NotImplementedError(f"{self.element_type} cannot use .hide() directly.")

    def check_invalid_child(self, c):
        if isinstance(c, str):
            raise TypeError(
                "Invalid child type: str. Use `ui_elements` `text` element."
            )