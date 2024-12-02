from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Union
from talon.experimental.textarea import TextArea
from talon.canvas import Canvas
from dataclasses import dataclass
from .constants import ElementEnumType, NodeEnumType
from talon.types import Rect, Point2d

class CursorType:
    x: int
    y: int
    virtual_x: int
    virtual_y: int

    def move_to(self, x: int, y: int):
        pass

    def virtual_move_to(self, x: int, y: int):
        pass

    def reset(self):
        pass

@dataclass
class Effect:
    callback: Callable[[], Optional[Callable]]
    dependencies: Optional[List[str]]
    tree: 'TreeType'
    cleanup: Optional[Callable[[], None]] = None
    name: Optional[str] = None

StateValueType = Union[int, float, str, bool, dict, list, None]
StateValueOrCallableType = Union[StateValueType, Callable[[StateValueType], StateValueType]]

class ReactiveStateType(ABC):
    _initial_value: StateValueType
    _value: StateValueType
    subscriber_trees: List['TreeType']
    next_state_queue: List[StateValueOrCallableType]

    @property
    def initial_value(self) -> StateValueType:
        pass

    @property
    def value(self) -> StateValueType:
        pass

    @abstractmethod
    def resolve_value(self, value_or_callable: StateValueOrCallableType) -> StateValueType:
        pass

    @abstractmethod
    def set_initial_value(self, value: StateValueType):
        pass

    @abstractmethod
    def set_value(self, value_or_callable: StateValueOrCallableType):
        pass

    @abstractmethod
    def activate_next_state_value(self):
        pass

class ScrollRegionType(ABC):
    scroll_y: int
    scroll_x: int

@dataclass
class MetaStateInput:
    value: str
    previous_value: str
    input: TextArea

class MetaStateType(ABC):
    _inputs: dict[str, MetaStateInput]
    _highlighted: dict[str, str]
    _buttons: set[str]
    _text_mutations: dict[str, str]
    _style_mutations: dict[str, dict[str, Union[str, int]]]
    _scroll_regions: dict[str, ScrollRegionType]
    _id_to_node: dict[str, 'NodeType']
    focused_id: Optional[str]
    unhighlight_jobs: dict[str, callable]

    @property
    def inputs(self) -> dict[str, MetaStateInput]:
        pass

    @property
    def highlighted(self) -> dict[str, str]:
        pass

    @property
    def buttons(self) -> set[str]:
        pass

    @property
    def text_mutations(self) -> dict[str, str]:
        pass

    @property
    def style_mutations(self) -> dict[str, dict[str, Union[str, int]]]:
        pass

    @property
    def scroll_regions(self) -> dict[str, ScrollRegionType]:
        pass

    @property
    def id_to_node(self) -> dict[str, 'NodeType']:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def clear_nodes(self):
        pass

    @abstractmethod
    def add_input(self, id: str, input: TextArea, initial_value: str):
        pass

    @abstractmethod
    def set_highlighted(self, id: str, color: str):
        pass

    @abstractmethod
    def set_unhighlighted(self, id: str):
        pass

    @abstractmethod
    def add_button(self, id: str):
        pass

    @abstractmethod
    def set_text_mutation(self, id: str, text: str):
        pass

    @abstractmethod
    def use_text_mutation(self, id: str, initial_text: str):
        pass

    @abstractmethod
    def set_style_mutation(self, id: str, style: dict[str, Union[str, int]]):
        pass

    @abstractmethod
    def add_scroll_region(self, id: str):
        pass

    @abstractmethod
    def scroll_y_increment(self, id: str, y: int):
        pass

    @abstractmethod
    def scroll_x_increment(self, id: str, x: int):
        pass

    @abstractmethod
    def map_id_to_node(self, id: str, node: object):
        pass

class NodeRootStateStoreType(ABC):
    effects: List[Effect]
    state_to_effects: dict[str, List[Effect]]
    state_to_components: dict[str, List['NodeComponentType']]

    @abstractmethod
    def add_effect(self, effect: Effect):
        pass

    @abstractmethod
    def clear(self):
        pass

class TreeNodeRefsType(ABC):
    buttons: dict[str, 'NodeType']
    inputs: dict[str, 'NodeType']
    dynamic_text: dict[str, 'NodeType']
    highlighted: dict[str, 'NodeType']
    scrollable_regions: dict[str, 'NodeType']

    @abstractmethod
    def clear(self):
        pass

@dataclass
class BoxModelSpacingType(ABC):
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

class BoxModelLayoutType(ABC):
    margin_spacing: BoxModelSpacingType
    padding_spacing: BoxModelSpacingType
    border_spacing: BoxModelSpacingType
    margin_rect: Rect
    padding_rect: Rect
    border_rect: Rect
    content_rect: Rect
    content_children_rect: Rect
    scroll_box_rect: Union[Rect, None] = None

    @abstractmethod
    def accumulate_outer_dimensions_width(self, new_width: int):
        pass

    @abstractmethod
    def accumulate_outer_dimensions_height(self, new_height: int):
        pass

    @abstractmethod
    def accumulate_content_dimensions(self, rect: Rect, axis: str = None):
        pass

    @abstractmethod
    def position_for_render(self, cursor: Point2d, flex_direction: str, align_items: str, justify_content: str):
        pass

class NodeType(ABC):
    options: object
    guid: str
    id: str
    key: str
    node_type: NodeEnumType
    element_type: ElementEnumType
    box_model: BoxModelLayoutType
    constraint_nodes: List['NodeType']
    children_nodes: List['NodeType']
    parent_node: Optional['NodeType']
    interactive: bool
    is_dirty: bool
    tree: 'TreeType'
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

class RenderCauseStateType(ABC):
    @abstractmethod
    def state_change(self):
        pass

    @abstractmethod
    def ref_change(self):
        pass

    @abstractmethod
    def set_text_change(self):
        pass

    @abstractmethod
    def highlight_change(self):
        pass

    @abstractmethod
    def input_focus_change(self):
        pass

    @abstractmethod
    def is_state_change(self):
        pass

    @abstractmethod
    def is_input_focus_change(self):
        pass

    @abstractmethod
    def is_ref_change(self):
        pass

    @abstractmethod
    def is_highlight_change(self):
        pass

    @abstractmethod
    def is_text_change(self):
        pass

    @abstractmethod
    def clear(self):
        pass

class NodeContainerType(NodeType):
    scroll_y: int
    scroll_y_percentage: float
    highlight_color: str
    is_uniform_border: bool
    justify_between_gaps: Optional[int]

    @abstractmethod
    def set_scroll_y(self, delta: int):
        pass

    @abstractmethod
    def virtual_render_child(self, c: object, cursor: object, child: NodeType, i: int, move_after_last_child: bool):
        pass

    @abstractmethod
    def grow_intrinsic_size(self, c: object, cursor: object):
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

class TreeType(ABC):
    canvas_base: Canvas
    canvas_decorator: Canvas
    canvas_mouse: Canvas
    cursor: CursorType
    effects: List[Effect]
    meta_state: MetaStateType
    processing_states: List[str]
    _renderer: callable
    surfaces: List[object]
    update_renderer: str
    root_node: NodeType
    show_hints: bool
    screen_index: int
    _renderer: callable
    render_cause: RenderCauseStateType
    render_version: int
    is_mounted: bool

    @abstractmethod
    def __init__(self, renderer: callable, update_renderer: str):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

class TreeManagerType(ABC):
    trees: List[TreeType]
    processing_tree: Optional[TreeType]

    @abstractmethod
    def render(self, renderer: callable):
        pass

    @abstractmethod
    def refresh_decorator_canvas(self):
        pass

    @abstractmethod
    def generate_hash_for_updater(self, renderer: callable):
        pass

class NodeScreenType(NodeContainerType):
    screen_index: int

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
    node_store: TreeNodeRefsType
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

@dataclass
class ClickEvent:
    id: str
    cause: str = "click"