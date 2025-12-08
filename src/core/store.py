from typing import Optional, TypedDict, Tuple
from ..interfaces import (
    Effect,
    TreeType,
    NodeType,
    ReactiveStateType,
    Point2d
)

class MouseState(TypedDict):
    hovered_id: Optional[str]
    mousedown_start_id: Optional[str]
    mousedown_start_pos: Optional[Tuple[int, int]]
    is_drag_active: bool
    drag_relative_offset: Optional[Tuple[int, int]]

class Store():
    def __init__(self):
        self.trees: list[TreeType] = []
        self.focused_id: Optional[str] = None
        self.focused_tree: Optional[TreeType] = None
        self.focused_visible: Optional[bool] = None
        self.processing_tree: Optional[TreeType] = None
        self.processing_components: list[NodeType] = []
        self.processing_states: set[str] = set()
        self.root_nodes: list[NodeType] = []
        self.id_to_node: dict[str, NodeType] = {}
        self.id_to_hint: dict[str, str] = {}
        self.pause_renders = False
        self.reactive_state: dict[str, ReactiveStateType] = {}
        self.staged_effects: list[Effect] = []
        self.ref_count_nodes = 0
        self.ref_count_trees = 0
        self.scale: float = 1.0  # UI scale, initialized from settings per tree
        self.mouse_state: MouseState = {
            "disable_events": False,
            "hovered_id": None,
            "last_clicked_pos": None,
            "mousedown_start_id": None,
            "mousedown_start_pos": None,
            "mousedown_start_offset": Point2d(0, 0),
            "is_drag_active": False,
            "drag_relative_offset": None,
        }

    def reset_mouse_state(self):
        self.mouse_state = {
            "disable_events": False,
            "hovered_id": None,
            "last_clicked_pos": None,
            "mousedown_start_id": None,
            "mousedown_start_pos": None,
            "mousedown_start_offset": Point2d(0, 0),
            "is_drag_active": False,
            "drag_relative_offset": None,
        }

    def synchronize_ids(self):
        new_id_to_node = {}
        for tree in self.trees:
            new_id_to_node.update(tree.meta_state.id_to_node)
        self.id_to_node = new_id_to_node

    def clear(self):
        self.trees = []
        self.focused_id = None
        self.focused_tree = None
        self.focused_visible = None
        self.pause_renders = False
        self.processing_tree = None
        self.processing_components = []
        self.processing_states.clear()
        self.root_nodes = []
        self.id_to_node = {}
        self.id_to_hint = {}
        self.reactive_state = {}
        self.staged_effects = []
        self.reset_mouse_state()

store = Store()
