from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Union, Deque, Any
from talon.experimental.textarea import TextArea
from talon.canvas import Canvas
from talon.skia.canvas import Canvas as SkiaCanvas
from dataclasses import dataclass
from .constants import ElementEnumType, NodeEnumType
from talon.types import Rect, Point2d

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

class MetaStateType(ABC):
    _inputs: dict[str, MetaStateInput]
    _highlighted: dict[str, str]
    _buttons: set[str]
    _scrollable = dict[str, ScrollableType]
    _text_mutations: dict[str, str]
    _style_mutations: dict[str, dict[str, Union[str, int]]]
    _id_to_node: dict[str, 'NodeType']
    ref_property_overrides: dict[str, dict[str, Union[str, int]]]
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
    def scrollable(self) -> dict[str, ScrollableType]:
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
    def clear_nodes(self):
        pass

    @abstractmethod
    def add_input(self, id: str, input: TextArea, initial_value: str, on_change: callable):
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

class BoxModelLayoutType(ABC):
    constraints: dict[str, int]
    margin_spacing: BoxModelSpacingType
    padding_spacing: BoxModelSpacingType
    border_spacing: BoxModelSpacingType
    margin_rect: Rect
    padding_rect: Rect
    border_rect: Rect
    content_rect: Rect
    content_children_rect: Rect
    intrinsic_margin_rect: Rect
    intrinsic_padding_rect: Rect
    intrinsic_border_rect: Rect
    intrinsic_content_rect: Rect
    intrinsic_content_children_rect: Rect
    scroll_box_rect: Union[Rect, None] = None
    scrollable: bool
    fixed_width: bool
    fixed_height: bool
    min_width: int
    min_height: int
    max_width: int
    max_height: int
    width: int
    height: int

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

    @abstractmethod
    def gc(self):
        pass

class BoxModelV2Type(ABC):
    width: Union[int, str]
    height: Union[int, str]
    min_width: Union[int, str]
    min_height: Union[int, str]
    max_width: Union[int, str]
    max_height: Union[int, str]
    fixed_width: bool
    fixed_height: bool

    margin_spacing: BoxModelSpacingType
    padding_spacing: BoxModelSpacingType
    border_spacing: BoxModelSpacingType

    margin_rect: Rect
    border_rect: Rect
    padding_rect: Rect
    content_rect: Rect
    content_children_rect: Rect

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

    def clip_rect(self):
        pass

    def is_visible(self) -> Union[bool, str]:
        pass

class NodeType(ABC):
    properties: object
    cascaded_properties: object
    guid: str
    id: str
    key: str
    node_type: NodeEnumType
    element_type: ElementEnumType
    box_model: BoxModelLayoutType
    box_model_v2: BoxModelV2Type
    constraint_nodes: List['NodeType']
    children_nodes: List['NodeType']
    parent_node: Optional['NodeType']
    interactive: bool
    is_dirty: bool
    tree: 'TreeType'
    root_node: 'NodeRootType'
    depth: int
    node_index_path: List[int]
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

    # @abstractmethod
    # def render(self):
    #     pass

    # @abstractmethod
    # def virtual_render(self):
    #     pass

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

class RenderTaskType(ABC):
    cause: str
    on_render: Callable
    args: List[object]

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
    def is_dragging(self):
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
    def render_drag_end(self):
        pass

    @abstractmethod
    def destroy(self):
        pass


class NodeContainerType(NodeType):
    highlight_color: str
    is_uniform_border: bool
    justify_between_gaps: Optional[int]

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

    # @abstractmethod
    # def render(self, c: object, cursor: object):
    #     pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def hide(self):
        pass

class NodeSvgType(NodeType):
    @abstractmethod
    def grow_intrinsic_size(self, c: object, cursor: object):
        pass

    # @abstractmethod
    # def virtual_render(self, c: object, cursor: object):
    #     pass

    # @abstractmethod
    # def render(self, c: object, cursor: object):
    #     pass

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
    processing_states: List[str]
    render_manager: RenderManagerType
    _renderer: callable
    requires_measure_redistribution: bool
    surfaces: List[object]
    update_renderer: str
    unused_screens: List[int]
    root_node: 'NodeRootType'
    show_hints: bool
    screen_index: int
    _renderer: callable
    render_cause: RenderCauseStateType
    render_version: int
    is_mounted: bool

    @abstractmethod
    def __init__(self, renderer: callable, update_renderer: str):
        pass

    # @abstractmethod
    # def render(self):
    #     pass

    @abstractmethod
    def render_debounced(self):
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
    def virtual_render(self, c: object, cursor: object):
        pass

    # @abstractmethod
    # def render(self, c: object, cursor: object):
    #     pass

    @abstractmethod
    def __getitem__(self):
        pass

@dataclass
class ClickEvent:
    id: str
    cause: str = "click"