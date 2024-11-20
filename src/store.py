from typing import Optional, TypedDict, Tuple
from .interfaces import TreeType, NodeType, EffectType, ReactiveStateType

class MouseState(TypedDict):
    hovered_id: Optional[str]
    mousedown_start_id: Optional[str]
    mousedown_start_pos: Optional[Tuple[int, int]]
    drag_active: bool
    drag_window_relative_offset: Optional[Tuple[int, int]]

class Store():
    def __init__(self):
        self.trees: list[TreeType] = []
        self.processing_tree: Optional[TreeType] = None
        self.root_nodes: list[NodeType] = []
        self.id_to_node: dict[str, NodeType] = {}
        self.reactive_state: dict[str, ReactiveStateType] = {}
        self.staged_effects: list[EffectType] = []
        self.mouse_state: MouseState = {
            "hovered_id": None,
            "mousedown_start_id": None,
            "mousedown_start_pos": None,
            "drag_active": False,
            "drag_window_relative_offset": None,
        }

    def reset_mouse_state(self):
        self.mouse_state = {
            "hovered_id": None,
            "mousedown_start_id": None,
            "mousedown_start_pos": None,
            "drag_active": False,
            "drag_window_relative_offset": None,
        }

    def synchronize_ids(self):
        new_id_to_node = {}
        for tree in self.trees:
            new_id_to_node.update(tree.meta_state.id_to_node)
        self.id_to_node = new_id_to_node

store = Store()