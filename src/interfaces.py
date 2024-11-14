from typing import Callable, List, Optional, TypedDict, Any, Union, Literal
from abc import ABC, abstractmethod

NodeEnumType = Literal['root', 'node', 'leaf', 'component']
ElementEnumType = Literal['button', 'text', 'div', 'input', 'screen', 'window', 'component']

class EffectType(TypedDict):
    name: str
    callback: Callable[[], Callable]
    dependencies: Optional[List[str]]
    component_node: Optional[object]

class ReactiveStateType(ABC):
    value: Any
    subscriber_root_nodes: List[object]
    next_state_queue: List[Any]

    @abstractmethod
    def set_value(self, value: Any):
        pass

    @abstractmethod
    def add_subscriber(self, root_node: object):
        pass

    @abstractmethod
    def activate_next_state_value(self):
        pass

class GlobalStoreType(ABC):
    root_nodes: dict[str, dict]
    id_nodes: dict[str, dict]
    active_component: Optional[str]
    reactive_global_state: dict[str, ReactiveStateType]
    staged_effects: List[EffectType]

class NodeRootStateStoreType(ABC):
    effects: List[EffectType]
    state_to_effects: dict[str, List[EffectType]]
    state_to_components: dict[str, List['NodeComponentType']]

    @abstractmethod
    def add_effect(self, effect: EffectType):
        pass

    @abstractmethod
    def clear(self):
        pass

class NodeRootStoreType(ABC):
    components: List['NodeType']
    buttons: List['NodeType']
    inputs: List['NodeType']
    dynamic_text: List['NodeType']
    highlighted: List['NodeType']
    scrollable_regions: List['NodeType']

    @abstractmethod
    def clear(self):
        pass

class NodeType(ABC):
    options: object
    guid: str
    id: str
    key: str
    node_type: NodeEnumType
    element_type: ElementEnumType
    box_model: object
    children_nodes: List['NodeType']
    parent_node: Optional['NodeType']
    is_dirty: bool
    root_node: object
    depth: int
    component_node: object

    @abstractmethod
    def add_child(self, node: 'NodeType'):
        pass

    @abstractmethod
    def __getitem__(self, children_nodes: Union[List['NodeType'], 'NodeType']):
        pass

    @abstractmethod
    def invalidate(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def check_invalid_child(self, c: 'NodeType'):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def hide(self):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def virtual_render(self):
        pass

    @abstractmethod
    def __init__(self, element_type: ElementEnumType, options: object):
        pass


class NodeContainerType(NodeType):
    scroll_y: int
    scroll_y_percentage: float
    highlight_color: str
    is_uniform_border: bool

    @abstractmethod
    def set_scroll_y(self, delta: int):
        pass

    @abstractmethod
    def virtual_render_child(self, c: object, cursor: object, child: NodeType, i: int, move_after_last_child: bool):
        pass

    @abstractmethod
    def virtual_render(self, c: object, cursor: object):
        pass

    @abstractmethod
    def calculate_flex_weights(self, flex_children: List[NodeType]):
        pass

    @abstractmethod
    def draw_debug_number(self, c: object, cursor: object, new_color: bool):
        pass

    @abstractmethod
    def render_borders(self, c: object, cursor: object):
        pass

    @abstractmethod
    def render_background(self, c: object, cursor: object):
        pass

    @abstractmethod
    def adjust_for_scroll_y_start(self, c: object):
        pass

    @abstractmethod
    def adjust_for_scroll_y_end(self, c: object):
        pass

    @abstractmethod
    def crop_scrollable_region_start(self, c: object):
        pass

    @abstractmethod
    def crop_scrollable_region_end(self, c: object):
        pass

    @abstractmethod
    def debugger_should_continue(self, c: object, cursor: object):
        pass

    @abstractmethod
    def debugger(self, c: object, cursor: object, incrememnt_step: bool, new_color: bool, is_breakpoint: bool):
        pass

    @abstractmethod
    def move_cursor_to_align_axis_before_children_render(self, cursor: object):
        pass

    @abstractmethod
    def move_cursor_to_top_left_child_based_on_align_axis(self, cursor: object, child: NodeType):
        pass

    @abstractmethod
    def move_cursor_from_top_left_child_to_next_child_along_align_axis(self, cursor: object, child: NodeType, rect: object, gap: int):
        pass

    @abstractmethod
    def render(self, c: object, cursor: object, scroll_region_key: int):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def hide(self):
        pass

class NodeRootType(NodeContainerType):
    blockable_canvases: List[object]
    canvas_base: object
    canvas_decorative: object
    cursor: object
    dynamic_canvas: object
    hash: str
    highlight_canvas: object
    highlight_color: str
    is_blockable_canvas_init: bool
    is_mounted: bool
    node_store: NodeRootStoreType
    render_busy: bool
    root_node: object
    screen_index: int
    state_store: NodeRootStateStoreType
    unhighlight_jobs: dict
    updater: object
    window: object

    @abstractmethod
    def on_draw_static(self, c: object):
        pass

    @abstractmethod
    def on_draw_dynamic(self, c: object):
        pass

    @abstractmethod
    def update_blockable_canvases(self):
        pass

    @abstractmethod
    def update_blockable_canvases_debounced(self):
        pass

    @abstractmethod
    def on_fully_rendered(self):
        pass

    @abstractmethod
    def on_draw_highlight(self, c: object):
        pass

    @abstractmethod
    def clear_blockable_canvases(self):
        pass

    @abstractmethod
    def init_blockable_canvases(self):
        pass

    @abstractmethod
    def generate_hash_from_tree(self):
        pass

    @abstractmethod
    def hash_and_prevent_duplicate_render(self):
        pass

    @abstractmethod
    def show(self, on_mount: Callable):
        pass

    @abstractmethod
    def on_hover_button(self, gpos: object):
        pass

    @abstractmethod
    def on_click_button(self, gpos: object):
        pass

    @abstractmethod
    def on_mouse_window(self, e: object):
        pass

    @abstractmethod
    def on_mouse(self, e: object):
        pass

    @abstractmethod
    def get_ids(self):
        pass

    @abstractmethod
    def set_text(self, id: str, text: str):
        pass

    @abstractmethod
    def highlight(self, id: str, color: str):
        pass

    @abstractmethod
    def unhighlight(self, id: str):
        pass

    @abstractmethod
    def highlight_briefly(self, id: str, color: str, duration: int):
        pass

    @abstractmethod
    def freeze_if_not_busy(self):
        pass

class NodeComponentType(ABC):
    root_node: object
    node_type: NodeEnumType
    element_type: ElementEnumType
    guid: str
    func: Callable
    options: object
    inner_node: NodeType
    is_initialized: bool
    children_nodes: List[NodeType]
    parent_node: NodeType
    is_dirty: bool
    depth: int

    @abstractmethod
    def adopt_inner_node_attributes(self, node: object):
        pass

    @abstractmethod
    def setup_children(self):
        pass

    @abstractmethod
    def virtual_render(self, c: object, cursor: object):
        pass

    @abstractmethod
    def render(self, c: object, cursor: object, scroll_region_key: int):
        pass

    @abstractmethod
    def __getitem__(self):
        pass