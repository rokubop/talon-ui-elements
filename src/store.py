from typing import Optional
from .interfaces import TreeType, NodeType, EffectType, ReactiveStateType

class Store():
    def __init__(self):
        self.trees: list[TreeType] = []
        self.processing_tree: Optional[TreeType] = None
        self.root_nodes: list[NodeType] = []
        self.id_to_node: dict[str, NodeType] = {}
        self.state: dict[str, ReactiveStateType] = {}
        self.staged_effects: list[EffectType] = []

    def synchronize_ids(self):
        new_id_to_node = {}
        for tree in self.trees:
            new_id_to_node.update(tree.meta_state.id_to_node)
        self.id_to_node = new_id_to_node

store = Store()
