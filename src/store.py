from typing import Optional, TypedDict, Tuple
from .interfaces import TreeType, NodeType, Effect, ReactiveStateType

class MouseState(TypedDict):
    hovered_id: Optional[str]
    mousedown_start_id: Optional[str]
    mousedown_start_pos: Optional[Tuple[int, int]]
    is_drag_active: bool
    drag_window_relative_offset: Optional[Tuple[int, int]]

class Store():
    def __init__(self):
        self.trees: list[TreeType] = []
        self.processing_tree: Optional[TreeType] = None
        self.processing_states: list[str] = []
        self.root_nodes: list[NodeType] = []
        self.id_to_node: dict[str, NodeType] = {}
        self.id_to_hint: dict[str, str] = {}
        self.reactive_state: dict[str, ReactiveStateType] = {}
        self.staged_effects: list[Effect] = []
        self.mouse_state: MouseState = {
            "hovered_id": None,
            "mousedown_start_id": None,
            "mousedown_start_pos": None,
            "is_drag_active": False,
            "drag_window_relative_offset": None,
        }

    def reset_mouse_state(self):
        self.mouse_state = {
            "hovered_id": None,
            "mousedown_start_id": None,
            "mousedown_start_pos": None,
            "is_drag_active": False,
            "drag_window_relative_offset": None,
        }

    def synchronize_ids(self):
        new_id_to_node = {}
        for tree in self.trees:
            new_id_to_node.update(tree.meta_state.id_to_node)
        self.id_to_node = new_id_to_node

    def clear(self):
        self.trees = []
        self.processing_tree = None
        self.processing_states = []
        self.root_nodes = []
        self.id_to_node = {}
        self.id_to_hint = {}
        self.reactive_state = {}
        self.staged_effects = []
        self.reset_mouse_state()

store = Store()
