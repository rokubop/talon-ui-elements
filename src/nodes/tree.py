import inspect
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
from typing import Any, Callable
from collections import defaultdict
from dataclasses import dataclass

from ..constants import ELEMENT_ENUM_TYPE, DRAG_INIT_THRESHOLD, DEFAULT_CURSOR_REFRESH_RATE
from ..utils import draw_rect, scale_value
from ..canvas_wrapper import CanvasWeakRef
from ..border_radius import draw_manual_rounded_rect_path
from ..core.entity_manager import entity_manager
from ..core.animations import TransitionManager
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
)
from ..hints import draw_hint, get_hint_generator, hint_clear_state, hint_tag_enable
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
        self.view_height = 0
        self.max_height = 0

    def reevaluate(self, node: NodeType):
        max_height = node.box_model.content_children_with_padding_size.height
        view_height = node.box_model.padding_size.height
        if view_height != self.view_height or max_height != self.max_height:
            self.view_height = view_height
            self.max_height = max_height
            self.offset_x = 0
            self.offset_y = 0

@dataclass
class DraggableOffset:
    x: int
    y: int


class MetaState(MetaStateType):
    def __init__(self):
        self._buttons = set()
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
        self.ref_property_overrides = {}
        self.unhighlight_jobs = {}
        self.new_component_ids = set()
        self.removed_component_ids = set()
        self.scrollbar_hovered_id = None
        self.scrollbar_dragging_id = None
        self.scrollbar_drag_start_y = None
        self.scrollbar_drag_start_offset_y = None

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
        self._buttons.add(id)

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
        if id in self._id_to_node and id in self._highlighted:
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
        entity_manager.synchronize_global_ids()

    def prepare_node_transition(self):
        self._staged_id_to_node = {}

    def commit_node_transition(self):
        self._id_to_node = self._staged_id_to_node
        self._staged_id_to_node = None
        entity_manager.synchronize_global_ids()

    def get_hover_links(self):
        return list(
            (b, b) for b in self._buttons
        ) + list(
            self._text_with_for_ids.items()
        )

    # Scrollbar interaction state management
    def set_scrollbar_hover(self, node_id):
        self.scrollbar_hovered_id = node_id

    def clear_scrollbar_hover(self):
        self.scrollbar_hovered_id = None

    def is_scrollbar_hovered(self, node_id):
        return self.scrollbar_hovered_id == node_id

    def start_scrollbar_drag(self, node_id, mouse_y, scroll_offset_y):
        self.scrollbar_dragging_id = node_id
        self.scrollbar_drag_start_y = mouse_y
        self.scrollbar_drag_start_offset_y = scroll_offset_y

    def clear_scrollbar_drag(self):
        self.scrollbar_dragging_id = None
        self.scrollbar_drag_start_y = None
        self.scrollbar_drag_start_offset_y = None

    def is_scrollbar_dragging(self, node_id=None):
        if node_id:
            return self.scrollbar_dragging_id == node_id
        return self.scrollbar_dragging_id is not None

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
        self._states.clear()
        self._style_mutations.clear()
        self._text_mutations.clear()
        self.windows.clear()
        self.unhighlight_jobs.clear()
        self.ref_property_overrides.clear()
        self.new_component_ids.clear()
        self.removed_component_ids.clear()
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
        self.active_modal_count = 0
        self.canvas_base = None
        self.canvas_blockable = []
        self.canvas_decorator = None
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
        self.drag_end_phase = False
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
        self.scroll_amount_per_tick = settings.get("user.ui_elements_scroll_speed")
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

    def validate_root_node(self):
        if self.root_node.element_type not in ["screen", "active_window"]:
            raise Exception("Root node must be a screen or active_window element")

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
            self.validate_root_node()
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
            node.compute_clip_regions_cache()
            for child in node.get_children_nodes():
                compute_for_node(child)

        compute_for_node(self.root_node)

    def nonlayout_flow(self):
        for node in self.absolute_nodes + self.fixed_nodes:
            node: NodeType = node()
            if node and node.tree == self:
                relative_positional_node: NodeType = node.relative_positional_node()
                node.v2_measure_intrinsic_size(self.current_base_canvas)
                node.v2_grow_size()
                node.v2_constrain_size()
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
        for id in list(self.meta_state.decoration_renders.keys()):
            if id in self.meta_state.id_to_node:
                node = self.meta_state.id_to_node[id]
                clip_count = self.apply_clip_regions(canvas, node, transforms)
                node.v2_render_decorator(canvas, transforms)
                self.restore_clip_regions(canvas, clip_count)

    def on_draw_decorator_canvas(self, canvas: SkiaCanvas):
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
                    if self.render_manager.render_cause == RenderCause.STATE_CHANGE:
                        self.reconcile_mouse_highlight()
                    self.draw_decoration_renders(draw_canvas, transforms)
                    self.draw_highlight_overlays(draw_canvas, transforms.offset)
                    canvas.paint.color = "FFFFFF"
                    self.draw_text_mutations(draw_canvas, Point2d(0, 0)) # Why does 0,0 work here?
                    if self.interactive_node_list or self.draggable_node:
                        if state_manager.is_focus_visible():
                            self.draw_focus_outline(draw_canvas, offset)
                        if self.show_hints:
                            self.draw_hints(draw_canvas, transforms)
                    self.init_key_controls()
                    self.draw_blockable_canvases()
                    self.on_fully_rendered()
                finally:
                    state_manager.set_processing_tree(None)
                self.finish_current_render()
        except Exception as e:
            print(f"Error during decorator canvas rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

    def on_draw_base_canvas_dragging(self, canvas: SkiaCanvas):
        try:
            self.move_canvas(canvas)
            self.move_inputs()
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
        except Exception as e:
            print(f"Error during drag end rendering: {e}")
            log_trace()
            self.finish_current_render()
            self.destroy()

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
            self.reset_cursor()
            self.init_node_hierarchy(self.root_node)
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
                self.render_decorator_canvas()
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
        draw_text_simple(
            canvas,
            self.meta_state.get_text_mutation(id),
            node.properties.color,
            node.properties,
            x,
            y
        )

        self.restore_clip_regions(canvas, clip_count)

    def draw_text_mutations(self, canvas: SkiaCanvas, offset: Point2d):
        for id, text_value in list(self.meta_state.text_mutations.items()):
            if id in self.meta_state.id_to_node:
                node = self.meta_state.id_to_node[id]
                self.draw_text_mutation(canvas, node, id, offset)

    def finish_current_render(self):
        self.render_manager.finish_current_render()

    def draw_hints(self, canvas: SkiaCanvas, transforms: RenderTransforms = None):
        if self.meta_state.inputs or self.meta_state.buttons:
            hint_tag_enable()
            hint_generator = get_hint_generator()
            for node in list(self.meta_state.id_to_node.values()):
                if node.element_type in ["button", "input_text", "link"] and not node.disabled:
                    draw_hint(canvas, node, hint_generator(node), transforms=transforms)

    def refresh_decorator_canvas(self):
        if self.canvas_decorator:
            self.canvas_decorator.freeze()

    def highlight_forced(self, id: str, color: str = None):
        self.render_cause.highlight_change()
        self.meta_state.set_highlighted(id, color)
        self.canvas_decorator.freeze()

    def highlight_no_render(self, id: str, color: str = None):
        if id in self.meta_state.highlighted:
            return
        self.meta_state.set_highlighted(id, color)

    def highlight(self, id: str, color: str = None):
        if id in self.meta_state.highlighted:
            return

        self.render_cause.highlight_change()
        self.meta_state.set_highlighted(id, color)
        self.canvas_decorator.freeze()

    def unhighlight_no_render(self, id: str):
        if id in self.meta_state.highlighted:
            self.meta_state.set_unhighlighted(id)

            job = self.meta_state.unhighlight_jobs.pop(id, None)
            if job:
                cron.cancel(job[0])

    def unhighlight(self, id: str):
        if id in self.meta_state.highlighted:
            self.render_cause.highlight_change()
            self.meta_state.set_unhighlighted(id)

            job = self.meta_state.unhighlight_jobs.pop(id, None)
            if job:
                cron.cancel(job[0])

            self.canvas_decorator.freeze()

    def highlight_briefly(self, id: str, color: str = None, duration: int = 150):
        if id in self.meta_state.unhighlight_jobs:
            job, _ = self.meta_state.unhighlight_jobs.pop(id)
            cron.cancel(job)
        self.highlight(id, color)
        pending_unhighlight = lambda: self.unhighlight(id)
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

        if key_string == "space" or key_string == "enter" or key_string == "return":
            focused_node = state_manager.get_focused_node()
            if getattr(focused_node, 'properties', None) and getattr(focused_node.properties, "on_click", None):
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

    def _is_draggable_ui(self):
        # Just check 1 level deep
        return any([node.properties.draggable for node in self.root_node.get_children_nodes()])

    def create_canvas(self):
        rect = self.root_node.boundary_rect

        if self._is_draggable_ui():
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

    def render_decorator_canvas(self):
        if not self.canvas_decorator and not self.render_manager.is_destroying:
            self.canvas_decorator = self.create_canvas()
            self.canvas_decorator.register("draw", self.on_draw_decorator_canvas)
            if self.interactive_node_list:
                focused_tree = state_manager.get_focused_tree()
                if focused_tree == self:
                    focus_canvas = True
                    node = state_manager.get_focused_node()
                    if node and node.tree == self and node.element_type == "input_text":
                        # input text has its own focus managed by Talon
                        focus_canvas = False
                    if focus_canvas:
                        self.canvas_decorator.focused = True
                elif not focused_tree:
                    self.canvas_decorator.focused = True

        if self.canvas_decorator:
            self.canvas_decorator.freeze()

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
                self.on_state_change_effect_cleanups()
                self.meta_state.clear_nodes()
                self.init_tree_constructor()

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

        mouse_delta_y = gpos.y - self.meta_state.scrollbar_drag_start_y
        view_height = scrollable_data.view_height
        max_height = scrollable_data.max_height
        thumb_height = node.box_model.scroll_bar_thumb_rect.height
        track_height = node.box_model.padding_size.height

        thumb_travel_distance = track_height - thumb_height
        content_travel_distance = max_height - view_height

        if thumb_travel_distance > 0 and content_travel_distance > 0:
            # Convert thumb movement to content scroll (inverse ratio)
            scroll_delta = -(mouse_delta_y / thumb_travel_distance) * content_travel_distance
            new_offset_y = self.meta_state.scrollbar_drag_start_offset_y + scroll_delta
            new_offset_y = max(view_height - max_height, min(0, new_offset_y))
            scrollable_data.offset_y = new_offset_y
            self.render_manager.render_scrollbar_dragging()

    def handle_scrollbar_mousedown(self, gpos):
        """Check for scrollbar click and initiate drag if found."""
        for node_id, scrollable_data in list(self.meta_state.scrollable.items()):
            node = self.meta_state.id_to_node.get(node_id)
            if node and node.box_model and node.box_model.scroll_bar_thumb_rect:
                if node.box_model.scroll_bar_thumb_rect.contains(gpos):
                    self.meta_state.start_scrollbar_drag(node_id, gpos.y, scrollable_data.offset_y)
                    self.render_manager.pause()
                    self.render_base_canvas()
                    return True
        return False

    def handle_scrollbar_mouseup(self, gpos):
        """Handle scrollbar drag end and restore hover state."""
        self.render_manager.resume()
        self.meta_state.clear_scrollbar_drag()
        self.render_base_canvas()
        self.check_scrollbar_hover(gpos)

    def check_scrollbar_hover(self, gpos):
        """Check if mouse is hovering over any scrollbar thumb and update visual state."""
        if self.meta_state.is_scrollbar_dragging():
            return

        prev_hovered_id = self.meta_state.scrollbar_hovered_id
        new_hovered_id = None

        for node_id, scrollable_data in list(self.meta_state.scrollable.items()):
            node = self.meta_state.id_to_node.get(node_id)
            if node and node.box_model and node.box_model.scroll_bar_thumb_rect:
                if node.box_model.scroll_bar_thumb_rect.contains(gpos):
                    new_hovered_id = node_id
                    break

        if new_hovered_id != prev_hovered_id:
            if new_hovered_id:
                self.meta_state.set_scrollbar_hover(new_hovered_id)
            else:
                self.meta_state.clear_scrollbar_hover()
            self.render_base_canvas()

    def on_hover(self, gpos):
        try:
            if not state_manager.is_drag_active():
                changed = False
                new_hovered_id = None
                prev_hovered_id = state_manager.get_hovered_id()
                for source_id, target_id in self.meta_state.get_hover_links():
                    source_node = self.meta_state.id_to_node.get(source_id, None)
                    target_node = source_node
                    if source_id != target_id:
                        target_node = self.meta_state.id_to_node.get(target_id, None)
                    if source_node and not getattr(target_node, 'disabled', False):
                        if source_node.is_fully_clipped_by_scroll():
                            continue
                        if source_node and source_node.box_model and source_node.box_model.padding_rect.contains(gpos):
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

        except Exception as e:
            print(f"talon_ui_elements on_hover error: {e}")
            self.destroy()

    def get_mouse_hovered_input_id(self, gpos):
        for id, input_data in list(self.meta_state.inputs.items()):
            if input_data.input and input_data.input.rect.contains(gpos):
                return id
        return None

    def on_mousemove(self, gpos):
        if self.meta_state.is_scrollbar_dragging():
            self.handle_scrollbar_drag_move(gpos)
            return

        if self.is_drag_end():
            return

        start_pos = state_manager.get_mousedown_start_pos()
        if start_pos:
            state_manager.set_mousedown_start_offset(gpos - start_pos)

        if start_pos and not self.active_modal_count and state_manager.get_drag_relative_offset():
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
        if self.handle_scrollbar_mousedown(gpos):
            return

        hovered_id = state_manager.get_hovered_id()
        state_manager.set_mousedown_start_pos(gpos)

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
                state_manager.focus_node(node, visible=False)
                return

        if self.root_node.box_model:
            if self.root_node.box_model.content_children_rect.contains(gpos):
                state_manager.blur()
            else:
                state_manager.blur_all()

    def click_node(self, node: NodeType):
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

    def validate_hover_state(self):
        """Validate hover state and clean up if mouse left the UI."""
        changed = False
        current_pos = self.get_cursor_position()

        hovered_id = state_manager.get_hovered_id()
        if hovered_id and not state_manager.is_drag_active():
            node = self.meta_state.id_to_node.get(hovered_id)

            if node and node.box_model:
                try:
                    if not node.box_model.padding_rect.contains(current_pos):
                        self.unhighlight_no_render(hovered_id)
                        state_manager.set_hovered_id(None)
                        changed = True
                except (AttributeError, TypeError):
                    # Box model changed/destroyed between check and access
                    state_manager.set_hovered_id(None)
                    changed = True
            else:
                state_manager.set_hovered_id(None)
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
        hovered_id = state_manager.get_hovered_id()
        if hovered_id and last_clicked_pos:
            node = self.meta_state.id_to_node.get(hovered_id)
            if node and node.box_model and node.box_model.padding_rect.contains(last_clicked_pos):
                self.meta_state.set_highlighted(hovered_id, node.properties.highlight_color)
            else:
                self.meta_state.set_unhighlighted(hovered_id)
                state_manager.set_hovered_id(None)
        state_manager.set_last_clicked_pos(None)

    def on_mouse(self, e: MouseEvent):
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

    def on_scroll_tick(self, e):
        if self.meta_state.scrollable:
            smallest_node = None
            for id, data in list(self.meta_state.scrollable.items()):
                node = self.meta_state.id_to_node.get(id)
                if getattr(node, 'box_model', None) and node.box_model.padding_rect.contains(e.gpos):
                    smallest_node = node if not smallest_node or node.box_model.padding_rect.height < smallest_node.box_model.padding_rect.height else smallest_node

            if smallest_node:
                max_height = smallest_node.box_model.content_children_with_padding_size.height
                view_height = smallest_node.box_model.padding_size.height

                if max_height <= view_height:
                    return

                # mouse wheel
                if abs(e.degrees.y) > 1e-5:
                    offset_y = self.scroll_amount_per_tick if e.degrees.y > 0 else -self.scroll_amount_per_tick
                # touchpad
                elif abs(e.pixels.y) > 1e-5:
                    offset_y = e.pixels.y
                else:
                    return

                max_positive_offset_y = 0
                max_negative_offset = view_height - max_height

                new_offset_y = self.meta_state.scrollable[smallest_node.id].offset_y + offset_y

                if new_offset_y > max_positive_offset_y:
                    new_offset_y = max_positive_offset_y
                elif new_offset_y < max_negative_offset:
                    new_offset_y = max_negative_offset

                self.meta_state.scrollable[smallest_node.id].offset_y = new_offset_y
                self.meta_state.scrollable[smallest_node.id].view_height = view_height
                self.meta_state.scrollable[smallest_node.id].max_height = max_height
                self.render_manager.render_scroll()

    def on_scroll(self, e):
        self.on_scroll_tick(e)

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

    def destroy(self):
        global scroll_throttle_job
        if not self.destroying:
            self.destroying = True
            self.render_manager.prepare_destroy()
            for effect in reversed(self.effects):
                if effect.cleanup:
                    if len(inspect.signature(effect.cleanup).parameters) == 1:
                        effect.cleanup(StateEvent())
                    else:
                        effect.cleanup()
            self.window_cleanup(hide=False)

            if self.render_debounce_job:
                cron.cancel(self.render_debounce_job)
                self.render_debounce_job = None

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

            if self.canvas_decorator:
                if self.is_key_controls_init:
                    self.canvas_decorator.unregister("key", self.on_key)
                    self.is_key_controls_init = False
                self.canvas_decorator.unregister("draw", self.on_draw_decorator_canvas)
                self.canvas_decorator.close()
                self.canvas_decorator = None

            self.destroy_blockable_canvas()

            self._tree_constructor = None
            self.current_base_canvas = None
            self.transition_manager.destroy()
            self.render_manager.destroy()
            state_manager.clear_state_for_tree(self)
            self.meta_state.clear()
            self.effects.clear()
            self.processing_states.clear()
            self.is_mounted = False
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
            if node.depth > 1 or node.element_type not in [ELEMENT_ENUM_TYPE["div"], ELEMENT_ENUM_TYPE["window"]]:
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
        elif node.properties.is_scrollable() or getattr(node.properties, "draggable", False):
            requires_id = True
        elif node.element_type == ELEMENT_ENUM_TYPE["window"]:
            requires_id = True
        elif getattr(node.properties, "for_id", False):
            requires_id = True
        elif node.properties.transition:
            requires_id = True

        if requires_id and not node.id:
            node_index_path_str = "-".join(map(str, node_index_path)) # "1-2-0"
            node.id = self.guid + node_index_path_str

    def _use_meta_state(self, node: NodeType):
        if node.id:
            self.meta_state.map_id_to_node(node.id, node)

            if overrides := self.meta_state.get_ref_property_overrides(node.id):
                node.properties.update_overrides(overrides)

            if node.element_type == ELEMENT_ENUM_TYPE["button"] or \
                    node.element_type == ELEMENT_ENUM_TYPE["link"]:
                self.meta_state.add_button(node.id)
            elif node.element_type == ELEMENT_ENUM_TYPE["text"]:
                if node.properties.for_id:
                    self.meta_state.add_text_with_for_id(node.id, node.properties.for_id)
                else:
                    self.meta_state.use_text_mutation(node.id, initial_text=node.text)
            elif node.element_type == ELEMENT_ENUM_TYPE["window"]:
                self.meta_state.add_window(node.id)

            if node.properties.is_scrollable():
                self.meta_state.add_scrollable(node.id)

            if node.properties.draggable:
                self.meta_state.add_draggable(node.id)

            if node.properties.transition:
                self.transition_manager.detect_changes(node.id, node)

    def _use_decorator(self, node: NodeType):
        if ((node.disabled and node.properties.disabled_style) or node.properties.highlight_style) \
                and node.uses_decoration_render == False:
            target_node = node if node.id else find_closest_parent_with_id(node.parent_node)
            if target_node and target_node.id:
                self.meta_state.add_decoration_render(target_node.id)
                node.uses_decoration_render = True
                for child_node in target_node.get_children_nodes():
                    child_node.uses_decoration_render = True

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
            self.active_modal_count += 1

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

        for i, child_node in enumerate(current_node.get_children_nodes()):
            self.init_node_hierarchy(child_node, node_index_path + [i], constraint_nodes, clip_nodes)

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

        if self.meta_state.buttons or self.meta_state.inputs or self.draggable_node:
            full_rect = self.draggable_node.box_model.border_rect \
                if getattr(self.draggable_node, 'box_model', None) \
                else self.root_node.box_model.content_children_rect

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