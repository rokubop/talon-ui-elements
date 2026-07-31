import inspect
import math
import time
import uuid
import threading
import traceback
import weakref
from talon import cron, settings, ctrl, storage
from talon.canvas import Canvas as RealCanvas, MouseEvent
from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect, Point2d
from typing import Any, Callable, Optional
from collections import defaultdict
from dataclasses import dataclass

from ..constants import (
    ELEMENT_ENUM_TYPE,
    DRAG_INIT_THRESHOLD,
    DECORATOR_COALESCE_MS,
    DEFAULT_CURSOR_REFRESH_RATE,
    DEFAULT_HIGHLIGHT_DURATION_MS,
    DEFAULT_SCROLL_BAR_FADE_IN_MS,
    DEFAULT_SCROLL_BAR_FADE_OUT_MS,
    DEFAULT_SCROLL_BAR_IDLE_MS,
    DEFAULT_SCROLL_BAR_WIDTH,
    DEFAULT_SCROLL_BUTTON_SIZE,
    DEFAULT_SCROLL_BUTTON_INSET,
    DEFAULT_SCROLL_BUTTON_BACKGROUND_COLOR,
    DEFAULT_SCROLL_BUTTON_HOVER_BACKGROUND_COLOR,
    DEFAULT_SCROLL_BUTTON_BORDER_COLOR,
    DEFAULT_SCROLL_BUTTON_ICON_COLOR,
    RESIZE_EDGE_THRESHOLD,
    RESIZE_GHOST_COLOR,
    RESIZE_GHOST_STROKE_WIDTH,
    RESIZE_EDGE_HIGHLIGHT_COLOR,
    RESIZE_EDGE_HIGHLIGHT_WIDTH,
    PRIMARY_MOD,
    KEY_SPACE, KEY_ENTER, KEY_RETURN, KEY_ESCAPE,
)
from ..utils import draw_rect, get_scale, scale_value
from ..canvas_wrapper import CanvasWeakRef
from ..border_radius import draw_manual_rounded_rect_path
from ..core.entity_manager import entity_manager
from ..core.animations import TransitionManager, ANIMATABLE_COLOR_PROPERTIES
from ..core.render_manager import RenderManager, RenderCause
from ..core.state_manager import state_manager
from ..core.store import store
from ..cursor import Cursor, CursorV2
from ..events import StateEvent, DragEndEvent, WindowCloseEvent
from ..interfaces import (
    TreeType,
    NodeType,
    MetaStateInput,
    MetaStateType,
    Effect,
    ClickEvent,
    ComponentType,
    RenderCauseStateType,
    RenderItem,
    RenderLayer,
    RenderTransforms,
    ScrollRegionType,
    ScrollableType,
    Size2d,
)
from ..hints import draw_hint, draw_scroll_button_hint, get_hint_generator, hint_clear_state, hint_tag_enable
from ..style import Style
from ..utils import (
    draw_text_simple,
    find_closest_parent_with_id,
    get_active_color_from_highlight_color,
    get_combined_screens_rect,
    subtract_rect,
)

scroll_throttle_job = None
scroll_throttle_time = "30ms"

debug = True

def log_trace():
    if debug:
        traceback.print_exc()

def log(*args):
    if debug:
        print("LOG:", *args)

def scroll_throttle_clear():
    global scroll_throttle_job
    if scroll_throttle_job:
        cron.cancel(scroll_throttle_job)
    scroll_throttle_job = None

class ScrollRegion(ScrollRegionType):
    def __init__(self, scroll_y: int = 0, scroll_x: int = 0):
        self.scroll_y = scroll_y
        self.scroll_x = scroll_x

class Scrollable(ScrollableType):
    def __init__(self, id):
        self.id = id
        self.offset_x = 0
        self.offset_y = 0
        self.target_offset_x = 0
        self.target_offset_y = 0
        self.rendered_offset_x = 0
        self.rendered_offset_y = 0
        self.view_height = 0
        self.max_height = 0
        self.view_width = 0
        self.max_width = 0

    def reevaluate(self, node: NodeType):
        max_height = node.box_model.content_children_with_padding_size.height
        view_height = node.box_model.padding_size.height
        max_width = node.box_model.content_children_with_padding_size.width
        view_width = node.box_model.padding_size.width
        height_changed = view_height != self.view_height or max_height != self.max_height
        width_changed = view_width != self.view_width or max_width != self.max_width
        if height_changed or width_changed:
            self.view_height = view_height
            self.max_height = max_height
            self.view_width = view_width
            self.max_width = max_width
            min_offset_y = min(0, view_height - max_height)
            min_offset_x = min(0, view_width - max_width)
            self.offset_y = max(min_offset_y, min(0, self.offset_y))
            self.offset_x = max(min_offset_x, min(0, self.offset_x))
            self.target_offset_y = max(min_offset_y, min(0, self.target_offset_y))
            self.target_offset_x = max(min_offset_x, min(0, self.target_offset_x))

@dataclass
class DraggableOffset:
    x: int
    y: int


@dataclass
class ScrollButtonOverlay:
    container_id: str
    role: str       # "up" | "down" | "left" | "right"
    axis: str       # "y" | "x"
    direction: int  # -1 | 1
    rect: Rect
    synthetic_id: str
    style: dict = None


class MetaState(MetaStateType):
    def __init__(self):
        self._buttons = []
        self._components = {}
        self._staged_components = {}
        self.decoration_renders = {}
        self._highlighted = {}
        self._id_to_node = {}
        self._staged_id_to_node = {}
        self._inputs = {}
        self._scroll_regions = {}
        self._scrollable = {}
        self._states = {}
        self._text_with_for_ids = {}
        self._draggable_offset = {}
        self._last_drag_offset = {}
        self._style_mutations = {}
        self._text_mutations = {}
        self.windows = set()
        self.resizable_nodes = set()
        self.ref_property_overrides = {}
        self.unhighlight_jobs = {}
        self.new_component_ids = set()
        self.removed_component_ids = set()
        self.scrollbar_hovered_id = None
        self.scrollbar_hovered_axis = None
        self.scrollbar_dragging_id = None
        self.scrollbar_dragging_axis = None
        self.scrollbar_drag_start_y = None
        self.scrollbar_drag_start_offset_y = None
        self.scrollbar_drag_start_x = None
        self.scrollbar_drag_start_offset_x = None
        self.scrollbar_opacity = {}
        self.scrollbar_fade_jobs = {}
        self.scrollbar_idle_jobs = {}
        self.scroll_button_overlays: dict[str, ScrollButtonOverlay] = {}
        self.scroll_button_hovered_id: str = None
        self.resize_edge_hovered = None
        self.resize_original_constraints = {}
        self.resize_dragging_id = None
        self.resize_edge = None
        self.resize_start_pos = None
        self.resize_start_rect = None
        self.resize_ghost_rect = None
        # True when any node in the current tree is a floating overlay
        # (uses_decoration_render and z_index > 0). Used to fast-exit
        # hit-test filtering when no overlay is open.
        self.has_hit_priority_overlay = False

    @property
    def buttons(self):
        return self._buttons

    @property
    def components(self):
        return self._components

    @property
    def highlighted(self):
        return self._highlighted

    @property
    def id_to_node(self):
        return self._id_to_node

    @property
    def staged_id_to_node(self):
        return self._staged_id_to_node

    @property
    def inputs(self):
        return self._inputs

    @property
    def scroll_regions(self):
        return self._scroll_regions

    @property
    def scrollable(self):
        return self._scrollable

    @property
    def states(self):
        return self._states

    @property
    def style_mutations(self):
        return self._style_mutations

    @property
    def text_mutations(self):
        return self._text_mutations

    @property
    def text_with_for_ids(self):
        return self._text_with_for_ids

    def add_input(self, id, input, initial_value = None, on_change = None):
        if id in self._inputs:
            input_data = self._inputs.pop(id)
            if input_data:
                input_data.input.unregister("label", input_data.on_change)
                input_data.input.hide()
                input_data.input = None
        input_data = MetaStateInput(
            value=initial_value,
            input=input,
            previous_value=None,
            on_change=on_change
        )
        input.register("label", on_change)
        self._inputs[id] = input_data

    def add_button(self, id):
        if id not in self._buttons:
            self._buttons.append(id)

    def add_component(self, component):
        if component.id not in self._staged_components:
            if component.id in self._components:
                self._staged_components[component.id] = self._components[component.id]
            else:
                self._staged_components[component.id] = component

    def map_id_to_node(self, id, node):
        self._id_to_node[id] = node

    def add_scroll_region(self, id):
        self._scroll_regions[id] = ScrollRegion(0, 0)

    def add_scrollable(self, id):
        if not id in self._scrollable:
            self._scrollable[id] = Scrollable(id)

    def add_text_with_for_id(self, id, for_id):
        if id not in self._text_with_for_ids:
            self._text_with_for_ids[id] = for_id

    def add_decoration_render(self, id):
        self.decoration_renders[id] = True

    def associate_state(self, key, components):
        if key not in self._states:
            self._states[key] = set()
        for c in components:
            self._states[key].add(c.id)
            c.states.add(key)

    def associate_local_state(self, key, component):
        if key not in self._states:
            self._states[key] = set()
        self._states[key].add(component.id)
        component.states.add(key)

    def add_draggable(self, id):
        # TODO: eventually use this instead of a single global draggable state
        if id not in self._draggable_offset:
            self._draggable_offset[id] = Point2d(0, 0)
            self._last_drag_offset[id] = Point2d(0, 0)

    def set_drag_offset(self, id: str, offset: Point2d):
        self._last_drag_offset[id] = offset

    def commit_drag_offset(self, id: str):
        self._draggable_offset[id] += self._last_drag_offset[id]
        self._last_drag_offset[id] = Point2d(0, 0)

    def get_accumulated_drag_offset(self, id):
        if id in self._draggable_offset:
            return self._draggable_offset[id] + self._last_drag_offset[id]
        return None

    def add_window(self, window_id):
        if window_id not in self.windows:
            self.windows.add(window_id)

    def get_current_drag_offset(self, id):
        if id in self._last_drag_offset:
            return self._last_drag_offset[id]
        return None

    def set_highlighted(self, id, color = None):
        if id in self._id_to_node:
            self._highlighted[id] = color

    def set_unhighlighted(self, id):
        if id in self._highlighted:
            self._highlighted.pop(id)

    def scroll_y_increment(self, id, y):
        if id in self._id_to_node:
            if id not in self._scroll_regions:
                self.add_scroll_region(id)
            self._scroll_regions[id].scroll_y += y

    def scroll_x_increment(self, id, x):
        if id in self._id_to_node:
            if id not in self._scroll_regions:
                self.add_scroll_region(id)
            self._scroll_regions[id].scroll_x += x

    def get_text_mutation(self, id: str):
        if id in self._id_to_node:
            return self._text_mutations.get(id, "")
        return ""

    def set_text_mutation(self, id, text):
        if id in self._id_to_node:
            self._text_mutations[id] = str(text)

    def use_text_mutation(self, id, initial_text):
        if id not in self._text_mutations:
            self._text_mutations[id] = str(initial_text)
        return self._text_mutations[id]

    def set_style_mutation(self, id, style):
        if id in self._id_to_node:
            self._style_mutations[id] = style

    def get_ref_property_overrides(self, id):
        return self.ref_property_overrides.get(id)

    def set_ref_property_override(self, id, property_name, value):
        if not self.ref_property_overrides.get(id):
            self.ref_property_overrides[id] = {}
        self.ref_property_overrides[id][property_name] = value

    def clear_nodes(self):
        self._id_to_node.clear()
        self._staged_id_to_node.clear()
        self._buttons.clear()
        self._text_with_for_ids.clear()
        self.has_hit_priority_overlay = False
        entity_manager.synchronize_global_ids()

    def prepare_node_transition(self):
        self._staged_id_to_node = {}

    def commit_node_transition(self):
        self._id_to_node = self._staged_id_to_node
        self._staged_id_to_node = None
        entity_manager.synchronize_global_ids()

    def get_hover_links(self):
        return list(
            (b, b) for b in reversed(self._buttons)
        ) + list(
            self._text_with_for_ids.items()
        )

    # Scrollbar interaction state management
    def set_scrollbar_hover(self, node_id, axis="y"):
        self.scrollbar_hovered_id = node_id
        self.scrollbar_hovered_axis = axis

    def clear_scrollbar_hover(self):
        self.scrollbar_hovered_id = None
        self.scrollbar_hovered_axis = None

    def is_scrollbar_hovered(self, node_id, axis=None):
        if axis:
            return self.scrollbar_hovered_id == node_id and self.scrollbar_hovered_axis == axis
        return self.scrollbar_hovered_id == node_id

    def start_scrollbar_drag(self, node_id, mouse_pos, scroll_offset, axis="y"):
        self.scrollbar_dragging_id = node_id
        self.scrollbar_dragging_axis = axis
        if axis == "y":
            self.scrollbar_drag_start_y = mouse_pos
            self.scrollbar_drag_start_offset_y = scroll_offset
        else:
            self.scrollbar_drag_start_x = mouse_pos
            self.scrollbar_drag_start_offset_x = scroll_offset

    def clear_scrollbar_drag(self):
        self.scrollbar_dragging_id = None
        self.scrollbar_dragging_axis = None
        self.scrollbar_drag_start_y = None
        self.scrollbar_drag_start_offset_y = None
        self.scrollbar_drag_start_x = None
        self.scrollbar_drag_start_offset_x = None

    def is_scrollbar_dragging(self, node_id=None):
        if node_id:
            return self.scrollbar_dragging_id == node_id
        return self.scrollbar_dragging_id is not None

    def get_scrollbar_opacity(self, node_id):
        return self.scrollbar_opacity.get(node_id, 0.0)

    def set_scrollbar_opacity(self, node_id, opacity):
        self.scrollbar_opacity[node_id] = max(0.0, min(1.0, opacity))

    def clear_scrollbar_fade_job(self, node_id):
        job = self.scrollbar_fade_jobs.pop(node_id, None)
        if job:
            cron.cancel(job)

    def clear_scrollbar_idle_job(self, node_id):
        job = self.scrollbar_idle_jobs.pop(node_id, None)
        if job:
            cron.cancel(job)

    # Resize interaction state management
    def start_resize_drag(self, node_id, edge, mouse_pos, start_rect):
        self.resize_dragging_id = node_id
        self.resize_edge = edge
        self.resize_start_pos = mouse_pos
        self.resize_start_rect = start_rect
        self.resize_ghost_rect = Rect(start_rect.x, start_rect.y, start_rect.width, start_rect.height)

    def clear_resize_drag(self):
        self.resize_dragging_id = None
        self.resize_edge = None
        self.resize_start_pos = None
        self.resize_start_rect = None
        self.resize_ghost_rect = None

    def is_resize_dragging(self, node_id=None):
        if node_id:
            return self.resize_dragging_id == node_id
        return self.resize_dragging_id is not None

    def set_resize_edge_hover(self, node_id, edge):
        self.resize_edge_hovered = (node_id, edge)

    def clear_resize_edge_hover(self):
        self.resize_edge_hovered = None

    def get_interaction_links(self):
        return list(
            (b, b) for b in self._buttons
        ) + list(
            self._text_with_for_ids.items()
        )

    def clear(self):
        for input_data in list(self._inputs.values()):
            if input_data:
                input_data.input.unregister("label", input_data.on_change)
                input_data.input.hide()
                input_data.input = None

        for job in list(self.unhighlight_jobs.values()):
            if job:
                cron.cancel(job[0])

        self._buttons.clear()
        self._components.clear()
        self._staged_components.clear()
        self.decoration_renders.clear()
        self._draggable_offset.clear()
        self._last_drag_offset.clear()
        self._highlighted.clear()
        self._inputs.clear()
        self._scroll_regions.clear()
        self._scrollable.clear()
        for job in list(self.scrollbar_fade_jobs.values()):
            if job:
                cron.cancel(job)
        for job in list(self.scrollbar_idle_jobs.values()):
            if job:
                cron.cancel(job)
        self.scrollbar_fade_jobs.clear()
        self.scrollbar_idle_jobs.clear()
        self.scrollbar_opacity.clear()
        self._states.clear()
        self._style_mutations.clear()
        self._text_mutations.clear()
        self.windows.clear()
        self.resizable_nodes.clear()
        self.unhighlight_jobs.clear()
        self.ref_property_overrides.clear()
        self.new_component_ids.clear()
        self.removed_component_ids.clear()
        self.clear_resize_drag()
        self.resize_edge_hovered = None
        self.resize_original_constraints.clear()
        self.clear_nodes()

class RenderCauseState(RenderCauseStateType):
    def __init__(self):
        self.state = None

    def state_change(self):
        self.state = "state"

    def ref_change(self):
        self.state = "ref"

    def set_text_change(self):
        self.state = "text"

    def highlight_change(self):
        self.state = "highlight"

    def input_focus_change(self):
        self.state = "input_focus"

    def set_is_dragging(self):
        self.state = "dragging"

    def is_dragging(self):
        return self.state == "dragging"

    def set_is_drag_end(self):
        self.state = "drag_end"

    def is_drag_end(self):
        return self.state == "drag_end"

    def is_state_change(self):
        return self.state == "state"

    def is_input_focus_change(self):
        return self.state == "input_focus"

    def is_ref_change(self):
        return self.state == "ref"

    def is_highlight_change(self):
        return self.state == "highlight"

    def is_text_change(self):
        return self.state == "text"

    def clear(self):
        self.state = None

    def __str__(self):
        return self.state

class Tree(TreeType):
    Canvas = RealCanvas # override for testing
    def __init__(
            self,
            tree_constructor: callable,
            hashed_tree_constructor: str,
            props: dict[str, Any] = {},
            initial_state = dict[str, Any]
        ):
        self.absolute_nodes = []
        self._active_modal_node_ref: Optional[weakref.ReferenceType[NodeType]] = None
        self._cached_modal_scope_ids: Optional[set[str]] = None
        self._prev_active_modal_id: Optional[str] = None
        self.canvas_base = None
        self.canvas_blockable = []
        self.canvas_decorator = None
        self._decorator_freeze_pending_job = None
        self._last_decorator_freeze_ts = 0.0
        self.current_base_canvas = None
        self.cursor = None
        self.cursor_v2 = None
        self.cursor_refresh_job = None
        self.cursor_refresh_rate = DEFAULT_CURSOR_REFRESH_RATE
        self.cursor_position = self.get_cursor_position()
        self.hover_validation_job = None
        self.last_mouse_event_time = 0
        self.effects = []
        self.destroying = False
        self.unmounting = False
        self._unmount_complete = False
        self.drag_end_phase = False
        self._text_selecting_node = None
        self._text_selected_nodes = []
        self._input_click_count = 0
        self._input_last_click_time = 0
        self._input_last_click_x = 0
        self._input_last_click_y = 0
        self.draggable_node = False
        self.draggable_node_delta_pos = None
        self.drag_handle_node = None
        self.processing_states = set()
        self.fixed_nodes = []
        self.guid = uuid.uuid4().hex
        self.hashed_tree_constructor = hashed_tree_constructor
        self.has_cursor_node = False
        self.interactive_node_list = []
        self.is_key_controls_init = False
        self.is_blockable_canvas_init = False
        self.is_mounted = False
        self.last_blockable_rects = []
        self.last_base_snapshot = None
        self.last_hints_snapshot = None
        self.lock = threading.Lock()
        self.meta_state = MetaState()
        self.name = tree_constructor.__name__
        self.props = props
        self.render_manager = RenderManager(self)
        self.render_cause = RenderCauseState()
        self.render_list = []
        self.render_layers = []
        self._tree_constructor = tree_constructor
        self.render_version = 2
        self.render_debounce_job = None
        self.redistribute_box_model = False
        self.root_node = None
        # Set by render(), drained by _commit_pending_render at the top of
        # the next paint. Deferred so init_tree_constructor can't mutate
        # self.root_node mid-pipeline when a state change fires synchronously
        # from queue_render.on_start during an in-flight paint.
        self._pending_render = False
        self.scroll_amount_per_tick = settings.get("user.ui_elements_scroll_speed")
        self._scroll_anim_job = None
        smooth_duration = settings.get("user.ui_elements_smooth_scroll_duration", 80)
        if smooth_duration > 0:
            n = smooth_duration / 16.0
            self._smooth_scroll_factor = 1.0 - (0.01 ** (1.0 / n))
        else:
            self._smooth_scroll_factor = 0
        self.show_hints = False
        self.style: Style = None
        self.transition_manager = TransitionManager(self)

        # Load scale from storage per tree, fallback to settings
        saved_scales = storage.get("ui_elements", {}).get("scale_per_tree", {})
        default_scale = settings.get("user.ui_elements_scale", 1.0)
        self.scale = saved_scales.get(hashed_tree_constructor, default_scale)

        if not store.trees:
            store.scale = settings.get("user.ui_elements_scale", 1.0)
        state_manager.init_states(initial_state)
        self.init_tree_constructor()
        state_manager.increment_ref_count_trees()

    def __del__(self):
        state_manager.decrement_ref_count_trees()

    @property
    def id(self):
        return self.root_node.id if self.root_node else None

    def reset_cursor(self):
        if self.cursor is None:
            self.cursor = Cursor(self.root_node.boundary_rect)
            self.cursor_v2 = CursorV2(Point2d(
                self.root_node.boundary_rect.x,
                self.root_node.boundary_rect.y
            ))
        else:
            self.cursor.reset()
            self.cursor_v2.reset()

    def auto_wrap_root_node(self):
        if self.root_node.element_type not in ["screen", "active_window"]:
            from .node_root import NodeRoot
            from ..properties import NodeRootProperties

            child_props = self.root_node.properties
            has_pct = (isinstance(child_props.width, str) and "%" in child_props.width) or \
                      (isinstance(child_props.height, str) and "%" in child_props.height)

            root = NodeRoot("screen", NodeRootProperties(
                justify_content="center",
                align_items="stretch" if has_pct else "center",
            ))
            root.add_child(self.root_node)
            self.root_node = root

    def get_cursor_position(self) -> Point2d:
        try:
            x, y = ctrl.mouse_pos()
            return Point2d(x, y)
        except:
            return Point2d(0, 0)

    def start_cursor_refresh_cycle(self, refresh_rate: int = DEFAULT_CURSOR_REFRESH_RATE):
        if self.cursor_refresh_job is None:
            self.cursor_refresh_rate = refresh_rate

            def cursor_refresh_callback():
                if not self.destroying and self.has_cursor_node:
                    self.update_cursor_positions()
                    self.render_manager.render_cursor_update()

            self.cursor_refresh_job = cron.interval(f"{refresh_rate}ms", cursor_refresh_callback)

    def stop_cursor_refresh_cycle(self):
        if self.cursor_refresh_job:
            cron.cancel(self.cursor_refresh_job)
            self.cursor_refresh_job = None

    def update_cursor_positions(self):
        self.cursor_position = self.get_cursor_position()

    def setup_cursor_refresh_cycle(self):
        if self.has_cursor_node:
            self.start_cursor_refresh_cycle(self.cursor_refresh_rate)
        else:
            self.stop_cursor_refresh_cycle()

    def check_for_stale_hover(self):
        if not self.destroying:
            if state_manager.are_mouse_events_disabled() or self.render_manager.is_rendering:
                self.schedule_hover_validation()
                return
            time_since_last_event = time.time() - self.last_mouse_event_time
            if time_since_last_event >= 0.2:
                if self.validate_hover_state():
                    self.render_manager.render_mouse_highlight()
                self.hover_validation_job = None
            else:
                self.schedule_hover_validation()

    def schedule_hover_validation(self):
        if self.hover_validation_job:
            cron.cancel(self.hover_validation_job)

        self.hover_validation_job = cron.after("100ms", self.check_for_stale_hover)

    def init_tree_constructor(self):
        state_manager.set_processing_tree(self)
        try:
            try:
                if len(inspect.signature(self._tree_constructor).parameters) > 0:
                    if self.props and not isinstance(self.props, dict):
                        raise Exception("props passed to actions.user.ui_elements_show should be a dictionary, and the receiving function should accept a single argument `props`")
                    self.root_node = self._tree_constructor(self.props or {})
                else:
                    self.root_node = self._tree_constructor()
                self.absolute_nodes.clear()
                self.fixed_nodes.clear()
                if not isinstance(self.root_node, NodeType):
                    raise Exception("actions.user.ui_elements_show was passed a function that didn't return any elements. Be sure to return an element tree composed of `screen`, `div`, `text`, etc.")
                self.auto_wrap_root_node()
            except Exception as e:
                from .error_boundary import build_error_card
                tb_str = traceback.format_exc()
                label = getattr(self._tree_constructor, "__qualname__", None) or "tree"
                print(f"ui_elements: error while rendering tree '{label}':\n{tb_str}")
                # the error card must not be able to crash the render itself
                try:
                    self.root_node = build_error_card(label, type(e).__name__, str(e), tb_str)
                    self.absolute_nodes.clear()
                    self.fixed_nodes.clear()
                    self.auto_wrap_root_node()
                except Exception:
                    self.root_node = None
                    print(f"ui_elements: error card failed to render for '{label}':\n{traceback.format_exc()}")
        finally:
            state_manager.set_processing_tree(None)

    def test(self, node: NodeType):
        if getattr(node, "text", None):
            print(node.text)
        if hasattr(node.box_model, "calculated_margin_size"):
            print('calculated_margin_size', node.box_model.calculated_margin_size)
        for child in node.get_children_nodes():
            self.test(child)

    def compute_clip_regions_cache(self):
        def compute_for_node(node: NodeType):
            # Defensive: skip Components that somehow weren't resolved by
            # init_node_hierarchy. They have no compute_clip_regions_cache and
            # no children, so just walking past them is safe.
            if isinstance(node, ComponentType):
                return
            node.compute_clip_regions_cache()
            for child in node.get_children_nodes():
                compute_for_node(child)

        compute_for_node(self.root_node)

    def nonlayout_flow(self):
        # Bound absolute/fixed nodes to the viewport so a tall subtree can't
        # grow off-screen. constrain_size only applies min(content, available),
        # so nodes that already fit are unaffected.
        viewport = None
        if self.root_node and self.root_node.boundary_rect:
            viewport = Size2d(
                int(self.root_node.boundary_rect.width),
                int(self.root_node.boundary_rect.height),
            )
        for node in self.absolute_nodes + self.fixed_nodes:
            node: NodeType = node()
            if node and node.tree == self:
                relative_positional_node: NodeType = node.relative_positional_node()
                node.v2_measure_intrinsic_size(self.current_base_canvas)
                node.v2_grow_size()
                node.v2_constrain_size(viewport.copy() if viewport else None)
                cursor = CursorV2(Point2d(
                    relative_positional_node.box_model.margin_pos.x,
                    relative_positional_node.box_model.margin_pos.y
                ))
                node.v2_layout(cursor)

    def build_base_render_layers(self):
        self.render_list.clear()
        self.render_layers.clear()
        self.root_node.v2_build_render_list()

        # Group by (z_index, z_subindex)
        layer_map = defaultdict(list)
        for r in self.render_list:
            z_index = r.node.properties.z_index or 0
            z_subindex = r.node.z_subindex or 0
            layer_map[(z_index, z_subindex)].append(r)

        # Create and sort layers
        self.render_layers = [
            RenderLayer(z_index=z, z_subindex=s, items=items)
            for (z, s), items in layer_map.items()
        ]
        self.render_layers.sort(key=lambda l: (l.z_index, l.z_subindex))

    def move_canvas(self, canvas: SkiaCanvas):
        offset = self.meta_state.get_current_drag_offset(self.draggable_node.id)
        transforms = RenderTransforms(offset=offset)
        for layer in self.render_layers:
            layer.draw_to_canvas(canvas, transforms)

    def commit_base_canvas(self):
        cursor_transforms = RenderTransforms(offset=self.cursor_position) \
            if self.has_cursor_node \
            else None

        for layer in self.render_layers:
            layer.draw_to_canvas(self.current_base_canvas, cursor_transforms)

    def apply_clip_regions(self, canvas: SkiaCanvas, node: NodeType, transforms: RenderTransforms = None):
        clip_count = 0
        if node.clip_nodes:
            for clip_ref in node.clip_nodes:
                clip_node = clip_ref()
                if clip_node and clip_node.box_model:
                    canvas.save()
                    clip_count += 1

                    rect = clip_node.box_model.padding_rect
                    if transforms and transforms.offset:
                        rect = rect.copy()
                        rect.x += transforms.offset.x
                        rect.y += transforms.offset.y

                    if clip_node.properties.has_border_radius():
                        border_radius = clip_node.properties.get_border_radius()
                        if border_radius.is_uniform():
                            canvas.clip_rrect(RoundRect.from_rect(rect, x=border_radius.top_left, y=border_radius.top_left))
                        else:
                            path = draw_manual_rounded_rect_path(rect, border_radius)
                            canvas.clip_path(path)
                    else:
                        canvas.clip_rect(rect)
        return clip_count

    def restore_clip_regions(self, canvas: SkiaCanvas, clip_count: int):
        for _ in range(clip_count):
            canvas.restore()

    def draw_decoration_renders(self, canvas: SkiaCanvas, transforms: RenderTransforms = None):
        # The decorator canvas paints on top of the base canvas, so when a
        # modal is open we must skip decoration renders for nodes outside the
        # modal subtree. Otherwise input cursors/text and open select
        # dropdowns from underneath the modal show through on top of it.
        modal_scope = self.get_modal_scope_ids()
        for id in list(self.meta_state.decoration_renders.keys()):
            if id in self.meta_state.id_to_node:
                if modal_scope is not None and id not in modal_scope:
                    continue
                node = self.meta_state.id_to_node[id]
                clip_count = self.apply_clip_regions(canvas, node, transforms)
                node.v2_render_decorator(canvas, transforms)
                self.restore_clip_regions(canvas, clip_count)

    def draw_scrollbars(self, canvas: SkiaCanvas, transforms: RenderTransforms = None):
        # Decorator canvas paints on top of the base canvas, so background
        # scrollbars would otherwise render in front of an open modal.
        modal_scope = self.get_modal_scope_ids()
        for id in list(self.meta_state.scrollable.keys()):
            if id in self.meta_state.id_to_node:
                if modal_scope is not None and id not in modal_scope:
                    continue
                node = self.meta_state.id_to_node[id]
                if hasattr(node, "render_scroll_bar"):
                    node.render_scroll_bar(canvas, transforms)

    def compute_scroll_button_overlays(self):
        """Walk scrollable containers and compute floating scroll button overlays
        for any direction with remaining scroll room."""
        self.meta_state.scroll_button_overlays.clear()
        default_size = scale_value(DEFAULT_SCROLL_BUTTON_SIZE)
        inset = scale_value(DEFAULT_SCROLL_BUTTON_INSET)
        bar_width = scale_value(DEFAULT_SCROLL_BAR_WIDTH)

        for sid in list(self.meta_state.scrollable.keys()):
            node = self.meta_state.id_to_node.get(sid)
            if not node or not node.box_model:
                continue
            if getattr(node.properties, "scroll_buttons", True) is False:
                continue
            style = getattr(node.properties, "scroll_buttons_style", None) or {}
            size = scale_value(style.get("size", DEFAULT_SCROLL_BUTTON_SIZE))

            sdata = self.meta_state.scrollable[sid]
            pad = node.box_model.padding_rect

            y_overflow = sdata.max_height > sdata.view_height
            x_overflow = sdata.max_width > sdata.view_width

            if y_overflow:
                x = pad.x + pad.width - size - inset - bar_width
                if sdata.offset_y < 0:
                    self._add_scroll_button_overlay(sid, "up", "y", 1,
                        Rect(x, pad.y + inset, size, size), style)
                if sdata.offset_y > (sdata.view_height - sdata.max_height):
                    self._add_scroll_button_overlay(sid, "down", "y", -1,
                        Rect(x, pad.y + pad.height - size - inset, size, size), style)

            if x_overflow:
                y = pad.y + pad.height - size - inset - bar_width
                left_x = pad.x + inset
                right_x = pad.x + pad.width - size - inset
                # Avoid colliding with the down button when both axes scroll
                if y_overflow:
                    right_x -= (size + inset)
                if sdata.offset_x < 0:
                    self._add_scroll_button_overlay(sid, "left", "x", 1,
                        Rect(left_x, y, size, size), style)
                if sdata.offset_x > (sdata.view_width - sdata.max_width):
                    self._add_scroll_button_overlay(sid, "right", "x", -1,
                        Rect(right_x, y, size, size), style)

    def _add_scroll_button_overlay(self, container_id, role, axis, direction, rect, style=None):
        synthetic_id = f"__sb__{container_id}__{role}"
        self.meta_state.scroll_button_overlays[synthetic_id] = ScrollButtonOverlay(
            container_id=container_id,
            role=role,
            axis=axis,
            direction=direction,
            rect=rect,
            synthetic_id=synthetic_id,
            style=style,
        )

    def draw_scroll_button_overlays(self, canvas: SkiaCanvas, transforms: RenderTransforms = None):
        if not self.meta_state.scroll_button_overlays:
            return
        modal_scope = self.get_modal_scope_ids()
        hovered = self.meta_state.scroll_button_hovered_id
        for overlay in list(self.meta_state.scroll_button_overlays.values()):
            if modal_scope is not None and overlay.container_id not in modal_scope:
                continue
            style = overlay.style or {}
            background_color = style.get("background_color", DEFAULT_SCROLL_BUTTON_BACKGROUND_COLOR)
            hover_background_color = style.get("hover_background_color", DEFAULT_SCROLL_BUTTON_HOVER_BACKGROUND_COLOR)
            border_color = style.get("border_color", DEFAULT_SCROLL_BUTTON_BORDER_COLOR)
            icon_color = style.get("icon_color", DEFAULT_SCROLL_BUTTON_ICON_COLOR)

            r = overlay.rect.copy()
            if transforms and transforms.offset:
                r.x += transforms.offset.x
                r.y += transforms.offset.y
            cx = r.x + r.width / 2
            cy = r.y + r.height / 2
            radius = r.width / 2

            canvas.paint.antialias = True
            canvas.paint.style = canvas.paint.Style.FILL
            canvas.paint.color = (hover_background_color
                if overlay.synthetic_id == hovered else background_color)
            canvas.draw_circle(cx, cy, radius)

            canvas.paint.style = canvas.paint.Style.STROKE
            canvas.paint.stroke_width = scale_value(1)
            canvas.paint.color = border_color
            canvas.draw_circle(cx, cy, radius)

            # Chevron
            canvas.paint.color = icon_color
            canvas.paint.stroke_width = scale_value(2)
            canvas.paint.style = canvas.paint.Style.STROKE
            arm = radius * 0.36
            depth = radius * 0.22
            if overlay.role == "up":
                canvas.draw_line(cx - arm, cy + depth / 2, cx, cy - depth / 2)
                canvas.draw_line(cx, cy - depth / 2, cx + arm, cy + depth / 2)
            elif overlay.role == "down":
                canvas.draw_line(cx - arm, cy - depth / 2, cx, cy + depth / 2)
                canvas.draw_line(cx, cy + depth / 2, cx + arm, cy - depth / 2)
            elif overlay.role == "left":
                canvas.draw_line(cx + depth / 2, cy - arm, cx - depth / 2, cy)
                canvas.draw_line(cx - depth / 2, cy, cx + depth / 2, cy + arm)
            elif overlay.role == "right":
                canvas.draw_line(cx - depth / 2, cy - arm, cx + depth / 2, cy)
                canvas.draw_line(cx + depth / 2, cy, cx - depth / 2, cy + arm)

    def scroll_button_overlay_at(self, gpos):
        """Return the scroll button overlay at the given position, or None.
        When a modal is open, only overlays inside the modal subtree are returned."""
        modal_scope = self.get_modal_scope_ids()
        for overlay in self.meta_state.scroll_button_overlays.values():
            if not overlay.rect.contains(gpos):
                continue
            if modal_scope is not None and overlay.container_id not in modal_scope:
                continue
            return overlay
        return None

    def on_draw_decorator_canvas(self, canvas: SkiaCanvas):
        completing_task = False
        try:
            if not self.render_manager.is_destroying:
                draw_canvas = canvas
                offset = self.meta_state.get_current_drag_offset(self.draggable_node.id) \
                    if (self.render_manager.is_dragging() or self.render_manager.is_drag_start()) \
                    else Point2d(0, 0)
                transforms = None
                if offset:
                    transforms = RenderTransforms(offset=offset)
                state_manager.set_processing_tree(self)
                try:
                    if self.interactive_node_list and self.render_manager.render_cause in (
                        RenderCause.STATE_CHANGE, RenderCause.REF_CHANGE
                    ):
                        self.reconcile_mouse_highlight()
                    self.draw_decoration_renders(draw_canvas, transforms)
                    if self.meta_state.scrollable:
                        self.draw_scrollbars(draw_canvas, transforms)
                        self.compute_scroll_button_overlays()
                        self.draw_scroll_button_overlays(draw_canvas, transforms)
                    elif self.meta_state.scroll_button_overlays:
                        self.meta_state.scroll_button_overlays.clear()
                    self.draw_highlight_overlays(draw_canvas, transforms.offset)
                    self.draw_resize_edge_highlight(draw_canvas, transforms.offset)
                    self.draw_resize_ghost(draw_canvas)
                    canvas.paint.color = "FFFFFF"
                    self.draw_text_mutations(draw_canvas, Point2d(0, 0)) # Why does 0,0 work here?
                    if self.interactive_node_list or self.draggable_node:
                        if state_manager.is_focus_visible():
                            self.draw_focus_outline(draw_canvas, offset)
                        if self.show_hints:
                            self.draw_hints(draw_canvas, transforms)
                    self.init_key_controls()
                    self.draw_blockable_canvases()
                    completing_task = self.render_manager.should_complete_on_decorator_draw()
                    if completing_task or not self.render_manager.is_rendering:
                        self.on_fully_rendered()
                finally:
                    state_manager.set_processing_tree(None)
                if completing_task:
                    self.finish_current_render()
                elif not self.render_manager.is_rendering:
                    # drain anything stranded while idle
                    self.render_manager.process_next_render()
        except Exception as e:
            print(f"Error during decorator canvas rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def on_draw_base_canvas_dragging(self, canvas: SkiaCanvas):
        try:
            self.move_canvas(canvas)
            self.move_inputs()
            # Raise on the drag-start tick only, not every dragging tick:
            # focused= is an OS focus call and doing it ~100Hz across a drag
            # is laggy. Talon sinks the canvas once at the start of the drag,
            # so a single raise is enough to ride out the whole drag.
            if self.render_manager.is_drag_start():
                self._raise_dragging_canvases_to_top()
        except Exception as e:
            print(f"Error during dragging rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def on_draw_base_canvas_drag_end(self, canvas: SkiaCanvas):
        try:
            self.root_node.v2_reposition()
            self.compute_clip_regions_cache()
            self.build_base_render_layers()
            self.commit_base_canvas()
            self._raise_dragging_canvases_to_top()
        except Exception as e:
            print(f"Error during drag end rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def _raise_dragging_canvases_to_top(self):
        # Talon sinks a draggable canvas below other on-screen canvases
        # (other ui_elements trees and this tree's own hint/decorator layer)
        # when it becomes the drag source. Re-assert focus to raise back to
        # the top. Order matters: focused=True acts as "raise to top of
        # stack", so raise base first and decorator second so the decorator
        # ends up on top of the base (preserving the in-tree paint order:
        # base < decorator).
        if self.canvas_base:
            try:
                self.canvas_base.focused = True
            except Exception:
                pass
        if self.canvas_decorator:
            try:
                self.canvas_decorator.focused = True
            except Exception:
                pass

    def on_draw_base_canvas_scroll(self, canvas: SkiaCanvas):
        try:
            self.reset_cursor()
            self.root_node.v2_layout(self.cursor_v2)
            self.nonlayout_flow()
            self.compute_clip_regions_cache()
            self.build_base_render_layers()
            self.commit_base_canvas()
        except Exception as e:
            print(f"Error during scroll rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def on_draw_base_canvas_cursor_update(self, canvas: SkiaCanvas):
        try:
            self.nonlayout_flow()
            self.build_base_render_layers()
            self.commit_base_canvas()
        except Exception as e:
            print(f"Error during cursor update rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def on_draw_base_canvas_animation_frame(self, canvas: SkiaCanvas):
        try:
            self.reset_cursor()
            self.root_node.v2_measure_intrinsic_size(canvas)
            self.root_node.v2_grow_size()
            self.root_node.v2_constrain_size()
            self.root_node.v2_layout(self.cursor_v2)
            self.nonlayout_flow()
            self.compute_clip_regions_cache()
            self.build_base_render_layers()
            self.commit_base_canvas()
        except Exception as e:
            print(f"Error during animation frame rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def on_draw_base_canvas_default(self, canvas: SkiaCanvas):
        try:
            self.meta_state.clear_nodes()
            self.reset_cursor()
            self.init_node_hierarchy(self.root_node)
            self._handle_modal_open_transition()
            self.transition_manager.apply_pending_mount_values()
            self.consume_components()
            self.consume_effects()
            self.root_node.v2_measure_intrinsic_size(canvas)
            self.root_node.v2_grow_size()
            self.root_node.v2_constrain_size()
            self.root_node.v2_layout(self.cursor_v2)
            self.nonlayout_flow()
            self.compute_clip_regions_cache()
            self.build_base_render_layers()
            self.commit_base_canvas()
            # Start mount animations immediately after base canvas commits,
            # since mount_style values are already visible at this point.
            # Waiting for the decorator canvas roundtrip adds ~150-300ms delay.
            if not self.is_mounted:
                self.transition_manager.start_mount_animations()
            # Set up cursor refresh cycle after tree is fully processed
            self.setup_cursor_refresh_cycle()
        except Exception as e:
            print(f"Error during base canvas draw: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def on_draw_base_canvas(self, canvas: SkiaCanvas):
        if not self.render_manager.is_destroying:
            self.current_base_canvas = canvas
            state_manager.set_processing_tree(self)
            try:
                self._commit_pending_render()
                dragging = self.render_manager.is_dragging() or self.render_manager.is_drag_start()
                if dragging:
                    self.on_draw_base_canvas_dragging(canvas)
                elif self.is_drag_end():
                    self.on_draw_base_canvas_drag_end(canvas)
                elif self.render_manager.is_scrolling() or self.render_manager.is_scrollbar_dragging():
                    self.on_draw_base_canvas_scroll(canvas)
                elif self.render_manager.is_animation_frame():
                    self.on_draw_base_canvas_animation_frame(canvas)
                elif self.render_manager.is_cursor_update() and not (self.render_manager.render_cause == RenderCause.STATE_CHANGE or self.render_manager.render_cause == RenderCause.REF_CHANGE):
                    self.on_draw_base_canvas_cursor_update(canvas)
                else:
                    self.on_draw_base_canvas_default(canvas)

                if not dragging:
                    self.show_inputs()
                if self.render_manager.is_rendering:
                    self.render_manager.expect_decorator_completion()
                self.render_decorator_canvas()
            except Exception as e:
                # _commit_pending_render runs user component code - an uncaught
                # raise here would leave the task current and wedge the queue
                print(f"Error during base canvas draw: {e}")
                log_trace()
                self.finish_current_render()
                self.destroy()
            finally:
                state_manager.set_processing_tree(None)

    def draw_highlight_overlay(self, canvas: SkiaCanvas, node: NodeType, offset: Point2d, color: str = None):
        transforms = RenderTransforms(offset=offset) if offset.x or offset.y else None
        clip_count = self.apply_clip_regions(canvas, node, transforms)

        rect = node.box_model.visible_rect
        rect.x += offset.x
        rect.y += offset.y
        canvas.paint.color = color or node.properties.highlight_color

        if rect:
            draw_rect(canvas, rect, node.properties.get_border_radius())

        self.restore_clip_regions(canvas, clip_count)

    def draw_highlight_overlays(self, canvas: SkiaCanvas, offset: Point2d):
        canvas.paint.style = canvas.paint.Style.FILL
        for id, color in list(self.meta_state.highlighted.items()):
            # migrating to new highlight system - decoration renders
            # so if we have decoration renders, prioritize that instead
            if not id in self.meta_state.decoration_renders and id in self.meta_state.id_to_node:
                node = self.meta_state.id_to_node[id]
                self.draw_highlight_overlay(canvas, node, offset, color)

    def draw_text_mutation(self, canvas: SkiaCanvas, node: NodeType, id: str, offset: Point2d):
        transforms = RenderTransforms(offset=offset) if offset.x or offset.y else None
        clip_count = self.apply_clip_regions(canvas, node, transforms)

        x, y = node.cursor_pre_draw_text
        x += offset.x
        y += offset.y
        text_value = self.meta_state.get_text_mutation(id)

        if node.text_multiline and "\n" not in str(text_value):
            # set_text changed to single line, draw simple
            draw_text_simple(canvas, text_value, node.properties.color, node.properties, x, y)
        elif node.text_multiline:
            gap = node.properties.gap or 0
            line_h = node.text_line_height + gap
            for i, (line_text, _) in enumerate(node.text_multiline):
                if line_text:
                    draw_text_simple(canvas, line_text, node.properties.color, node.properties, x, y + line_h * i)
        else:
            draw_text_simple(canvas, text_value, node.properties.color, node.properties, x, y)

        self.restore_clip_regions(canvas, clip_count)

    def draw_text_mutations(self, canvas: SkiaCanvas, offset: Point2d):
        modal_scope = self.get_modal_scope_ids()
        for id, text_value in list(self.meta_state.text_mutations.items()):
            if id in self.meta_state.id_to_node:
                if modal_scope is not None and id not in modal_scope:
                    continue
                node = self.meta_state.id_to_node[id]
                self.draw_text_mutation(canvas, node, id, offset)

    def finish_current_render(self):
        self.render_manager.finish_current_render()

    def draw_hints(self, canvas: SkiaCanvas, transforms: RenderTransforms = None):
        if not (self.meta_state.inputs or self.meta_state.buttons or self.interactive_node_list or self.meta_state.scroll_button_overlays):
            return
        hint_tag_enable()
        hint_generator = get_hint_generator()
        nodes = list(self.meta_state.id_to_node.values())

        # Modal scope: when a modal is open, only its subtree gets hints.
        modal_scope_ids = self.get_modal_scope_ids()
        if modal_scope_ids is not None:
            nodes = [n for n in nodes if n.id in modal_scope_ids]

        # Scan once for open decoration-render subtrees (e.g. select dropdown).
        decoration_rects = None
        decoration_node_ids = None
        for n in nodes:
            if n.uses_decoration_render and n.box_model:
                if decoration_rects is None:
                    decoration_rects = []
                    decoration_node_ids = set()
                decoration_rects.append(n.box_model.padding_rect)
                stack = [n]
                while stack:
                    cur = stack.pop()
                    decoration_node_ids.add(id(cur))
                    stack.extend(getattr(cur, 'children_nodes', None) or ())

        # Fast path: no decoration render active — original draw-all behavior.
        if decoration_rects is None:
            for node in nodes:
                if getattr(node, 'hintable', node.interactive) and not getattr(node, 'disabled', False):
                    draw_hint(canvas, node, hint_generator(node), transforms=transforms)
            for overlay in list(self.meta_state.scroll_button_overlays.values()):
                draw_scroll_button_hint(canvas, overlay, transforms=transforms)
            return

        # Decoration-aware path: hide hints that would land inside a decoration
        # subtree's rect, and defer the subtree's own hints so they paint last.
        deferred = []
        for node in nodes:
            if not getattr(node, 'hintable', node.interactive) or getattr(node, 'disabled', False):
                continue
            if id(node) in decoration_node_ids:
                deferred.append(node)
                continue
            bm = node.box_model
            if bm:
                r = bm.padding_rect
                occluded = False
                for d in decoration_rects:
                    if not (r.x + r.width <= d.x or d.x + d.width <= r.x or
                            r.y + r.height <= d.y or d.y + d.height <= r.y):
                        occluded = True
                        break
                if occluded:
                    continue
            draw_hint(canvas, node, hint_generator(node), transforms=transforms)
        for overlay in list(self.meta_state.scroll_button_overlays.values()):
            draw_scroll_button_hint(canvas, overlay, transforms=transforms)
        for node in deferred:
            draw_hint(canvas, node, hint_generator(node), transforms=transforms)

    def refresh_decorator_canvas(self):
        if self.canvas_decorator:
            self.request_decorator_freeze()

    def highlight_forced(self, id: str, color: str = None):
        self.render_cause.highlight_change()
        self.meta_state.set_highlighted(id, color)
        self.request_decorator_freeze()

    def _retarget_fading_highlight(self, id: str, color: str = None):
        """Reverse a fade-out on re-highlight. The id stays in highlighted
        during the fade, so the guard would otherwise drop it."""
        anim = self.transition_manager.highlight_anims.get(id)
        if anim and anim.direction == "out":
            node = self.meta_state.id_to_node.get(id)
            if node and node.properties.transition and node.properties.highlight_style:
                if color is not None:
                    self.meta_state.set_highlighted(id, color)
                self.transition_manager.start_highlight(id, node, "in")
                return True
        return False

    def highlight_no_render(self, id: str, color: str = None):
        if id in self.meta_state.highlighted:
            self._retarget_fading_highlight(id, color)
            return
        self.meta_state.set_highlighted(id, color)
        node = self.meta_state.id_to_node.get(id)
        if node and node.properties.transition and node.properties.highlight_style:
            self.transition_manager.start_highlight(id, node, "in")

    def highlight(self, id: str, color: str = None):
        if id in self.meta_state.highlighted:
            if self._retarget_fading_highlight(id, color):
                self.request_decorator_freeze()
            return

        self.render_cause.highlight_change()
        self.meta_state.set_highlighted(id, color)
        node = self.meta_state.id_to_node.get(id)
        if node and node.properties.transition and node.properties.highlight_style:
            self.transition_manager.start_highlight(id, node, "in")
        self.request_decorator_freeze()

    def unhighlight_no_render(self, id: str):
        if id in self.meta_state.highlighted:
            node = self.meta_state.id_to_node.get(id)
            if node and node.properties.transition and node.properties.highlight_style:
                self.transition_manager.start_highlight(id, node, "out")
            else:
                self.meta_state.set_unhighlighted(id)

            job = self.meta_state.unhighlight_jobs.pop(id, None)
            if job:
                cron.cancel(job[0])

    def unhighlight(self, id: str):
        if id in self.meta_state.highlighted:
            self.render_cause.highlight_change()
            node = self.meta_state.id_to_node.get(id)
            if node and node.properties.transition and node.properties.highlight_style:
                self.transition_manager.start_highlight(id, node, "out")
            else:
                self.meta_state.set_unhighlighted(id)

            job = self.meta_state.unhighlight_jobs.pop(id, None)
            if job:
                cron.cancel(job[0])

            self.request_decorator_freeze()

    def highlight_briefly(self, id: str, color: str = None, duration: int = DEFAULT_HIGHLIGHT_DURATION_MS):
        if id in self.meta_state.unhighlight_jobs:
            job, _ = self.meta_state.unhighlight_jobs.pop(id)
            cron.cancel(job)
        self.highlight(id, color)
        def pending_unhighlight():
            # pop first - unhighlight() early-returns if already unhighlighted, stranding the entry
            self.meta_state.unhighlight_jobs.pop(id, None)
            self.unhighlight(id)
        self.meta_state.unhighlight_jobs[id] = (cron.after(f"{duration}ms", pending_unhighlight), pending_unhighlight)

    def move_inputs(self):
        offset = self.meta_state.get_current_drag_offset(self.draggable_node.id)
        for id, input_data in list(self.meta_state.inputs.items()):
            if input_data.input:
                input_data.input.rect = Rect(
                    input_data.rect.x + offset.x,
                    input_data.rect.y + offset.y,
                    input_data.rect.width,
                    input_data.rect.height
                )

    def show_inputs(self):
        if self.meta_state.inputs and not self.is_mounted:
            focused_input = None

            for id, input_data in list(self.meta_state.inputs.items()):
                if state_manager.is_focused(id):
                    focused_input = input_data.input
                    continue
                if input_data.input:
                    input_data.input.show()

            if focused_input:
                focused_input.show()

    def on_key(self, e):
        key_string = e.key.lower() if e.key is not None else ""
        for mod in e.mods:
            key_string = mod.lower() + "-" + key_string

        # Esc dismisses an open dismissible modal. Takes priority over input
        # focus / other handlers — convention is that Esc always escapes the
        # modal first. Locked modals (backdrop_click_close=False) ignore Esc.
        if key_string == KEY_ESCAPE and e.down and self._active_modal_node_ref:
            modal = self._active_modal_node_ref()
            if modal and getattr(modal.properties, 'backdrop_click_close', True):
                on_close = getattr(modal.properties, 'on_close', None)
                if on_close:
                    try:
                        on_close()
                    except Exception:
                        traceback.print_exc()
                    return

        # Copy selected text
        if key_string == f"{PRIMARY_MOD}-c" and e.down and self._text_selected_nodes:
            for node in self._text_selected_nodes:
                node.copy_selection()
            return

        # Route to select dropdown (open or focused-closed)
        for node in self.interactive_node_list:
            if node.element_type == ELEMENT_ENUM_TYPE["select"]:
                if getattr(node, 'is_open', False):
                    if node.on_key(key_string, e.down):
                        return
                elif e.down:
                    focused_node = state_manager.get_focused_node()
                    if focused_node == node:
                        if node.on_key(key_string, e.down):
                            return

        # Route to custom input when focused
        from ..platform.custom_input import custom_input_manager
        if custom_input_manager.has_focused_input:
            custom_input_manager.handle_canvas_key(e)
            return

        if key_string == KEY_SPACE or key_string == KEY_ENTER or key_string == KEY_RETURN:
            focused_node = state_manager.get_focused_node()
            is_clickable = getattr(focused_node, 'properties', None) and (
                getattr(focused_node.properties, "on_click", None)
                or getattr(focused_node.properties, 'type', None) == 'submit'
            )
            if is_clickable:
                if e.down:
                    state_manager.highlight_briefly(focused_node.id)
                    self.click_node(focused_node)

    def draw_focus_outline(self, canvas: SkiaCanvas, offset: Point2d):
        node = state_manager.get_focused_node()
        if node and node.tree == self:
            # border_rect = node.box_model.border_rect
            border_rect = node.box_model.border_rect
            stroke_width = node.properties.focus_outline_width
            focus_outline_rect = Rect(
                border_rect.x - stroke_width + offset.x,
                border_rect.y - stroke_width + offset.y,
                border_rect.width + stroke_width * 2,
                border_rect.height + stroke_width * 2
            )

            apply_clip = False
            clip_rect = node.box_model.clip_rect
            if clip_rect:
                padding_rect = node.box_model.padding_rect
                apply_clip = clip_rect and \
                    (clip_rect.top > padding_rect.top or \
                    clip_rect.left > padding_rect.left or \
                    clip_rect.bot < padding_rect.bot or \
                    clip_rect.right < padding_rect.right)

            if apply_clip:
                canvas.save()
                canvas.clip_rect(clip_rect)

            canvas.paint.style = canvas.paint.Style.STROKE
            canvas.paint.color = node.properties.focus_outline_color
            canvas.paint.stroke_width = stroke_width

            border_radius = node.properties.get_border_radius()
            if border_radius.has_radius():
                # Adjust border radius for the stroke offset
                if border_radius.is_uniform():
                    adjusted_radius = border_radius.top_left
                    draw_rect(canvas, focus_outline_rect, adjusted_radius)
                else:
                    # Use per-corner radius as-is for focus outline
                    draw_rect(canvas, focus_outline_rect, border_radius)
            else:
                canvas.draw_rect(focus_outline_rect)

            if apply_clip:
                canvas.restore()

    def init_key_controls(self):
        if not self.is_key_controls_init and self.canvas_decorator:
            self.is_key_controls_init = True
            self.canvas_decorator.register("key", self.on_key)
            self.canvas_decorator.register("scroll", self.on_scroll)

    def _is_draggable_ui(self):
        # Just check 1 level deep
        return any([node.properties.draggable for node in self.root_node.get_children_nodes()])

    def _has_cursor_element(self):
        """Check if any child of root is a cursor element (1 level deep)."""
        return any([node.element_type == "cursor" for node in self.root_node.get_children_nodes()])

    def create_canvas(self):
        rect = self.root_node.boundary_rect

        if self._is_draggable_ui() or self._has_cursor_element():
            rect = get_combined_screens_rect()

        # Some display drivers will show a "black screen of death"
        # if rect is >= screen.rect size.
        # This problem doesn't happen with Canvas.from_screen, just Canvas.from_rect.
        safe_rect = Rect(
            rect.x,
            rect.y,
            rect.width - 0.001,
            rect.height - 1.0
        )
        return CanvasWeakRef(self.Canvas.from_rect(safe_rect))

    def request_decorator_freeze(self):
        """Coalesced decorator repaint: first request paints immediately,
        requests within DECORATOR_COALESCE_MS ride one trailing freeze."""
        if not self.canvas_decorator or self.render_manager.is_destroying or self.destroying:
            return
        if self._decorator_freeze_pending_job:
            return
        elapsed_ms = (time.monotonic() - self._last_decorator_freeze_ts) * 1000
        if elapsed_ms >= DECORATOR_COALESCE_MS:
            self._freeze_decorator_now()
        else:
            delay = max(1, math.ceil(DECORATOR_COALESCE_MS - elapsed_ms))
            self._decorator_freeze_pending_job = cron.after(f"{delay}ms", self._on_decorator_freeze_job)

    def _on_decorator_freeze_job(self):
        self._decorator_freeze_pending_job = None
        if self.canvas_decorator and not self.render_manager.is_destroying and not self.destroying:
            self._freeze_decorator_now()

    def _freeze_decorator_now(self):
        if self._decorator_freeze_pending_job:
            cron.cancel(self._decorator_freeze_pending_job)
            self._decorator_freeze_pending_job = None
        self._last_decorator_freeze_ts = time.monotonic()
        self.canvas_decorator.freeze()

    def render_decorator_canvas(self):
        if not self.canvas_decorator and not self.render_manager.is_destroying:
            self.canvas_decorator = self.create_canvas()
            self.canvas_decorator.register("draw", self.on_draw_decorator_canvas)
            if self.interactive_node_list:
                focused_tree = state_manager.get_focused_tree()
                if focused_tree == self:
                    self.canvas_decorator.focused = True
                elif not focused_tree:
                    self.canvas_decorator.focused = True

        if self.canvas_decorator:
            self._freeze_decorator_now()

    def render_base_canvas(self):
        if not self.render_manager.is_destroying:
            if not self.canvas_base:
                with self.lock:
                    self.canvas_base = self.create_canvas()
                    self.canvas_base.register("draw", self.on_draw_base_canvas)

            self.canvas_base.freeze()

    def render(self, props: dict[str, Any] = {}, on_mount: callable = None, on_unmount: callable = None, show_hints: bool = None):
        if not self.render_manager.is_destroying:
            self.props = self.props or props

            if self.is_mounted:
                self._pending_render = True

            if on_mount or on_unmount:
                state_manager.register_effect(Effect(
                    tree=self,
                    callback=on_mount,
                    cleanup=on_unmount,
                    dependencies=[]
                ))

            if show_hints is not None:
                self.show_hints = show_hints

            self.render_base_canvas()

    def _commit_pending_render(self):
        """Apply a deferred render at the top of a paint. Runs effect cleanups,
        resets the interactive list, and rebuilds self.root_node. Called from
        on_draw_base_canvas before dispatching to a variant, so the variant's
        whole pipeline sees a stable, init_node_hierarchy-walkable root."""
        if not self._pending_render:
            return
        # Reset the flag before doing work so re-entrant state changes that
        # arrive during init_tree_constructor get a fresh pending request
        # for the next paint instead of looping inside this one.
        self._pending_render = False
        if self.is_mounted:
            self.on_state_change_effect_cleanups()
            self.interactive_node_list.clear()
        self.init_tree_constructor()

    def render_animation_frame(self):
        if not self.destroying:
            self.render_manager.render_animation_frame()

    def append_to_render_list(self, node: NodeType, draw: Callable[[SkiaCanvas], None]):
        self.render_list.append(RenderItem(node, draw))

    def _render_debounced_execute(self, *args):
        if not self.render_manager.is_destroying:
            self.render(*args)
            self.render_debounce_job = None

    def render_debounced(self, props: dict[str, Any] = {}, on_mount: callable = None, on_unmount: callable = None, show_hints: bool = None):
        if self.render_debounce_job:
            cron.cancel(self.render_debounce_job)
        self.render_debounce_job = cron.after("1ms", lambda: self._render_debounced_execute(props, on_mount, on_unmount, show_hints))

    def hide(self):
        self.destroy()

    def on_state_change_effect_callbacks(self):
        for state in state_manager.get_processing_states():
            for effect in self.effects:
                component_mount = effect.component and effect.component.id in self.meta_state.new_component_ids
                if component_mount or state in effect.dependencies:
                    if len(inspect.signature(effect.callback).parameters) == 1:
                        effect.callback(StateEvent())
                    else:
                        effect.callback()

    def on_state_change_effect_cleanups(self):
        for state in state_manager.get_processing_states():
            for effect in reversed(self.effects):
                if state in effect.dependencies:
                    if effect.cleanup:
                        if len(inspect.signature(effect.cleanup).parameters) == 1:
                            effect.cleanup(StateEvent())
                        else:
                            effect.cleanup()

    def on_component_unmount_effect_cleanups(self):
        for state in state_manager.get_processing_states():
            effects_to_keep = []
            for effect in reversed(self.effects):
                if effect.cleanup and effect.component and effect.component.id in self.meta_state.removed_component_ids:
                    if len(inspect.signature(effect.cleanup).parameters) == 1:
                        effect.cleanup(StateEvent())
                    else:
                        effect.cleanup()
                else:
                    effects_to_keep.append(effect)
            self.effects = list(reversed(effects_to_keep))
            self.meta_state.removed_component_ids.clear()

    def on_fully_rendered(self):
        if not self.render_manager.is_destroying:
            if self.is_mounted:
                if self.render_manager.render_cause == RenderCause.STATE_CHANGE:
                    self.on_state_change_effect_callbacks()
                elif self.render_manager.render_cause == RenderCause.DRAG_END:
                    if self.draggable_node and self.draggable_node.properties and self.draggable_node.properties.on_drag_end:
                        if len(inspect.signature(self.draggable_node.properties.on_drag_end).parameters) == 1:
                            self.draggable_node.properties.on_drag_end(StateEvent())
                        else:
                            self.draggable_node.properties.on_drag_end()
            else:
                self.is_mounted = True

                for effect in self.effects:
                    if effect.callback:
                        if len(inspect.signature(effect.callback).parameters) == 1:
                            cleanup = effect.callback(StateEvent())
                        else:
                            cleanup = effect.callback()
                        if cleanup and not effect.cleanup:
                            effect.cleanup = cleanup

            # component mounted
            if self.meta_state.new_component_ids:
                for id in list(self.meta_state.new_component_ids):
                    if id in self.meta_state.components:
                        self.meta_state.new_component_ids.clear()

            self.processing_states.clear()
            self.render_cause.clear()
            self.drag_end_phase = False

    def handle_scrollbar_drag_move(self, gpos):
        """Handle scrollbar dragging movement and scroll calculation."""
        node_id = self.meta_state.scrollbar_dragging_id
        node = self.meta_state.id_to_node.get(node_id)
        scrollable_data = self.meta_state.scrollable.get(node_id)

        if not (node and scrollable_data and node.box_model):
            return

        axis = self.meta_state.scrollbar_dragging_axis

        if axis == "x":
            mouse_delta_x = gpos.x - self.meta_state.scrollbar_drag_start_x
            view_width = scrollable_data.view_width
            max_width = scrollable_data.max_width
            thumb_width = node.box_model.scroll_bar_x_thumb_rect.width
            track_width = node.box_model.padding_size.width

            thumb_travel_distance = track_width - thumb_width
            content_travel_distance = max_width - view_width

            if thumb_travel_distance > 0 and content_travel_distance > 0:
                scroll_delta = -(mouse_delta_x / thumb_travel_distance) * content_travel_distance
                new_offset_x = self.meta_state.scrollbar_drag_start_offset_x + scroll_delta
                new_offset_x = max(view_width - max_width, min(0, new_offset_x))
                scrollable_data.offset_x = new_offset_x
                scrollable_data.target_offset_x = new_offset_x
                self.render_manager.render_scrollbar_dragging()
        else:
            mouse_delta_y = gpos.y - self.meta_state.scrollbar_drag_start_y
            view_height = scrollable_data.view_height
            max_height = scrollable_data.max_height
            thumb_height = node.box_model.scroll_bar_thumb_rect.height
            track_height = node.box_model.padding_size.height

            thumb_travel_distance = track_height - thumb_height
            content_travel_distance = max_height - view_height

            if thumb_travel_distance > 0 and content_travel_distance > 0:
                scroll_delta = -(mouse_delta_y / thumb_travel_distance) * content_travel_distance
                new_offset_y = self.meta_state.scrollbar_drag_start_offset_y + scroll_delta
                new_offset_y = max(view_height - max_height, min(0, new_offset_y))
                scrollable_data.offset_y = new_offset_y
                scrollable_data.target_offset_y = new_offset_y
                self.render_manager.render_scrollbar_dragging()

    def handle_scrollbar_mousedown(self, gpos):
        """Check for scrollbar click and initiate drag if found."""
        modal_scope = self.get_modal_scope_ids()
        for node_id, scrollable_data in list(self.meta_state.scrollable.items()):
            if modal_scope is not None and node_id not in modal_scope:
                continue
            node = self.meta_state.id_to_node.get(node_id)
            if node and node.box_model:
                if node.box_model.scroll_bar_thumb_rect and node.box_model.scroll_bar_thumb_rect.contains(gpos):
                    self.meta_state.start_scrollbar_drag(node_id, gpos.y, scrollable_data.offset_y, axis="y")
                    self._scrollbar_show(node_id)
                    self.render_manager.pause()
                    self.render_base_canvas()
                    return True
                if node.box_model.scroll_bar_x_thumb_rect and node.box_model.scroll_bar_x_thumb_rect.contains(gpos):
                    self.meta_state.start_scrollbar_drag(node_id, gpos.x, scrollable_data.offset_x, axis="x")
                    self._scrollbar_show(node_id)
                    self.render_manager.pause()
                    self.render_base_canvas()
                    return True
                if node.box_model.scroll_bar_track_rect and node.box_model.scroll_bar_track_rect.contains(gpos):
                    self._scrollbar_track_jump(node_id, scrollable_data, node, gpos, axis="y")
                    return True
                if node.box_model.scroll_bar_x_track_rect and node.box_model.scroll_bar_x_track_rect.contains(gpos):
                    self._scrollbar_track_jump(node_id, scrollable_data, node, gpos, axis="x")
                    return True
        return False

    def _scrollbar_track_jump(self, node_id, scrollable_data, node, gpos, axis="y"):
        """Jump scroll to click position on the track, then start drag."""
        if axis == "y":
            track_rect = node.box_model.scroll_bar_track_rect
            thumb_rect = node.box_model.scroll_bar_thumb_rect
            if not track_rect or not thumb_rect:
                return
            view_height = scrollable_data.view_height
            max_height = scrollable_data.max_height
            content_travel = max_height - view_height
            thumb_center_y = gpos.y - thumb_rect.height / 2
            ratio = (thumb_center_y - track_rect.y) / (track_rect.height - thumb_rect.height)
            ratio = max(0, min(1, ratio))
            new_offset = -ratio * content_travel
            new_offset = max(view_height - max_height, min(0, new_offset))
            scrollable_data.offset_y = new_offset
            scrollable_data.target_offset_y = new_offset
            self.meta_state.start_scrollbar_drag(node_id, gpos.y, new_offset, axis="y")
        else:
            track_rect = node.box_model.scroll_bar_x_track_rect
            thumb_rect = node.box_model.scroll_bar_x_thumb_rect
            if not track_rect or not thumb_rect:
                return
            view_width = scrollable_data.view_width
            max_width = scrollable_data.max_width
            content_travel = max_width - view_width
            thumb_center_x = gpos.x - thumb_rect.width / 2
            ratio = (thumb_center_x - track_rect.x) / (track_rect.width - thumb_rect.width)
            ratio = max(0, min(1, ratio))
            new_offset = -ratio * content_travel
            new_offset = max(view_width - max_width, min(0, new_offset))
            scrollable_data.offset_x = new_offset
            scrollable_data.target_offset_x = new_offset
            self.meta_state.start_scrollbar_drag(node_id, gpos.x, new_offset, axis="x")
        self._scrollbar_show(node_id)
        self.render_manager.pause()
        self.render_base_canvas()

    def handle_scrollbar_mouseup(self, gpos):
        """Handle scrollbar drag end and restore hover state."""
        dragging_id = self.meta_state.scrollbar_dragging_id
        self.render_manager.resume()
        self.meta_state.clear_scrollbar_drag()
        self.render_base_canvas()
        self.check_scrollbar_hover(gpos)
        if dragging_id:
            self._scrollbar_schedule_idle_hide(dragging_id)

    def check_scrollbar_hover(self, gpos):
        """Check if mouse is hovering over any scrollbar thumb and update visual state."""
        if self.meta_state.is_scrollbar_dragging():
            return

        modal_scope = self.get_modal_scope_ids()
        prev_hovered_id = self.meta_state.scrollbar_hovered_id
        prev_hovered_axis = self.meta_state.scrollbar_hovered_axis
        new_hovered_id = None
        new_hovered_axis = None

        for node_id, scrollable_data in list(self.meta_state.scrollable.items()):
            if modal_scope is not None and node_id not in modal_scope:
                continue
            node = self.meta_state.id_to_node.get(node_id)
            if node and node.box_model:
                if node.box_model.scroll_bar_thumb_rect and node.box_model.scroll_bar_thumb_rect.contains(gpos):
                    new_hovered_id = node_id
                    new_hovered_axis = "y"
                    break
                if node.box_model.scroll_bar_x_thumb_rect and node.box_model.scroll_bar_x_thumb_rect.contains(gpos):
                    new_hovered_id = node_id
                    new_hovered_axis = "x"
                    break
                if node.box_model.scroll_bar_track_rect and node.box_model.scroll_bar_track_rect.contains(gpos):
                    new_hovered_id = node_id
                    new_hovered_axis = "y"
                    break
                if node.box_model.scroll_bar_x_track_rect and node.box_model.scroll_bar_x_track_rect.contains(gpos):
                    new_hovered_id = node_id
                    new_hovered_axis = "x"
                    break

        if new_hovered_id != prev_hovered_id or new_hovered_axis != prev_hovered_axis:
            if new_hovered_id:
                self.meta_state.set_scrollbar_hover(new_hovered_id, new_hovered_axis)
                self._scrollbar_show(new_hovered_id)
            else:
                self.meta_state.clear_scrollbar_hover()
                if prev_hovered_id:
                    self._scrollbar_schedule_idle_hide(prev_hovered_id)
            self.render_base_canvas()

    def detect_resize_edge(self, gpos):
        """Detect if mouse is near a resizable element's edge. Returns (node_id, edge_str) or (None, None)."""
        # Scrollbar takes priority over resize edges
        for node_id, scrollable_data in list(self.meta_state.scrollable.items()):
            node = self.meta_state.id_to_node.get(node_id)
            if node and node.box_model:
                if (node.box_model.scroll_bar_thumb_rect and node.box_model.scroll_bar_thumb_rect.contains(gpos)):
                    return (None, None)
                if (node.box_model.scroll_bar_x_thumb_rect and node.box_model.scroll_bar_x_thumb_rect.contains(gpos)):
                    return (None, None)
                if (node.box_model.scroll_bar_track_rect and node.box_model.scroll_bar_track_rect.contains(gpos)):
                    return (None, None)
                if (node.box_model.scroll_bar_x_track_rect and node.box_model.scroll_bar_x_track_rect.contains(gpos)):
                    return (None, None)

        threshold = scale_value(RESIZE_EDGE_THRESHOLD)
        resizable_ids = self.meta_state.resizable_nodes | {
            wid for wid in self.meta_state.windows
            if self.meta_state.id_to_node.get(wid) and getattr(self.meta_state.id_to_node[wid].properties, 'resizable', False)
        }
        for node_id in resizable_ids:
            node = self.meta_state.id_to_node.get(node_id)
            if not node:
                continue
            if getattr(node, 'is_minimized', False):
                continue
            if not node.box_model or not node.box_model.border_rect:
                continue

            # Determine allowed edges
            resizable = node.properties.resizable
            if resizable is True:
                allowed_edges = {"top", "right", "bottom", "left"}
            elif isinstance(resizable, str):
                allowed_edges = {resizable}
            elif isinstance(resizable, list):
                allowed_edges = set(resizable)
            else:
                continue

            rect = node.box_model.border_rect
            x, y = gpos.x, gpos.y

            near_top = "top" in allowed_edges and abs(y - rect.y) <= threshold and rect.x - threshold <= x <= rect.x + rect.width + threshold
            near_bottom = "bottom" in allowed_edges and abs(y - (rect.y + rect.height)) <= threshold and rect.x - threshold <= x <= rect.x + rect.width + threshold
            near_left = "left" in allowed_edges and abs(x - rect.x) <= threshold and rect.y - threshold <= y <= rect.y + rect.height + threshold
            near_right = "right" in allowed_edges and abs(x - (rect.x + rect.width)) <= threshold and rect.y - threshold <= y <= rect.y + rect.height + threshold

            # Corners (only if both edges are allowed)
            if near_top and near_left:
                return (node_id, "top_left")
            if near_top and near_right:
                return (node_id, "top_right")
            if near_bottom and near_left:
                return (node_id, "bottom_left")
            if near_bottom and near_right:
                return (node_id, "bottom_right")
            # Single edges
            if near_top:
                return (node_id, "top")
            if near_bottom:
                return (node_id, "bottom")
            if near_left:
                return (node_id, "left")
            if near_right:
                return (node_id, "right")

        return (None, None)

    def handle_resize_drag_move(self, gpos):
        """Compute ghost rect during resize drag."""
        ms = self.meta_state
        dx = gpos.x - ms.resize_start_pos.x
        dy = gpos.y - ms.resize_start_pos.y
        edge = ms.resize_edge
        sr = ms.resize_start_rect

        new_x, new_y = sr.x, sr.y
        new_w, new_h = sr.width, sr.height

        # Use original user constraints (before any resize overrides)
        oc = ms.resize_original_constraints.get(ms.resize_dragging_id, {})
        min_w = oc.get('min_width') or scale_value(100)
        min_h = oc.get('min_height') or scale_value(40)
        max_w = oc.get('max_width')
        max_h = oc.get('max_height')

        if "right" in edge:
            new_w = sr.width + dx
        if "left" in edge:
            new_w = sr.width - dx
            new_x = sr.x + dx
        if "bottom" in edge:
            new_h = sr.height + dy
        if "top" in edge:
            new_h = sr.height - dy
            new_y = sr.y + dy

        # Clamp width
        if new_w < min_w:
            if "left" in edge:
                new_x = sr.x + sr.width - min_w
            new_w = min_w
        if max_w and new_w > max_w:
            if "left" in edge:
                new_x = sr.x + sr.width - max_w
            new_w = max_w

        # Clamp height
        if new_h < min_h:
            if "top" in edge:
                new_y = sr.y + sr.height - min_h
            new_h = min_h
        if max_h and new_h > max_h:
            if "top" in edge:
                new_y = sr.y + sr.height - max_h
            new_h = max_h

        ms.resize_ghost_rect = Rect(new_x, new_y, new_w, new_h)
        self.render_manager.render_resize_ghost()

    def _compute_resize_layout_compensation(self, node, old_width, old_height, new_width, new_height):
        """Compute drag offset adjustment to counteract layout repositioning after resize.

        When a parent uses center/flex_end alignment, changing the window size
        shifts its natural (layout-computed) position. We compensate so the
        window stays where the ghost outline was.
        """
        parent = node.parent_node
        if not parent:
            return Point2d(0, 0)

        dw = new_width - old_width
        dh = new_height - old_height
        flex_dir = parent.properties.flex_direction or "column"
        justify = parent.properties.justify_content or "flex_start"
        align = parent.properties.align_items or "stretch"

        def axis_compensation(delta, alignment):
            if alignment == "center":
                return delta / 2
            elif alignment == "flex_end":
                return delta
            return 0

        if flex_dir == "column":
            # Main axis = Y (justify), Cross axis = X (align)
            comp_x = axis_compensation(dw, align)
            comp_y = axis_compensation(dh, justify)
        else:
            # Main axis = X (justify), Cross axis = Y (align)
            comp_x = axis_compensation(dw, justify)
            comp_y = axis_compensation(dh, align)

        return Point2d(comp_x, comp_y)

    def handle_resize_mouseup(self, gpos):
        """Apply final size from resize ghost and resume rendering."""
        ms = self.meta_state
        node_id = ms.resize_dragging_id
        ghost = ms.resize_ghost_rect
        node = ms.id_to_node.get(node_id)

        if node and ghost:
            start_rect = ms.resize_start_rect

            # Unscale ghost dimensions since update_property will re-scale
            scale = get_scale() or 1.0
            unscaled_w = ghost.width / scale
            unscaled_h = ghost.height / scale

            ms.set_ref_property_override(node_id, "width", unscaled_w)
            ms.set_ref_property_override(node_id, "height", unscaled_h)
            # Also cap max so layout can't expand beyond resized size
            ms.set_ref_property_override(node_id, "max_width", unscaled_w)
            ms.set_ref_property_override(node_id, "max_height", unscaled_h)

            # Compensate for layout repositioning (e.g. centering shifts)
            compensation = self._compute_resize_layout_compensation(
                node, start_rect.width, start_rect.height, ghost.width, ghost.height
            )

            # Combine left/top edge movement + layout compensation
            offset_dx = (ghost.x - start_rect.x) + compensation.x
            offset_dy = (ghost.y - start_rect.y) + compensation.y
            if offset_dx != 0 or offset_dy != 0:
                if node_id in ms._draggable_offset:
                    ms._draggable_offset[node_id] = Point2d(
                        ms._draggable_offset[node_id].x + offset_dx,
                        ms._draggable_offset[node_id].y + offset_dy,
                    )

            # Save dimensions for persistence (unscaled)
            if hasattr(node, 'save_resize_dimensions'):
                node.save_resize_dimensions(unscaled_w, unscaled_h)

        ms.clear_resize_drag()
        self.destroy_blockable_canvas()
        self.render_manager.resume()
        self.render_base_canvas()

    def draw_resize_edge_highlight(self, canvas, offset):
        """Draw colored bars on hovered resize edges."""
        ms = self.meta_state
        if not ms.resize_edge_hovered or ms.is_resize_dragging():
            return

        node_id, edge = ms.resize_edge_hovered
        node = ms.id_to_node.get(node_id)
        if not node or not node.box_model or not node.box_model.border_rect:
            return

        rect = node.box_model.border_rect
        ox = offset.x if offset else 0
        oy = offset.y if offset else 0
        x, y, w, h = rect.x + ox, rect.y + oy, rect.width, rect.height
        hw = scale_value(RESIZE_EDGE_HIGHLIGHT_WIDTH)

        canvas.paint.style = canvas.paint.Style.FILL
        canvas.paint.color = RESIZE_EDGE_HIGHLIGHT_COLOR

        if "top" in edge:
            canvas.draw_rect(Rect(x, y, w, hw))
        if "bottom" in edge:
            canvas.draw_rect(Rect(x, y + h - hw, w, hw))
        if "left" in edge:
            canvas.draw_rect(Rect(x, y, hw, h))
        if "right" in edge:
            canvas.draw_rect(Rect(x + w - hw, y, hw, h))

    def draw_resize_ghost(self, canvas):
        """Draw stroke outline during resize drag."""
        ms = self.meta_state
        if not ms.is_resize_dragging() or not ms.resize_ghost_rect:
            return

        ghost = ms.resize_ghost_rect
        canvas.paint.style = canvas.paint.Style.STROKE
        canvas.paint.color = RESIZE_GHOST_COLOR
        canvas.paint.stroke_width = scale_value(RESIZE_GHOST_STROKE_WIDTH)
        canvas.draw_rect(ghost)

    def on_hover(self, gpos):
        try:
            if not state_manager.is_drag_active():
                # Detect resize edge hover before button hover
                resize_node_id, resize_edge = self.detect_resize_edge(gpos)
                prev_resize_hover = self.meta_state.resize_edge_hovered
                if resize_edge:
                    new_hover = (resize_node_id, resize_edge)
                    if prev_resize_hover != new_hover:
                        self.meta_state.set_resize_edge_hover(resize_node_id, resize_edge)
                        # Suppress button hover when on resize edge
                        prev_hovered_id = state_manager.get_hovered_id()
                        if prev_hovered_id:
                            self.unhighlight_no_render(prev_hovered_id)
                            state_manager.set_hovered_id(None)
                        self.render_manager.render_mouse_highlight()
                    if not self.hover_validation_job:
                        self.schedule_hover_validation()
                    return
                elif prev_resize_hover:
                    self.meta_state.clear_resize_edge_hover()
                    self.render_manager.render_mouse_highlight()

                # Scroll button hover
                hovered_overlay = self.scroll_button_overlay_at(gpos)
                hovered_overlay_id = hovered_overlay.synthetic_id if hovered_overlay else None
                if hovered_overlay_id != self.meta_state.scroll_button_hovered_id:
                    self.meta_state.scroll_button_hovered_id = hovered_overlay_id
                    self.render_manager.render_mouse_highlight()
                if hovered_overlay_id:
                    # Suppress button hover when over a scroll button overlay
                    prev_hovered_id = state_manager.get_hovered_id()
                    if prev_hovered_id:
                        self.unhighlight_no_render(prev_hovered_id)
                        state_manager.set_hovered_id(None)
                        self.render_manager.render_mouse_highlight()
                    if not self.hover_validation_job:
                        self.schedule_hover_validation()
                    return

                changed = False
                new_hovered_id = None
                prev_hovered_id = state_manager.get_hovered_id()
                decoration_ids = self._decoration_subtree_ids_at(gpos)
                for source_id, target_id in self.meta_state.get_hover_links():
                    if decoration_ids is not None and \
                            source_id not in decoration_ids and \
                            target_id not in decoration_ids:
                        continue
                    source_node = self.meta_state.id_to_node.get(source_id, None)
                    target_node = source_node
                    if source_id != target_id:
                        target_node = self.meta_state.id_to_node.get(target_id, None)
                    if source_node and not getattr(target_node, 'disabled', False):
                        if source_node and source_node.box_model and self._hover_hit_rect(source_node).contains(gpos):
                            if source_node.is_fully_clipped_by_scroll():
                                continue
                            if self._modal_backdrop_blocked_by_panel(gpos, source_id):
                                continue
                            new_hovered_id = target_id
                            if new_hovered_id != prev_hovered_id:
                                state_manager.set_hovered_id(target_id)
                                changed = True
                                self.unhighlight_no_render(prev_hovered_id)
                                self.highlight_no_render(target_id, color=target_node.properties.highlight_color)
                                if not self.hover_validation_job:
                                    self.schedule_hover_validation()
                            break

                if not new_hovered_id and prev_hovered_id:
                    self.unhighlight_no_render(prev_hovered_id)
                    changed = True
                    state_manager.set_hovered_id(None)
                if changed:
                    self.render_manager.render_mouse_highlight()

        except Exception:
            print("talon_ui_elements on_hover error:")
            traceback.print_exc()

    def get_mouse_hovered_input_id(self, gpos):
        modal_scope = self.get_modal_scope_ids()
        # Check textarea nodes (always custom-rendered)
        for node in self.interactive_node_list:
            if node.element_type == ELEMENT_ENUM_TYPE["textarea"] and node.box_model:
                if modal_scope is not None and node.id not in modal_scope:
                    continue
                if node.box_model.border_rect.contains(gpos):
                    return node.id

        for node in self.interactive_node_list:
            if node.element_type == ELEMENT_ENUM_TYPE["input_text"] and node.box_model:
                if modal_scope is not None and node.id not in modal_scope:
                    continue
                if node.box_model.border_rect.contains(gpos):
                    return node.id
        return None

    def _get_selectable_text_at(self, gpos):
        for node in self.meta_state.id_to_node.values():
            if node.element_type in (ELEMENT_ENUM_TYPE["text"], ELEMENT_ENUM_TYPE["code"]) and \
                    getattr(node, 'selectable', False) and node.box_model:
                hit_rect = node.parent_node.box_model.padding_rect \
                    if node.parent_node and node.parent_node.box_model \
                    else node.box_model.padding_rect
                if hit_rect.contains(gpos):
                    return node
        return None

    def on_mousemove(self, gpos):
        if self.meta_state.is_resize_dragging():
            self.handle_resize_drag_move(gpos)
            return

        if self.meta_state.is_scrollbar_dragging():
            self.handle_scrollbar_drag_move(gpos)
            return

        if self.is_drag_end():
            return

        if self._text_selecting_node:
            if self._text_selecting_node.element_type in (ELEMENT_ENUM_TYPE["textarea"], ELEMENT_ENUM_TYPE["text"], ELEMENT_ENUM_TYPE["code"]):
                self._text_selecting_node.update_selection_from_drag(gpos.x, click_y=gpos.y)
            else:
                self._text_selecting_node.update_selection_from_drag(gpos.x)
            return

        start_pos = state_manager.get_mousedown_start_pos()
        if start_pos:
            state_manager.set_mousedown_start_offset(gpos - start_pos)

        if start_pos and not self._active_modal_node_ref and state_manager.get_drag_relative_offset():
            is_drag_start = False
            if not state_manager.is_drag_active():
                threshold = scale_value(DRAG_INIT_THRESHOLD)
                if abs(gpos.x - start_pos.x) > threshold or abs(gpos.y - start_pos.y) > threshold:
                    state_manager.set_drag_active(True)
                    is_drag_start = True

            if is_drag_start:
                offset = state_manager.get_mousedown_start_offset()
                hovered_id = state_manager.get_hovered_id()
                if hovered_id:
                    self.meta_state.set_unhighlighted(hovered_id)
                    self.render_manager.render_mouse_highlight()
                self.render_manager.render_drag_start(
                    mouse_pos=gpos,
                    mousedown_start_pos=state_manager.get_mousedown_start_pos(),
                    mousedown_start_offset=offset
                )
                self.meta_state.set_drag_offset(
                    self.draggable_node.id,
                    offset
                )
                return

        if state_manager.get_mousedown_start_pos() and state_manager.is_drag_active():
            offset = state_manager.get_mousedown_start_offset()
            self.render_manager.render_dragging(
                mouse_pos=gpos,
                mousedown_start_pos=state_manager.get_mousedown_start_pos(),
                mousedown_start_offset=offset
            )
            self.meta_state.set_drag_offset(
                self.draggable_node.id,
                offset
            )

    def on_mousedown(self, gpos):
        if self.meta_state.resize_edge_hovered:
            node_id, edge = self.meta_state.resize_edge_hovered
            node = self.meta_state.id_to_node.get(node_id)
            if node and node.box_model and node.box_model.border_rect:
                start_rect = node.box_model.border_rect
                # Save original user constraints on first resize
                if node_id not in self.meta_state.resize_original_constraints:
                    self.meta_state.resize_original_constraints[node_id] = {
                        'min_width': node.box_model.min_width if node.box_model else getattr(node.properties, 'min_width', None),
                        'min_height': node.box_model.min_height if node.box_model else getattr(node.properties, 'min_height', None),
                        'max_width': node.box_model.max_width if node.box_model else getattr(node.properties, 'max_width', None),
                        'max_height': node.box_model.max_height if node.box_model else getattr(node.properties, 'max_height', None),
                    }
                self.meta_state.start_resize_drag(node_id, edge, gpos, start_rect)
                self.render_manager.pause()
                return

        if self.handle_scrollbar_mousedown(gpos):
            return

        scroll_btn = self.scroll_button_overlay_at(gpos)
        if scroll_btn:
            state_manager.smooth_scroll_node(
                scroll_btn.container_id, scroll_btn.axis, scroll_btn.direction
            )
            return

        hovered_id = state_manager.get_hovered_id()
        state_manager.set_mousedown_start_pos(gpos)

        # Close open selects if click is outside the select's own elements
        hovered_node = self.meta_state.id_to_node.get(hovered_id) if hovered_id else None
        hovered_interactive_id = getattr(hovered_node, 'interactive_id', None) if hovered_node else None
        for node in self.interactive_node_list:
            if node.element_type == ELEMENT_ENUM_TYPE["select"] and getattr(node, 'is_open', False):
                if hovered_interactive_id != node.id:
                    node._close()

        if self.draggable_node and self.drag_handle_node and self.draggable_node.box_model:
            draggable_top_left_pos = self.draggable_node.box_model.margin_pos
            drag_handle_rect = self.drag_handle_node.box_model.border_rect
            if drag_handle_rect.contains(gpos):
                relative_offset = Point2d(gpos.x - draggable_top_left_pos.x, gpos.y - draggable_top_left_pos.y)
                state_manager.set_drag_relative_offset(relative_offset)

        if hovered_id in list(self.meta_state.buttons):
            node = self.meta_state.id_to_node.get(hovered_id)
            if node:
                state_manager.set_mousedown_start_id(hovered_id)
                active_color = get_active_color_from_highlight_color(node.properties.highlight_color)
                state_manager.focus_node(node, visible=False)
                self.meta_state.set_highlighted(hovered_id, active_color)
                self.render_manager.render_mouse_highlight()
                # Schedule validation in case mouse teleports away after click
                if not self.hover_validation_job:
                    self.schedule_hover_validation()
                return

        input_id = self.get_mouse_hovered_input_id(gpos)
        if input_id:
            node = self.meta_state.id_to_node.get(input_id)
            if node:
                is_textarea = node.element_type == ELEMENT_ENUM_TYPE["textarea"]
                state_manager.focus_node(node, visible=True)
                if hasattr(node, 'set_cursor_from_click'):
                    import time
                    now = time.monotonic()
                    click_x, click_y = gpos.x, gpos.y
                    near_last = abs(click_x - self._input_last_click_x) < 20 and abs(click_y - self._input_last_click_y) < 20
                    if now - self._input_last_click_time < 0.4 and near_last:
                        self._input_click_count = min(self._input_click_count + 1, 3)
                    else:
                        self._input_click_count = 1
                    self._input_last_click_time = now
                    self._input_last_click_x = click_x
                    self._input_last_click_y = click_y
                    if is_textarea:
                        node.set_cursor_from_click(gpos.x, click_y=gpos.y, click_count=self._input_click_count)
                    else:
                        node.set_cursor_from_click(gpos.x, self._input_click_count)
                    if self._input_click_count == 1:
                        self._text_selecting_node = node
                return

        selectable_node = self._get_selectable_text_at(gpos)
        if selectable_node:
            if self.canvas_decorator:
                self.canvas_decorator.focused = True
            for node in self._text_selected_nodes:
                if node is not selectable_node:
                    node.clear_selection()
            self._text_selected_nodes = [selectable_node]

            import time
            now = time.monotonic()
            click_x, click_y = gpos.x, gpos.y
            near_last = abs(click_x - self._input_last_click_x) < 20 and abs(click_y - self._input_last_click_y) < 20
            if now - self._input_last_click_time < 0.4 and near_last:
                self._input_click_count = min(self._input_click_count + 1, 3)
            else:
                self._input_click_count = 1
            self._input_last_click_time = now
            self._input_last_click_x = click_x
            self._input_last_click_y = click_y
            selectable_node.set_selection_from_click(gpos.x, gpos.y, self._input_click_count)
            if self._input_click_count == 1:
                self._text_selecting_node = selectable_node
            return

        # Clear any text selections when clicking elsewhere
        for node in self._text_selected_nodes:
            node.clear_selection()
        self._text_selected_nodes = []

        if self.root_node.box_model:
            if self.root_node.box_model.content_children_rect.contains(gpos):
                state_manager.blur(pos=gpos)
            else:
                state_manager.blur_all(pos=gpos)

    def click_node(self, node: NodeType):
        if node and getattr(node, 'properties', None) and getattr(node.properties, 'type', None) == 'submit':
            from .node_form import find_parent_form
            form_node = find_parent_form(node)
            if form_node and form_node.on_submit:
                try:
                    form_node.fire_submit()
                except Exception as e:
                    print(f"Error during form submit: {e}")
                    log_trace()
                    self.destroy()
                return  # Form handled it
        if node and getattr(node, 'on_click', None):
            try:
                sig = inspect.signature(node.on_click)
                if len(sig.parameters) == 0:
                    node.on_click()
                else:
                    node.on_click(ClickEvent(id=node.id))
            except Exception as e:
                print(f"Error during node click: {e}")
                log_trace()
                self.destroy()

    def on_drag_mouseup_begin(self, e):
        self.drag_end_phase = True
        self.meta_state.commit_drag_offset(self.draggable_node.id)
        state_manager.set_drag_active(False)
        state_manager.set_drag_relative_offset(None)

    def on_mouseup(self, gpos):
        try:
            if self._text_selecting_node and hasattr(self._text_selecting_node, 'finalize_selection'):
                self._text_selecting_node.finalize_selection()
            self._text_selecting_node = None

            if self.meta_state.is_resize_dragging():
                self.handle_resize_mouseup(gpos)
                return

            if self.meta_state.is_scrollbar_dragging():
                self.handle_scrollbar_mouseup(gpos)
                return

            hovered_id = state_manager.get_hovered_id()
            mousedown_start_id = state_manager.get_mousedown_start_id()

            if mousedown_start_id and hovered_id == mousedown_start_id:
                node = self.meta_state.id_to_node.get(mousedown_start_id)
                if node:
                    self.meta_state.set_highlighted(mousedown_start_id, node.properties.highlight_color)
                    if not state_manager.is_drag_active():
                        state_manager.set_last_clicked_pos(gpos)
                        self.click_node(node)

            state_manager.set_mousedown_start_pos(None)
            state_manager.set_drag_relative_offset(None)

            if self.draggable_node and self.drag_handle_node:
                if state_manager.is_drag_active():
                    # move delay to render manager with proper queue
                    offset = state_manager.get_mousedown_start_offset()
                    self.meta_state.set_drag_offset(
                        self.draggable_node.id,
                        offset
                    )
                    self.render_manager.render_drag_end(
                        mouse_pos=gpos,
                        mousedown_start_pos=state_manager.get_mousedown_start_pos(),
                        mousedown_start_offset=offset,
                        on_start=self.on_drag_mouseup_begin,
                        # on_end=self.on_drag_mouseup_cleanup
                    )

            state_manager.set_mousedown_start_pos(None)
        except Exception as e:
            print(f"talon_ui_elements on_mouseup error: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def _decoration_subtree_ids_at(self, gpos):
        """If gpos falls inside an open floating-overlay subtree (e.g. an
        expanded select dropdown), return the set of node ids that belong to
        that subtree so hit-tests can restrict matches to it. Without this,
        hover/click can fall through to a sibling button that happens to sit
        under the floating dropdown. Returns None when no overlay is covering
        gpos. `uses_decoration_render` alone isn't enough — it's also cascaded
        onto nodes with `highlight_style`, so we additionally require
        `z_index > 0` to distinguish real overlays from decoration-rendered
        highlights.

        When a modal is open, the result is intersected with the modal subtree
        so clicks/hovers can never reach background elements."""
        modal_scope = self.get_modal_scope_ids()
        if not self.meta_state.has_hit_priority_overlay:
            return modal_scope
        for node in self.meta_state.id_to_node.values():
            if not (node.uses_decoration_render and node.box_model):
                continue
            if (node.properties.z_index or 0) <= 0:
                continue
            if not node.box_model.padding_rect.contains(gpos):
                continue
            ids = set()
            stack = [node]
            while stack:
                cur = stack.pop()
                cur_id = getattr(cur, 'id', None)
                if cur_id:
                    ids.add(cur_id)
                stack.extend(getattr(cur, 'children_nodes', None) or ())
            if modal_scope is not None:
                ids &= modal_scope
            return ids
        return modal_scope

    def _hover_hit_rect(self, source_node):
        """Hit-test rect for a hover-link source. For `for_id` text labels we
        expand the tight glyph padding_rect by a few pixels so the click target
        matches the visual line-height. Other nodes use their padding_rect."""
        rect = source_node.box_model.padding_rect
        if source_node.element_type == ELEMENT_ENUM_TYPE["text"] and \
                getattr(source_node.properties, "for_id", None):
            pad_x = scale_value(4)
            pad_y = scale_value(6)
            return Rect(
                rect.x - pad_x,
                rect.y - pad_y,
                rect.width + pad_x * 2,
                rect.height + pad_y * 2,
            )
        return rect

    def validate_hover_state(self):
        """Validate hover state and clean up if mouse left the UI."""
        if state_manager.are_mouse_events_disabled() or self.render_manager.is_rendering:
            return False
        changed = False
        current_pos = self.get_cursor_position()

        hovered_id = state_manager.get_hovered_id()
        if hovered_id and not state_manager.is_drag_active():
            # Check every source node that maps to this hovered target. With
            # for_id, a label text is the source and the checkbox is the target -
            # the cursor lives over the source's rect, not the target's, so
            # checking only the target would clear hover incorrectly.
            still_hovered = False
            try:
                decoration_ids = self._decoration_subtree_ids_at(current_pos)
                for source_id, target_id in self.meta_state.get_hover_links():
                    if target_id != hovered_id:
                        continue
                    if decoration_ids is not None and \
                            source_id not in decoration_ids and \
                            target_id not in decoration_ids:
                        continue
                    source_node = self.meta_state.id_to_node.get(source_id)
                    if source_node and source_node.box_model and \
                            self._hover_hit_rect(source_node).contains(current_pos) and \
                            not source_node.is_fully_clipped_by_scroll() and \
                            not self._modal_backdrop_blocked_by_panel(current_pos, source_id):
                        still_hovered = True
                        break
            except (AttributeError, TypeError):
                still_hovered = False

            if not still_hovered:
                self.unhighlight_no_render(hovered_id)
                state_manager.set_hovered_id(None)
                changed = True

        # Validate resize edge hover state
        if self.meta_state.resize_edge_hovered:
            resize_node_id, _ = self.meta_state.resize_edge_hovered
            current_resize_node_id, current_edge = self.detect_resize_edge(current_pos)
            if not current_edge or current_resize_node_id != resize_node_id:
                self.meta_state.clear_resize_edge_hover()
                changed = True

        # Also validate click state
        mousedown_start_id = state_manager.get_mousedown_start_id()
        if mousedown_start_id:
            node = self.meta_state.id_to_node.get(mousedown_start_id)

            if node and node.box_model and node.box_model.padding_pos:
                try:
                    if not node.box_model.padding_rect.contains(current_pos):
                        self.meta_state.set_unhighlighted(mousedown_start_id)
                        state_manager.set_mousedown_start_id(None)
                        changed = True
                except (AttributeError, TypeError):
                    # Box model changed/destroyed between check and access
                    state_manager.set_mousedown_start_id(None)
                    changed = True
            else:
                state_manager.set_mousedown_start_id(None)
                changed = True

        return changed

    def reconcile_mouse_highlight(self):
        last_clicked_pos = state_manager.get_last_clicked_pos()
        prev_hovered_id = state_manager.get_hovered_id()
        gpos = self.get_cursor_position()

        # Re-detect which element is under the cursor after re-render
        new_hovered_id = None
        decoration_ids = self._decoration_subtree_ids_at(gpos)
        for source_id, target_id in self.meta_state.get_hover_links():
            if decoration_ids is not None and \
                    source_id not in decoration_ids and \
                    target_id not in decoration_ids:
                continue
            source_node = self.meta_state.id_to_node.get(source_id, None)
            target_node = source_node
            if source_id != target_id:
                target_node = self.meta_state.id_to_node.get(target_id, None)
            if source_node and not getattr(target_node, 'disabled', False):
                if source_node.box_model and self._hover_hit_rect(source_node).contains(gpos):
                    if source_node.is_fully_clipped_by_scroll():
                        continue
                    new_hovered_id = target_id
                    break

        if new_hovered_id:
            if new_hovered_id != prev_hovered_id:
                self.meta_state.set_unhighlighted(prev_hovered_id)
            state_manager.set_hovered_id(new_hovered_id)
            node = self.meta_state.id_to_node.get(new_hovered_id)
            if node:
                self.meta_state.set_highlighted(new_hovered_id, node.properties.highlight_color)
        elif prev_hovered_id:
            self.meta_state.set_unhighlighted(prev_hovered_id)
            state_manager.set_hovered_id(None)

        state_manager.set_last_clicked_pos(None)

    def on_mouse(self, e: MouseEvent):
        if self.unmounting:
            return
        if not state_manager.are_mouse_events_disabled() and \
                not self.render_manager.is_destroying:
            self.last_mouse_event_time = time.time()

            if e.event == "mousemove":
                self.on_mousemove(e.gpos)
                self.check_scrollbar_hover(e.gpos)
                self.on_hover(e.gpos)
            elif e.event == "mousedown":
                self.on_mousedown(e.gpos)
            elif e.event == "mouseup":
                self.on_mouseup(e.gpos)

    def _try_scroll_node(self, node, e):
        """Try to scroll a node. Returns True if the node actually scrolled."""
        scrollable_data = self.meta_state.scrollable[node.id]
        did_scroll = False
        smooth = self._smooth_scroll_factor > 0

        # Vertical scroll
        max_height = node.box_model.content_children_with_padding_size.height
        view_height = node.box_model.padding_size.height

        if max_height > view_height:
            offset_y = 0
            is_wheel_y = abs(e.degrees.y) > 1e-5
            is_touchpad_y = abs(e.pixels.y) > 1e-5

            # mouse wheel
            if is_wheel_y:
                offset_y = self.scroll_amount_per_tick if e.degrees.y > 0 else -self.scroll_amount_per_tick
            # touchpad
            elif is_touchpad_y:
                offset_y = e.pixels.y

            if offset_y:
                min_y = view_height - max_height
                if smooth and is_wheel_y:
                    new_target = scrollable_data.target_offset_y + offset_y
                    new_target = max(min_y, min(0, new_target))
                    if new_target != scrollable_data.target_offset_y:
                        scrollable_data.target_offset_y = new_target
                        scrollable_data.view_height = view_height
                        scrollable_data.max_height = max_height
                        did_scroll = True
                else:
                    new_offset_y = scrollable_data.offset_y + offset_y
                    new_offset_y = max(min_y, min(0, new_offset_y))
                    if new_offset_y != scrollable_data.offset_y:
                        scrollable_data.offset_y = new_offset_y
                        scrollable_data.target_offset_y = new_offset_y
                        scrollable_data.view_height = view_height
                        scrollable_data.max_height = max_height
                        did_scroll = True

        # Horizontal scroll
        max_width = node.box_model.content_children_with_padding_size.width
        view_width = node.box_model.padding_size.width

        if max_width > view_width:
            offset_x = 0
            degrees_x = getattr(e.degrees, 'x', 0) if hasattr(e.degrees, 'x') else 0
            pixels_x = getattr(e.pixels, 'x', 0) if hasattr(e.pixels, 'x') else 0
            is_wheel_x = abs(degrees_x) > 1e-5
            is_touchpad_x = abs(pixels_x) > 1e-5

            # mouse wheel
            if is_wheel_x:
                offset_x = self.scroll_amount_per_tick if degrees_x > 0 else -self.scroll_amount_per_tick
            # touchpad
            elif is_touchpad_x:
                offset_x = pixels_x

            if offset_x:
                min_x = view_width - max_width
                if smooth and is_wheel_x:
                    new_target = scrollable_data.target_offset_x + offset_x
                    new_target = max(min_x, min(0, new_target))
                    if new_target != scrollable_data.target_offset_x:
                        scrollable_data.target_offset_x = new_target
                        scrollable_data.view_width = view_width
                        scrollable_data.max_width = max_width
                        did_scroll = True
                else:
                    new_offset_x = scrollable_data.offset_x + offset_x
                    new_offset_x = max(min_x, min(0, new_offset_x))
                    if new_offset_x != scrollable_data.offset_x:
                        scrollable_data.offset_x = new_offset_x
                        scrollable_data.target_offset_x = new_offset_x
                        scrollable_data.view_width = view_width
                        scrollable_data.max_width = max_width
                        did_scroll = True

        return did_scroll

    def _try_scroll_textarea(self, e) -> bool:
        """Handle mouse wheel scrolling for textarea nodes."""
        from ..platform.custom_input import custom_input_manager

        modal_scope = self.get_modal_scope_ids()
        # Find textarea to scroll: prefer focused, fall back to hovered
        node = None
        focused_node = state_manager.get_focused_node()
        if focused_node and focused_node.tree == self \
                and focused_node.element_type == ELEMENT_ENUM_TYPE["textarea"] \
                and (modal_scope is None or focused_node.id in modal_scope):
            node = focused_node
        else:
            for n in self.interactive_node_list:
                if n.element_type != ELEMENT_ENUM_TYPE["textarea"]:
                    continue
                if modal_scope is not None and n.id not in modal_scope:
                    continue
                if getattr(n, 'box_model', None) and n.box_model.border_rect.contains(e.gpos):
                    node = n
                    break

        if not node or not getattr(node, 'box_model', None):
            return False

        state = custom_input_manager.get_state(node.id)
        if not state:
            return False

        paint = node._make_paint()
        line_h = node._get_line_height(paint)
        content_width = node.box_model.content_size.width
        content_height = node.box_model.content_size.height

        text = state.text or ""
        lines = node._get_wrapped_lines(text, content_width, paint) if text else [("", 0)]
        total_height = len(lines) * line_h

        if total_height <= content_height:
            return False

        offset_y = 0
        if abs(e.degrees.y) > 1e-5:
            offset_y = self.scroll_amount_per_tick if e.degrees.y > 0 else -self.scroll_amount_per_tick
        elif abs(e.pixels.y) > 1e-5:
            offset_y = e.pixels.y

        if not offset_y:
            return True

        max_scroll = total_height - content_height
        new_offset = state.scroll_offset - offset_y
        new_offset = max(0, min(max_scroll, new_offset))

        if new_offset != state.scroll_offset:
            state.scroll_offset = new_offset
            self.render_decorator_canvas()

        # Always consume scroll when over a textarea with overflow
        return True

    def on_scroll_tick(self, e):
        if self._try_scroll_textarea(e):
            return

        if self.meta_state.scrollable:
            modal_scope = self.get_modal_scope_ids()
            # Collect all scrollable containers under the cursor, sorted smallest first
            candidates = []
            for id, data in list(self.meta_state.scrollable.items()):
                if modal_scope is not None and id not in modal_scope:
                    continue
                node = self.meta_state.id_to_node.get(id)
                if getattr(node, 'box_model', None) and node.box_model.padding_rect.contains(e.gpos):
                    area = node.box_model.padding_rect.width * node.box_model.padding_rect.height
                    candidates.append((area, node))

            candidates.sort(key=lambda x: x[0])

            # Try each candidate from smallest to largest, bubble up if can't scroll
            for _, node in candidates:
                if self._try_scroll_node(node, e):
                    self._scrollbar_show(node.id)
                    degrees_x = getattr(e.degrees, 'x', 0) if hasattr(e.degrees, 'x') else 0
                    is_wheel = abs(e.degrees.y) > 1e-5 or abs(degrees_x) > 1e-5
                    if self._smooth_scroll_factor > 0 and is_wheel:
                        self._start_scroll_anim()
                    else:
                        self.render_manager.render_scroll()
                    return

    def on_scroll(self, e):
        if self.unmounting:
            return
        self.on_scroll_tick(e)

    def _scroll_anim_tick(self):
        if self.destroying:
            self._stop_scroll_anim()
            return

        any_animating = False
        factor = self._smooth_scroll_factor

        for data in self.meta_state.scrollable.values():
            dy = data.target_offset_y - data.offset_y
            if abs(dy) > 0.5:
                data.offset_y += dy * factor
                if abs(data.target_offset_y - data.offset_y) <= 0.5:
                    data.offset_y = data.target_offset_y
                any_animating = True
            elif data.offset_y != data.target_offset_y:
                data.offset_y = data.target_offset_y

            dx = data.target_offset_x - data.offset_x
            if abs(dx) > 0.5:
                data.offset_x += dx * factor
                if abs(data.target_offset_x - data.offset_x) <= 0.5:
                    data.offset_x = data.target_offset_x
                any_animating = True
            elif data.offset_x != data.target_offset_x:
                data.offset_x = data.target_offset_x

        if any_animating:
            self.render_manager.render_scroll()
        else:
            self._stop_scroll_anim()

    def _start_scroll_anim(self):
        if not self._scroll_anim_job:
            self._scroll_anim_job = cron.interval("16ms", self._scroll_anim_tick)

    def _stop_scroll_anim(self):
        if self._scroll_anim_job:
            cron.cancel(self._scroll_anim_job)
            self._scroll_anim_job = None

    def _scrollbar_show(self, node_id):
        """Show scrollbar with fade-in, cancel any pending fade-out."""
        self.meta_state.clear_scrollbar_fade_job(node_id)
        self.meta_state.clear_scrollbar_idle_job(node_id)
        opacity = self.meta_state.get_scrollbar_opacity(node_id)
        if opacity < 1.0:
            self._scrollbar_fade_in(node_id)
        self._scrollbar_schedule_idle_hide(node_id)

    def _scrollbar_fade_in(self, node_id):
        """Animate scrollbar opacity from current to 1.0."""
        start_opacity = self.meta_state.get_scrollbar_opacity(node_id)
        if start_opacity >= 1.0:
            return
        remaining_ratio = 1.0 - start_opacity
        duration_ms = DEFAULT_SCROLL_BAR_FADE_IN_MS * remaining_ratio
        start_time = time.monotonic()

        def tick():
            if self.destroying:
                self.meta_state.clear_scrollbar_fade_job(node_id)
                return
            elapsed = (time.monotonic() - start_time) * 1000
            t = min(1.0, elapsed / duration_ms) if duration_ms > 0 else 1.0
            new_opacity = start_opacity + (1.0 - start_opacity) * t
            self.meta_state.set_scrollbar_opacity(node_id, new_opacity)
            self.render_manager.render_scroll()
            if t >= 1.0:
                self.meta_state.clear_scrollbar_fade_job(node_id)

        self.meta_state.clear_scrollbar_fade_job(node_id)
        self.meta_state.scrollbar_fade_jobs[node_id] = cron.interval("16ms", tick)

    def _scrollbar_fade_out(self, node_id):
        """Animate scrollbar opacity from current to 0.0."""
        if self.meta_state.is_scrollbar_hovered(node_id) or \
                self.meta_state.is_scrollbar_dragging(node_id):
            return
        start_opacity = self.meta_state.get_scrollbar_opacity(node_id)
        if start_opacity <= 0.0:
            return
        duration_ms = DEFAULT_SCROLL_BAR_FADE_OUT_MS * start_opacity
        start_time = time.monotonic()

        def tick():
            if self.destroying:
                self.meta_state.clear_scrollbar_fade_job(node_id)
                return
            elapsed = (time.monotonic() - start_time) * 1000
            t = min(1.0, elapsed / duration_ms) if duration_ms > 0 else 1.0
            new_opacity = start_opacity * (1.0 - t)
            self.meta_state.set_scrollbar_opacity(node_id, new_opacity)
            self.render_manager.render_scroll()
            if t >= 1.0:
                self.meta_state.clear_scrollbar_fade_job(node_id)

        self.meta_state.clear_scrollbar_fade_job(node_id)
        self.meta_state.scrollbar_fade_jobs[node_id] = cron.interval("16ms", tick)

    def _scrollbar_schedule_idle_hide(self, node_id):
        """Schedule fade-out after idle period."""
        self.meta_state.clear_scrollbar_idle_job(node_id)

        def start_fade_out():
            self.meta_state.scrollbar_idle_jobs.pop(node_id, None)
            self._scrollbar_fade_out(node_id)

        self.meta_state.scrollbar_idle_jobs[node_id] = cron.after(
            f"{DEFAULT_SCROLL_BAR_IDLE_MS}ms", start_fade_out
        )

    def is_drag_end(self):
        return self.drag_end_phase or self.render_manager.is_drag_end()

    def window_cleanup(self, hide: bool = False):
        if self.meta_state.windows:
            for id in list(self.meta_state.windows):
                node = self.meta_state.id_to_node.get(id)
                if node and node.on_close and not node.destroying:
                    try:
                        if len(inspect.signature(node.on_close).parameters) == 1:
                            node.on_close(WindowCloseEvent(hide=hide))
                        else:
                            node.on_close()
                    except Exception as e:
                        print(f"Error during window on_close: {e}")
                        log_trace()

    def destroy_blockable_canvas(self):
        if self.canvas_blockable:
            for canvas in self.canvas_blockable:
                canvas.unregister("mouse", self.on_mouse)
                canvas.unregister("scroll", self.on_scroll)
                canvas.close()
            self.is_blockable_canvas_init = False
            self.last_blockable_rects.clear()
            self.canvas_blockable.clear()

    def minimize(self):
        if self.meta_state.windows:
            for id in list(self.meta_state.windows):
                node = self.meta_state.id_to_node.get(id)
                if node and node.on_minimize and not node.destroying:
                    try:
                        node.on_minimize()
                    except Exception as e:
                        print(f"Error during window on_minimize: {e}")
                        log_trace()

    def _has_unmount_animations(self):
        """Check if any node has unmount_style + transition"""
        for node in self.meta_state.id_to_node.values():
            if getattr(node.properties, 'unmount_style', None) and node.properties.transition:
                return True
        return False

    def _start_unmount(self):
        """Begin exit animations, defer actual destruction"""
        self.unmounting = True
        self.transition_manager.start_unmount(on_complete=self._finish_unmount)

    def _finish_unmount(self):
        """Called when all exit animations complete - do actual destruction"""
        self._unmount_complete = True
        self.destroy()

    def destroy(self):
        global scroll_throttle_job
        if not self.destroying:
            if not self.unmounting and self._has_unmount_animations():
                self._start_unmount()
                return
            if self.unmounting and not self._unmount_complete:
                # Already playing unmount animations - ignore duplicate destroy calls.
                # _finish_unmount will call destroy() when animations complete.
                return
            self.destroying = True
            self.render_manager.prepare_destroy()
            # Defer effect cleanups to avoid recursive action errors when
            # a cleanup calls ui_elements_hide for another tree
            deferred_cleanups = []
            for effect in reversed(self.effects):
                if effect.cleanup:
                    deferred_cleanups.append(effect.cleanup)
            if deferred_cleanups:
                def run_deferred_cleanups():
                    for cleanup in deferred_cleanups:
                        try:
                            if len(inspect.signature(cleanup).parameters) == 1:
                                cleanup(StateEvent())
                            else:
                                cleanup()
                        except Exception as e:
                            print(f"Error during effect cleanup: {e}")
                cron.after("1ms", run_deferred_cleanups)
            self.window_cleanup(hide=False)

            if self.render_debounce_job:
                cron.cancel(self.render_debounce_job)
                self.render_debounce_job = None

            self._stop_scroll_anim()

            self.stop_cursor_refresh_cycle()
            if self.hover_validation_job:
                cron.cancel(self.hover_validation_job)
                self.hover_validation_job = None
            self.cursor_position = None
            self.cursor_refresh_rate = DEFAULT_CURSOR_REFRESH_RATE
            self.has_cursor_node = False
            self.last_mouse_event_time = 0

            if self.canvas_base:
                self.canvas_base.unregister("draw", self.on_draw_base_canvas)
                self.canvas_base.close()
                self.canvas_base = None

            if self._decorator_freeze_pending_job:
                cron.cancel(self._decorator_freeze_pending_job)
                self._decorator_freeze_pending_job = None

            if self.canvas_decorator:
                if self.is_key_controls_init:
                    self.canvas_decorator.unregister("key", self.on_key)
                    self.canvas_decorator.unregister("scroll", self.on_scroll)
                    self.is_key_controls_init = False
                self.canvas_decorator.unregister("draw", self.on_draw_decorator_canvas)
                self.canvas_decorator.close()
                self.canvas_decorator = None

            self.destroy_blockable_canvas()

            from ..platform.custom_input import custom_input_manager
            if custom_input_manager.has_focused_input:
                custom_input_manager.blur()

            self._tree_constructor = None
            self.current_base_canvas = None
            self.transition_manager.destroy()
            self.render_manager.destroy()
            state_manager.clear_state_for_tree(self)
            self.meta_state.clear()
            self.effects.clear()
            self.processing_states.clear()
            self.is_mounted = False
            self._pending_render = False
            self.interactive_node_list.clear()
            if self.root_node:
                self.root_node.destroy()
            self.root_node = None
            self.draggable_node = None
            self.drag_handle_node = None
            self.draggable_node_delta_pos = None
            self.absolute_nodes.clear()
            self.fixed_nodes.clear()
            scroll_throttle_job = None
            self.render_list.clear()
            self.render_layers.clear()
            # Only clear hint state if no other trees have hints
            has_other_trees_with_hints = any(
                tree != self and (tree.meta_state.inputs or tree.meta_state.buttons)
                for tree in store.trees
            )
            if not has_other_trees_with_hints:
                hint_clear_state()
            self.render_cause.clear()
            self.last_base_snapshot = None
            self.last_hints_snapshot = None
            state_manager.clear_tree(self)
            self.destroying = False

    def _assign_dragging_node_and_handle(self, node: NodeType):
        if hasattr(node.properties, "draggable") and node.properties.draggable:
            if node.depth > 1 or node.element_type not in [ELEMENT_ENUM_TYPE["div"], ELEMENT_ENUM_TYPE["form"], ELEMENT_ENUM_TYPE["window"]]:
                raise Exception('Only top level divs can be draggable. Assign "draggable" property to the top level div (Not "screen" or "active_window").')
            self.draggable_node = node
            self.drag_handle_node = node

        if node.properties.drag_handle:
            self.drag_handle_node = node

    def _assign_missing_ids(self, node: NodeType, node_index_path: list[int]):
        requires_id = False
        if node.interactive:
            self.interactive_node_list.append(node)
            requires_id = True
        elif node.element_type in (ELEMENT_ENUM_TYPE["button"], ELEMENT_ENUM_TYPE["link"]) \
                and getattr(node, 'on_click', None):
            requires_id = True
        elif node.properties.is_scrollable() or getattr(node.properties, "draggable", False):
            requires_id = True
        elif node.element_type == ELEMENT_ENUM_TYPE["window"]:
            requires_id = True
        elif getattr(node.properties, "for_id", False):
            requires_id = True
        elif node.properties.transition:
            requires_id = True
        elif getattr(node, 'selectable', False):
            requires_id = True

        if requires_id and not node.id:
            node_index_path_str = "-".join(map(str, node_index_path)) # "1-2-0"
            node.id = self.guid + node_index_path_str

    def _use_meta_state(self, node: NodeType):
        if node.id:
            self.meta_state.map_id_to_node(node.id, node)

            if overrides := self.meta_state.get_ref_property_overrides(node.id):
                node.properties.update_overrides(overrides)

            if getattr(node, 'on_click', None):
                self.meta_state.add_button(node.id)
            elif node.element_type in (ELEMENT_ENUM_TYPE["text"], ELEMENT_ENUM_TYPE["code"]):
                if getattr(node.properties, 'for_id', None):
                    self.meta_state.add_text_with_for_id(node.id, node.properties.for_id)
                elif getattr(node, 'selectable', False):
                    pass
                else:
                    self.meta_state.use_text_mutation(node.id, initial_text=node.text)
            elif node.element_type == ELEMENT_ENUM_TYPE["window"]:
                self.meta_state.add_window(node.id)

            if node.properties.is_scrollable():
                self.meta_state.add_scrollable(node.id)

            if node.properties.draggable:
                self.meta_state.add_draggable(node.id)

            if node.properties.resizable and node.id:
                self.meta_state.resizable_nodes.add(node.id)

            if node.properties.transition:
                self.transition_manager.detect_changes(node.id, node)

    def _use_decorator(self, node: NodeType):
        if not node.properties.highlight_style and node.properties.transition \
                and isinstance(node.properties.transition, dict) and node.interactive \
                and node.properties.highlight_color:
            has_color_transition = any(
                prop in node.properties.transition or "all" in node.properties.transition
                for prop in ANIMATABLE_COLOR_PROPERTIES
            )
            if has_color_transition:
                node.properties.highlight_style = {
                    "background_color": node.properties.highlight_color
                }

        if ((node.disabled and node.properties.disabled_style) or node.properties.highlight_style) \
                and node.uses_decoration_render == False:
            target_node = node if node.id else find_closest_parent_with_id(node.parent_node)
            if target_node and target_node.id:
                self.meta_state.add_decoration_render(target_node.id)
                node.uses_decoration_render = True
                for child_node in target_node.get_children_nodes():
                    child_node.uses_decoration_render = True

        if node.element_type == ELEMENT_ENUM_TYPE["select"] \
                and getattr(node, 'is_open', False) and node.id:
            self.meta_state.add_decoration_render(node.id)

        if node.uses_decoration_render and (node.properties.z_index or 0) > 0:
            self.meta_state.has_hit_priority_overlay = True

    def _apply_constraint_nodes(self, node: NodeType, constraint_nodes: list[NodeType]):
        if node.properties.width is not None or \
                node.properties.max_width is not None or \
                node.properties.height is not None or \
                node.properties.max_height is not None or \
                node.properties.is_scrollable():
            if constraint_nodes is None:
                constraint_nodes = []
            constraint_nodes = constraint_nodes + [node]

        if constraint_nodes:
            for constraint in constraint_nodes:
                node.add_constraint_node(constraint)

        return constraint_nodes

    def _cascade_clip_nodes(self, node: NodeType, clip_nodes: list[NodeType]):
        if node.properties.overflow and node.properties.overflow.is_boundary:
            if clip_nodes is None:
                clip_nodes = []
            clip_nodes = clip_nodes + [node]

        if clip_nodes:
            for clip_node in clip_nodes:
                node.add_clip_node(clip_node)

        return clip_nodes

    def _check_deprecated_ui(self, node: NodeType):
        if node.element_type == ELEMENT_ENUM_TYPE["screen"] and node.deprecated_ui:
            self.render_version = 1

    def _apply_justify_content_if_space_evenly(self, node: NodeType):
        if node.properties.justify_content == "space_evenly":
            for child_node in node.get_children_nodes():
                child_node.properties.flex = 1

    def _find_parent_relative_positional_node(self, node: NodeType):
        if node.properties.position != "static":
            return weakref.ref(node)
        elif node.parent_node:
            return self._find_parent_relative_positional_node(node.parent_node)
        else:
            return weakref.ref(node.tree.root_node)

    def _cascade_children_z_subindex(self, node: NodeType):
        """
        Within each z_index, we have z_subindex to help with stacking order.
        This is for example of a parent is position absolute, it should be
        treated higher than relative positioned siblings, and it's children
        get the cascaded z_subindex.
        """
        children_nodes = node.get_children_nodes()
        if children_nodes:
            for child_node in children_nodes:
                child_node.z_subindex = node.z_subindex
                self._cascade_children_z_subindex(child_node)

    def _set_interactive_ids(self, node: NodeType):
        if node.interactive and node.id:
            node.interactive_id = node.id

        if node.interactive_id:
            for child in node.get_children_nodes():
                child.interactive_id = node.interactive_id

    def _check_modals(self, node: NodeType):
        if node.element_type == ELEMENT_ENUM_TYPE["modal"] and node.properties.open:
            # Last open modal in walk order wins (deeper / later siblings sit on top).
            self._active_modal_node_ref = weakref.ref(node)
            self._cached_modal_scope_ids = None

    @property
    def active_modal_node(self) -> Optional[NodeType]:
        return self._active_modal_node_ref() if self._active_modal_node_ref else None

    def get_modal_scope_ids(self) -> Optional[set]:
        """Set of node ids inside the active modal's subtree, or None when no
        modal is open. Hot-path callers can early-out on a single attr check
        before invoking this. Computed lazily and cached per render."""
        if not self._active_modal_node_ref:
            return None
        if self._cached_modal_scope_ids is not None:
            return self._cached_modal_scope_ids
        modal = self._active_modal_node_ref()
        if not modal:
            return None
        ids = set()
        stack = [modal]
        while stack:
            cur = stack.pop()
            cur_id = getattr(cur, 'id', None)
            if cur_id:
                ids.add(cur_id)
            stack.extend(getattr(cur, 'children_nodes', None) or ())
        self._cached_modal_scope_ids = ids
        return ids

    def _handle_modal_open_transition(self):
        """Detect modal open events across renders and force-collapse any
        scrollbars on background scrollables so a previously-visible bar
        doesn't bleed through under the panel."""
        modal = self.active_modal_node
        current_id = modal.id if modal else None
        prev_id = self._prev_active_modal_id
        self._prev_active_modal_id = current_id
        if current_id and current_id != prev_id:
            self._force_hide_background_scrollbars()

    def _force_hide_background_scrollbars(self):
        modal_scope = self.get_modal_scope_ids()
        if modal_scope is None:
            return
        hov_id = self.meta_state.scrollbar_hovered_id
        if hov_id and hov_id not in modal_scope:
            self.meta_state.clear_scrollbar_hover()
        needs_render = False
        for node_id in list(self.meta_state.scrollable.keys()):
            if node_id in modal_scope:
                continue
            self.meta_state.clear_scrollbar_fade_job(node_id)
            self.meta_state.clear_scrollbar_idle_job(node_id)
            if self.meta_state.get_scrollbar_opacity(node_id) > 0.0:
                self.meta_state.set_scrollbar_opacity(node_id, 0.0)
                needs_render = True
        if needs_render:
            self.render_manager.render_scroll()

    def _modal_backdrop_blocked_by_panel(self, gpos, source_id) -> bool:
        """When `source_id` is the active modal's clickable backdrop and `gpos`
        falls inside the panel's rect, the panel visually intercepts the click
        — so it must not pass through to dismiss the modal."""
        modal = self.active_modal_node
        if not modal:
            return False
        backdrop = getattr(modal, 'backdrop_node', None)
        panel = getattr(modal, 'panel_node', None)
        if not backdrop or not panel:
            return False
        if source_id != backdrop.id:
            return False
        if panel.box_model and panel.box_model.border_rect and \
                panel.box_model.border_rect.contains(gpos):
            return True
        return False

    def _setup_nonlayout_nodes(self, node: NodeType):
        if node.properties.position != "static":
            if node.element_type == "cursor":
                self.has_cursor_node = True
                self.cursor_refresh_rate = getattr(node, 'refresh_rate', DEFAULT_CURSOR_REFRESH_RATE)
                self.absolute_nodes.append(weakref.ref(node))
                node.relative_positional_node = weakref.ref(self.root_node)
            elif node.properties.position == "fixed":
                self.fixed_nodes.append(weakref.ref(node))
                node.relative_positional_node = weakref.ref(self.root_node)
                node.z_subindex += 1
            elif node.properties.position == "absolute":
                self.absolute_nodes.append(weakref.ref(node))
                node.relative_positional_node = self._find_parent_relative_positional_node(node.parent_node)

            if node.properties.position != "relative":
                node.z_subindex += 1
            self._cascade_children_z_subindex(node)

    def _resolve_component(self, node: NodeType, node_index_path: list[int]):
        if isinstance(node, ComponentType):
            state_manager.set_processing_tree(self)
            try:
                node_tree = node.initialize(node_index_path)
            finally:
                state_manager.set_processing_tree(None)
            self.meta_state.add_component(node)
            return node_tree
        return node

    def init_node_hierarchy(
            self,
            current_node: NodeType,
            node_index_path = [], # [1, 2, 0]
            constraint_nodes: list[NodeType] = None,
            clip_nodes: list[NodeType] = None
        ):
        """
        First step in the rendering process. Runs before layout.
        Runs once for each node in the tree to establish meta_state and relationships
        """
        if not node_index_path:
            # Root call: clear per-render modal tracking before walking the tree.
            self._active_modal_node_ref = None
            self._cached_modal_scope_ids = None

        current_node = self._resolve_component(current_node, node_index_path)

        # Safety check - ensure current_node is valid
        if current_node is None:
            return

        current_node.tree = self
        current_node.depth = len(node_index_path)
        current_node.node_index_path = node_index_path

        if getattr(current_node, 'parent_node', None):
            current_node.inherit_cascaded_properties(current_node.parent_node)
        self._assign_dragging_node_and_handle(current_node)
        self._assign_missing_ids(current_node, node_index_path)
        self._set_interactive_ids(current_node)
        if not self.is_mounted:
            state_manager.autofocus_node(current_node)
        self._use_meta_state(current_node)
        # use decorator has some redundant looping. refactor this later
        self._use_decorator(current_node)
        self._check_modals(current_node)
        constraint_nodes = self._apply_constraint_nodes(current_node, constraint_nodes)
        clip_nodes = self._cascade_clip_nodes(current_node, clip_nodes)
        self._setup_nonlayout_nodes(current_node)
        self._check_deprecated_ui(current_node)
        self._apply_justify_content_if_space_evenly(current_node)

        inject = getattr(current_node, "_maybe_inject_scroll_buttons", None)
        if inject:
            inject()

        for i, child_node in enumerate(current_node.get_children_nodes()):
            child_key = getattr(child_node, "key", None)
            # Keyed children get a stable path segment so their state survives
            # sibling reordering. Unkeyed children fall back to position index.
            segment = f"k_{child_key}" if child_key is not None else i
            self.init_node_hierarchy(child_node, node_index_path + [segment], constraint_nodes, clip_nodes)

        if not node_index_path:
            # root call only - per-node rebuild is O(n^2)
            entity_manager.synchronize_global_ids()

    def consume_effects(self):
        for effect in list(store.staged_effects):
            if effect.tree == self or effect.tree is None:
                self.effects.append(effect)
                store.staged_effects.remove(effect)

    def consume_components(self):
        if not self.meta_state._staged_components and not self.meta_state._components:
            return
        prev_ids = set(self.meta_state._components)
        new_ids = set(self.meta_state._staged_components)

        self.meta_state.new_component_ids = new_ids - prev_ids
        self.meta_state.removed_component_ids = prev_ids - new_ids

        self.meta_state._components = self.meta_state._staged_components
        self.meta_state._staged_components = {}

        if self.meta_state.removed_component_ids:
            self.on_component_unmount_effect_cleanups()

    def have_blockable_rects_changed(self, blockable_rects):
        dimension_change = False
        position_change = False

        if len(blockable_rects) != len(self.last_blockable_rects):
            dimension_change = True
            position_change = True

        for i, rect in enumerate(self.last_blockable_rects):
            if not rect.width == blockable_rects[i].width or not rect.height == blockable_rects[i].height:
                dimension_change = True
                break

        for i, rect in enumerate(self.last_blockable_rects):
            if not rect.x == blockable_rects[i].x or not rect.y == blockable_rects[i].y:
                position_change = True
                break

        return dimension_change, position_change

    def move_blockable_canvas_rects(self, blockable_rects, offset=Point2d):
        if blockable_rects and len(blockable_rects) == len(self.canvas_blockable):
            for i, rect in enumerate(blockable_rects):
                offset = self.meta_state.get_current_drag_offset(self.draggable_node.id)
                x = rect.x + offset.x
                y = rect.y + offset.y
                self.canvas_blockable[i].move(x, y)
        self.last_blockable_rects.clear()
        self.last_blockable_rects.extend(blockable_rects)

    def should_rerender_blockable_canvas(self):
        return self.render_manager.render_cause == RenderCause.STATE_CHANGE \
            or self.render_manager.render_cause == RenderCause.DRAG_START \
            or self.render_manager.render_cause == RenderCause.DRAGGING \
            or self.is_drag_end()

    def calculate_blockable_rects(self):
        """
        If we have at least one interactive element, then we will consider
        the whole content area as blockable. If we have an inputs, then we
        need to carve holes for those inputs because they are managed separately.
        """
        blockable_rects = []

        if self.meta_state.buttons or self.meta_state.inputs or self.draggable_node or self.interactive_node_list or self.meta_state.scrollable:
            full_rect = self.draggable_node.box_model.border_rect \
                if getattr(self.draggable_node, 'box_model', None) \
                else self.root_node.box_model.content_children_rect

            # Expand blockable area to cover resize edge detection zone
            has_resizable = bool(self.meta_state.resizable_nodes) or any(
                self.meta_state.id_to_node.get(wid) and
                getattr(self.meta_state.id_to_node[wid].properties, 'resizable', False)
                for wid in self.meta_state.windows
            )
            if has_resizable:
                threshold = scale_value(RESIZE_EDGE_THRESHOLD)
                full_rect = Rect(
                    full_rect.x - threshold,
                    full_rect.y - threshold,
                    full_rect.width + threshold * 2,
                    full_rect.height + threshold * 2
                )

            blockable_rects = [full_rect]

            if self.meta_state.inputs:
                for input_id, input_data in list(self.meta_state.inputs.items()):
                    if not input_data.input or not self.meta_state.id_to_node.get(input_id):
                        continue
                    input_rect = self.meta_state.id_to_node[input_id].box_model.visible_rect

                    new_rects = []
                    for rect in blockable_rects:
                        if rect.intersects(input_rect):
                            new_rects.extend(subtract_rect(rect, input_rect))
                        else:
                            new_rects.append(rect)
                    blockable_rects = new_rects

        return blockable_rects

    def on_test_draw_blockable_canvas(self, canvas: SkiaCanvas):
        canvas.paint.color = "FF0000"
        canvas.draw_rect(canvas.rect)

    def draw_blockable_canvases(self):
        try:
            is_rerender = False

            if self.is_blockable_canvas_init:
                if self.should_rerender_blockable_canvas():
                    is_rerender = True
                else:
                    return

            if not self.root_node or not self.root_node.box_model:
                return

            blockable_rects = self.calculate_blockable_rects()

            if self.render_manager.render_cause == RenderCause.DRAGGING \
                    or self.render_manager.render_cause == RenderCause.DRAG_START:
                offset = self.meta_state.get_current_drag_offset(self.draggable_node.id)
                self.move_blockable_canvas_rects(blockable_rects, offset)
                return
            elif self.render_manager.render_cause == RenderCause.DRAG_END:
                return

            if is_rerender:
                dimension_change, position_change = self.have_blockable_rects_changed(blockable_rects)
                if dimension_change:
                    self.destroy_blockable_canvas()
                elif position_change:
                    self.move_blockable_canvas_rects(blockable_rects)
                    return

            if not self.is_blockable_canvas_init:
                self.is_blockable_canvas_init = True
                self.last_blockable_rects.clear()
                self.last_blockable_rects.extend(blockable_rects)
                for rect in blockable_rects:
                    canvas = CanvasWeakRef(self.Canvas.from_rect(rect))
                    self.canvas_blockable.append(canvas)
                    canvas.blocks_mouse = True
                    canvas.register("mouse", self.on_mouse)
                    canvas.register("scroll", self.on_scroll)
                    canvas.freeze()
        except Exception as e:
            print(f"talon_ui_elements draw_blockable_canvases error: {e}")
            self.destroy()