from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, List, Optional, Union, Deque, Any
from talon.canvas import Canvas
from talon.experimental.textarea import TextArea
from talon.skia import Surface
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from .constants import ElementEnumType, NodeEnumType

@dataclass
class Size2d:
    width: float
    height: float

    def copy(self):
        return Size2d(self.width, self.height)

@dataclass
class BoxModelSpacing:
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

@dataclass
class Margin(BoxModelSpacing):
    pass

@dataclass
class Padding(BoxModelSpacing):
    pass

@dataclass
class Border(BoxModelSpacing):
    pass

class OverflowType(ABC):
    x: str
    y: str
    scrollable: bool
    scrollable_x: bool
    scrollable_y: bool
    is_boundary: bool

class PropertiesDimensionalType(ABC):
    align_items: str
    align_self: str
    border_color: str
    border: Border
    flex_direction: str
    flex: int
    height: Union[int, str]
    justify_content: str
    margin: Margin
    max_height: int
    max_width: int
    min_height: int
    min_width: int
    overflow: OverflowType
    padding: Padding
    position: str
    width: Union[int, str]

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

class ScrollableType(ABC):
    id: str
    offset_x: Union[int, float]
    offset_y: Union[int, float]

@dataclass
class MetaStateInput:
    value: str
    previous_value: str
    input: TextArea
    on_change: Callable[[str], None]
    rect: Rect = None

class MetaStateType(ABC):
    _inputs: dict[str, MetaStateInput]
    _highlighted: dict[str, str]
    _buttons: set[str]
    _draggable_offset: dict[str, Point2d]
    _last_drag_offset: dict[str, Point2d]
    _scrollable = dict[str, ScrollableType]
    _states: dict[str, Any]
    _text_mutations: dict[str, str]
    _style_mutations: dict[str, dict[str, Union[str, int]]]
    _id_to_node: dict[str, 'NodeType']
    _staged_id_to_node: dict[str, 'NodeType']
    ref_property_overrides: dict[str, dict[str, Union[str, int]]]
    unhighlight_jobs: dict[str, callable]

    @property
    def inputs(self) -> dict[str, MetaStateInput]:
        pass

    @property
    def components(self) -> dict[str, 'ComponentType']:
        pass

    @property
    def highlighted(self) -> dict[str, str]:
        pass

    @property
    def buttons(self) -> set[str]:
        pass

    @property
    def scrollable(self) -> dict[str, ScrollableType]:
        pass

    @property
    def states(self) -> dict[str, Any]:
        pass

    @property
    def add_scrollable(self, id) -> None:
        pass

    @property
    def text_mutations(self) -> dict[str, str]:
        pass

    @property
    def style_mutations(self) -> dict[str, dict[str, Union[str, int]]]:
        pass

    @property
    def id_to_node(self) -> dict[str, 'NodeType']:
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def prepare_node_transition(self):
        pass

    @abstractmethod
    def clear_nodes(self):
        pass

    @abstractmethod
    def add_input(self, id: str, input: TextArea, initial_value: str, on_change: callable):
        pass

    @abstractmethod
    def set_drag_offset(self, id: str, offset: Point2d):
        pass

    @abstractmethod
    def get_accumulated_drag_offset(self, id: str) -> Point2d:
        pass

    @abstractmethod
    def get_current_drag_offset(self, id: str) -> Point2d:
        pass

    @abstractmethod
    def commit_drag_offset(self, id: str):
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
    def add_component(self, component: 'ComponentType'):
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
    def get_ref_property_overrides(self, id: str) -> dict[str, Union[str, int]]:
        pass

    @abstractmethod
    def set_ref_property_override(self, id: str, property_name: str, value: Union[str, int]):
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

    @abstractmethod
    def associate_state(self, key: str, components: List['NodeComponentType']):
        pass

    @abstractmethod
    def associate_local_state(self, key: str, component: 'NodeComponentType'):
        pass

class ComponentType(ABC):
    id: tuple[str, tuple[int]]
    name: str
    renderer: Callable
    props: Optional[dict[str, Any]]
    parent_node: Optional['NodeType']
    children_nodes: List['NodeType']
    states: set[str]

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

    @abstractmethod
    def clear(self):
        pass

@dataclass
class BoxModelSpacingType(ABC):
    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

class BoxModelV2Type(ABC):
    id: Union[str, None]
    width: Union[int, str]
    height: Union[int, str]
    min_width: Union[int, str]
    min_height: Union[int, str]
    max_width: Union[int, str]
    max_height: Union[int, str]
    fixed_width: bool
    fixed_height: bool
    overflow: OverflowType
    overflow_size: Size2d
    position: str
    position_left: int
    position_top: int
    position_right: int
    position_bottom: int

    margin_spacing: BoxModelSpacingType
    padding_spacing: BoxModelSpacingType
    border_spacing: BoxModelSpacingType

    margin_rect: Rect
    border_rect: Rect
    padding_rect: Rect
    content_rect: Rect
    content_children_rect: Rect
    padding_with_scroll_bar_rect: Rect

    margin_pos: Point2d
    border_pos: Point2d
    padding_pos: Point2d
    content_pos: Point2d
    content_children_pos: Point2d

    margin_size: Size2d
    border_size: Size2d
    padding_size: Size2d
    content_size: Size2d
    content_children_size: Size2d
    content_children_with_padding_size: Size2d

    calculated_margin_size: Size2d
    calculated_border_size: Size2d
    calculated_padding_size: Size2d
    calculated_content_size: Size2d
    calculated_content_children_size: Size2d

    intrinsic_margin_size: Size2d
    intrinsic_border_size: Size2d
    intrinsic_padding_size: Size2d
    intrinsic_content_size: Size2d
    intrinsic_content_children_size: Size2d
    intrinsic_margin_size_with_bounding_constraints: Size2d

    scroll_bar_track_rect: Union[Rect, None]
    scroll_bar_thumb_rect: Union[Rect, None]
    conditional_scroll_bar_y_width: int

    clip_nodes: List['NodeType']
    clip_rect: Union[Rect, None]

    def is_visible(self) -> Union[bool, str]:
        pass

    def has_scroll_bar_y(self) -> bool:
        pass

    def shift_relative_position(self, cursor):
        pass

class NodeType(ABC):
    properties: object
    cascaded_properties: object
    guid: str
    id: str
    key: str
    node_type: NodeEnumType
    element_type: ElementEnumType
    box_model: BoxModelV2Type
    constraint_nodes: List['NodeType']
    children_nodes: List['NodeType']
    parent_node: Optional['NodeType']
    participates_in_layout: bool
    interactive: bool
    is_dirty: bool
    tree: 'TreeType'
    root_node: 'NodeRootType'
    depth: int
    node_index_path: List[int]
    component_node: object
    relative_positional_node: Optional['NodeType']

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
    def participating_children_nodes(self) -> List['NodeType']:
        pass

    @abstractmethod
    def non_participating_children_nodes(self) -> List['NodeType']:
        pass

    @abstractmethod
    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        pass

    @abstractmethod
    def v2_grow_size(self):
        pass

    @abstractmethod
    def v2_constrain_size(self, available_size: Size2d = None):
        pass

    @abstractmethod
    def v2_layout(self, cursor: object) -> Size2d:
        pass

    @abstractmethod
    def v2_render(self, c: SkiaCanvas):
        pass

    @abstractmethod
    def v2_scroll_layout(self, offset: Point2d = None):
        pass

    @abstractmethod
    def v2_reposition(self, offset: Point2d = None):
        pass

    @abstractmethod
    def inherit_cascaded_properties(self, parent_node: 'NodeType'):
        pass

    @abstractmethod
    def is_fully_clipped_by_scroll(self):
        pass

    @abstractmethod
    def __init__(self, element_type: ElementEnumType, properties: object):
        pass

    def get_children_nodes(self) -> List['NodeType']:
        pass

class RenderCauseStateType(ABC):
    @abstractmethod
    def state_change(self):
        pass

    @abstractmethod
    def ref_change(self):
        pass

    @abstractmethod
    def set_is_dragging(self):
        pass

    @abstractmethod
    def is_dragging(self):
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

@dataclass
class RenderItem:
    node: NodeType
    draw: Callable[[SkiaCanvas], None]

@dataclass
class RenderLayer:
    z_index: int
    z_subindex: int
    items: List[RenderItem]

    def render_to_surface(self, width, height, offset_x=0, offset_y=0):
        surface = Surface(width, height)
        canvas = surface.canvas()
        canvas.translate(-offset_x, -offset_y)
        for item in self.items:
            item.draw(canvas)
        return surface.snapshot()

    def draw_to_canvas(self, canvas: SkiaCanvas):
        for item in self.items:
            item.draw(canvas)

class RenderTaskType(ABC):
    cause: str
    start: Callable
    args: List[object]
    on_start: Callable
    on_end: Callable
    group: str
    policy: str
    metadata: dict[str, Any]

class RenderManagerType(ABC):
    queue: Deque[RenderTaskType]
    current_render_task: Optional[RenderTaskType]
    tree: 'TreeType'
    _render_debounce_job: Optional[object]

    @property
    def render_cause(self):
        pass

    @property
    def is_rendering(self):
        pass

    @property
    def is_destroying(self):
        pass

    @abstractmethod
    def is_scrolling(self):
        pass

    @abstractmethod
    def is_drag_start(self):
        pass

    @abstractmethod
    def is_dragging(self):
        pass

    @abstractmethod
    def is_drag_end(self):
        pass

    @abstractmethod
    def __init__(self, tree: 'TreeType'):
        pass

    @abstractmethod
    def queue_render(self, render_task: RenderTaskType):
        pass

    @abstractmethod
    def _queue_render_after_debounce(self, interval: str, render_task: RenderTaskType):
        pass

    @abstractmethod
    def _queue_render_after_debounce_execute(self, render_task: RenderTaskType):
        pass

    @abstractmethod
    def prepare_destroy(self):
        pass

    @abstractmethod
    def process_next_render(self):
        pass

    @abstractmethod
    def finish_current_render(self):
        pass

    @abstractmethod
    def render_mount(
            self,
            props: dict[str, Any] = {},
            on_mount: callable = None,
            on_unmount: callable = None,
            show_hints: bool = None
        ):
        pass

    @abstractmethod
    def render_text_mutation(self):
        pass

    @abstractmethod
    def render_ref_change(self):
        pass

    @abstractmethod
    def render_drag_start(self):
        pass

    @abstractmethod
    def render_drag_end(self):
        pass

    @abstractmethod
    def schedule_state_change(self, on_start: callable, on_end: callable = None):
        pass

    @abstractmethod
    def destroy(self):
        pass


class NodeContainerType(NodeType):
    highlight_color: str
    is_uniform_border: bool
    justify_between_gaps: Optional[int]

    # @abstractmethod
    # def debugger_should_continue(self, c: object, cursor: object):
    #     pass

    # @abstractmethod
    # def debugger(self, c: object, cursor: object, incrememnt_step: bool, new_color: bool, is_breakpoint: bool):
    #     pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def hide(self):
        pass

class NodeSvgType(NodeType):
    pass

class TreeType(ABC):
    canvas_base: Canvas
    canvas_decorator: Canvas
    canvas_mouse: Canvas
    current_canvas: SkiaCanvas
    cursor: CursorType
    draggable_node: NodeType
    draggable_node_delta_pos: Point2d
    drag_handle_node: NodeType
    effects: List[Effect]
    meta_state: MetaStateType
    name: str
    processing_states: List[str]
    render_manager: RenderManagerType
    _tree_constructor: callable
    requires_measure_redistribution: bool
    surfaces: List[object]
    last_surface_snapshot: object
    hashed_tree_constructor: str
    unused_screens: List[int]
    root_node: 'NodeRootType'
    show_hints: bool
    screen_index: int
    render_cause: RenderCauseStateType
    render_version: int
    is_mounted: bool

    @abstractmethod
    def render_debounced(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def append_to_render_list(self, node: NodeType, draw: Callable[[SkiaCanvas], None]):
        pass

class TreeManagerType(ABC):
    trees: List[TreeType]
    processing_tree: Optional[TreeType]

    @abstractmethod
    def render(self, tree_constructor: callable):
        pass

    @abstractmethod
    def refresh_decorator_canvas(self):
        pass

    @abstractmethod
    def generate_hash_for_updater(self, tree_constructor: callable):
        pass

class NodeRootType(NodeContainerType):
    screen_index: int
    boundary_rect: Rect

class NodeComponentType(ABC):
    root_node: object
    node_type: NodeEnumType
    element_type: ElementEnumType
    guid: str
    func: Callable
    properties: object
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
    def __getitem__(self):
        pass

@dataclass
class ClickEvent:
    id: str
    cause: str = "click"