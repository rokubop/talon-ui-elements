from talon.skia.canvas import Canvas as SkiaCanvas
from talon.canvas import Canvas, MouseEvent
from talon.skia import RoundRect
from talon.types import Rect, Point2d
from talon import cron, settings
from typing import Any
from ..constants import ELEMENT_ENUM_TYPE, DRAG_INIT_THRESHOLD
from ..canvas_wrapper import CanvasWeakRef
from ..cursor import Cursor
from ..interfaces import (
    TreeType,
    NodeType,
    MetaStateInput,
    MetaStateType,
    Effect,
    ClickEvent,
    RenderCauseStateType,
    ScrollRegionType,
    ScrollableType,
)
from ..entity_manager import entity_manager
from ..hints import draw_hint, get_hint_generator, hint_tag_enable, hint_clear_state
from ..state_manager import state_manager
from ..store import store
from ..utils import draw_text_simple, get_active_color_from_highlight_color, get_combined_screens_rect
from ..render_manager import RenderManager, RenderCause
import inspect
import uuid
import threading

scroll_throttle_job = None
scroll_throttle_time = "30ms"

def scroll_throttle_clear():
    global scroll_throttle_job
    if scroll_throttle_job:
        cron.cancel(scroll_throttle_job)
    scroll_throttle_job = None

class ScrollRegion(ScrollRegionType):
    def __init__(self, scroll_y: int, scroll_x: int):
        self.scroll_y = scroll_y
        self.scroll_x = scroll_x

class Scrollable(ScrollableType):
    def __init__(self, id):
        self.id = id
        self.offset_x = 0
        self.offset_y = 0

class MetaState(MetaStateType):
    def __init__(self):
        self._buttons = set()
        self._highlighted = {}
        self._id_to_node = {}
        self._inputs = {}
        self._scroll_regions = {}
        self._scrollable = {}
        self._style_mutations = {}
        self._text_mutations = {}
        self.ref_property_overrides = {}
        self.unhighlight_jobs = {}

    @property
    def buttons(self):
        return self._buttons

    @property
    def highlighted(self):
        return self._highlighted

    @property
    def id_to_node(self):
        return self._id_to_node

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
    def style_mutations(self):
        return self._style_mutations

    @property
    def text_mutations(self):
        return self._text_mutations

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

    def map_id_to_node(self, id, node):
        self._id_to_node[id] = node

    def add_scroll_region(self, id):
        self._scroll_regions[id] = ScrollRegion(0, 0)

    def add_scrollable(self, id):
        if id not in self._scrollable:
            self._scrollable[id] = Scrollable(id)

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
        entity_manager.synchronize_global_ids()

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
        self._highlighted.clear()
        self._inputs.clear()
        self._scroll_regions.clear()
        self._scrollable.clear()
        self._style_mutations.clear()
        self._text_mutations.clear()
        self.unhighlight_jobs.clear()
        self.ref_property_overrides.clear()
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
    def __init__(
            self,
            renderer: callable,
            hashed_renderer: str,
            props: dict[str, Any] = {},
            initial_state = dict[str, Any]
        ):
        self.canvas_base = None
        self.canvas_blockable = []
        self.canvas_decorator = None
        self.cursor = None
        self.effects = []
        self.draggable_node = False
        self.draggable_node_delta_pos = None
        self.drag_handle_node = None
        self.draw_busy = None
        self.processing_states = []
        self.guid = uuid.uuid4().hex
        self.hashed_renderer = hashed_renderer
        self.interactive_node_list = []
        self.is_key_controls_init = False
        self.is_blockable_canvas_init = False
        self.is_mounted = False
        self.last_blockable_rects = []
        self.lock = threading.Lock()
        self.meta_state = MetaState()
        self.props = props
        self.render_manager = RenderManager(self)
        self.render_cause = RenderCauseState()
        self._renderer = renderer
        self.render_version = 2
        self.render_debounce_job = None
        self.redistribute_box_model = False
        self.root_node = None
        self.show_hints = False
        self.scroll_amount_per_tick = settings.get("user.ui_elements_scroll_speed")
        self.surfaces = []
        state_manager.init_states(initial_state)
        self.init_nodes_and_boundary()
        state_manager.increment_ref_count_trees()

    def __del__(self):
        state_manager.decrement_ref_count_trees()

    def reset_cursor(self):
        if self.cursor is None:
            self.cursor = Cursor(self.root_node.boundary_rect)
        else:
            self.cursor.reset()

    def validate_root_node(self):
        if self.root_node.element_type not in ["screen", "active_window"]:
            raise Exception("Root node must be a screen or active_window element")

    def init_nodes_and_boundary(self):
        state_manager.set_processing_tree(self)
        if len(inspect.signature(self._renderer).parameters) > 0:
            if self.props and not isinstance(self.props, dict):
                print(f"props: {self.props}")
                raise Exception("props passed to actions.user.ui_elements_show should be a dictionary, and the receiving function should accept a single argument `props`")
            self.root_node = self._renderer(self.props or {})
        else:
            self.root_node = self._renderer()

        if not isinstance(self.root_node, NodeType):
            raise Exception("actions.user.ui_elements_show was passed a function that didn't return any elements. Be sure to return an element tree composed of `screen`, `div`, `text`, etc.")

        self.validate_root_node()
        state_manager.set_processing_tree(None)

    def on_draw_base_canvas(self, canvas: SkiaCanvas):
        if not self.render_manager.is_destroying:
            state_manager.set_processing_tree(self)
            self.reset_cursor()
            self.init_node_hierarchy(self.root_node)
            self.consume_effects()

            self.root_node.v2_measure_intrinsic_size(canvas)
            self.root_node.v2_grow_size(canvas, self.cursor)
            self.root_node.v2_constrain_size(canvas, self.cursor)
            self.root_node.v2_layout(canvas, self.cursor)
            self.root_node.v2_render(canvas, self.cursor)

            self.root_node.virtual_render(canvas, self.cursor)
            self.root_node.grow_intrinsic_size(canvas, self.cursor)
            self.root_node.render(canvas, self.cursor)
            self.show_inputs()
            self.render_decorator_canvas()
            state_manager.set_processing_tree(None)

    def draw_highlights(self, canvas: SkiaCanvas):
        canvas.paint.style = canvas.paint.Style.FILL
        for id, color in list(self.meta_state.highlighted.items()):
            if id in self.meta_state.id_to_node:
                node = self.meta_state.id_to_node[id]
                box_model = node.box_model
                canvas.paint.color = color or node.properties.highlight_color

                if hasattr(node.properties, 'border_radius'):
                    border_radius = node.properties.border_radius
                    canvas.draw_rrect(RoundRect.from_rect(box_model.padding_rect, x=border_radius, y=border_radius))
                else:
                    canvas.draw_rect(box_model.padding_rect)

    def draw_text_mutations(self, canvas: SkiaCanvas):
        for id, text_value in list(self.meta_state.text_mutations.items()):
            if id in self.meta_state.id_to_node:
                node = self.meta_state.id_to_node[id]
                x, y = node.cursor_pre_draw_text
                draw_text_simple(canvas, text_value, node.properties, x, y)

    def draw_hints(self, canvas: SkiaCanvas):
        if self.meta_state.inputs or self.meta_state.buttons:
            hint_tag_enable()
            hint_generator = get_hint_generator()
            for node in list(self.meta_state.id_to_node.values()):
                if node.element_type in ["button", "input_text"]:
                    draw_hint(canvas, node, hint_generator(node))

    # def render_text_mutation(self):
    #     if self.canvas_decorator:
    #         self.render_cause.set_text_change()
    #         self.canvas_decorator.freeze()

    def refresh_decorator_canvas(self):
        if self.canvas_decorator:
            self.canvas_decorator.freeze()

    def highlight(self, id: str, color: str = None):
        if id in self.meta_state.highlighted:
            return

        self.render_cause.highlight_change()
        self.meta_state.set_highlighted(id, color)
        self.canvas_decorator.freeze()

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

    def draw_focus_outline(self, canvas: SkiaCanvas):
        node = state_manager.get_focused_node()
        if node and node.tree == self:
            border_rect = node.box_model.border_rect
            stroke_width = node.properties.focus_outline_width
            focus_outline_rect = Rect(
                border_rect.x - stroke_width,
                border_rect.y - stroke_width,
                border_rect.width + stroke_width * 2,
                border_rect.height + stroke_width * 2
            )

            get_clip_rect = node.box_model.constraints["get_clip_rect"]
            clip_rect = get_clip_rect() if get_clip_rect else None
            apply_clip = clip_rect and \
                (clip_rect.top > node.box_model.padding_rect.top or \
                clip_rect.left > node.box_model.padding_rect.left or \
                clip_rect.bot < node.box_model.padding_rect.bot or \
                clip_rect.right < node.box_model.padding_rect.right)

            if apply_clip:
                canvas.save()
                canvas.clip_rect(clip_rect)

            canvas.paint.style = canvas.paint.Style.STROKE
            canvas.paint.color = node.properties.focus_outline_color
            canvas.paint.stroke_width = stroke_width

            if node.properties.border_radius:
                border_radius = node.properties.border_radius
                canvas.draw_rrect(RoundRect.from_rect(focus_outline_rect, x=border_radius, y=border_radius))
            else:
                canvas.draw_rect(focus_outline_rect)

            if apply_clip:
                canvas.restore()

    def init_key_controls(self):
        if not self.is_key_controls_init and self.canvas_decorator:
            self.is_key_controls_init = True
            self.canvas_decorator.register("key", self.on_key)

    def on_draw_decorator_canvas(self, canvas: SkiaCanvas):
        if not self.render_manager.is_destroying:
            state_manager.set_processing_tree(self)
            self.draw_highlights(canvas)
            self.draw_text_mutations(canvas)
            self.draw_focus_outline(canvas)
            if self.show_hints:
                self.draw_hints(canvas)
            self.init_key_controls()
            self.draw_blockable_canvases()
            # canvas.paint.style = canvas.paint.Style.STROKE
            # canvas.paint.color = "red"
            # canvas.draw_rect(Rect(510.0, 290.0, 900, 500))
            self.on_fully_rendered()
            state_manager.set_processing_tree(None)
            self.render_manager.finish_current_render()

    def _is_draggable_ui(self):
        # Just check 1 level deep
        return any([node.properties.draggable for node in self.root_node.children_nodes])

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
            rect.height - 0.001
        )
        return CanvasWeakRef(Canvas.from_rect(safe_rect))

    def render_decorator_canvas(self):
        if not self.canvas_decorator:
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
                self.init_nodes_and_boundary()

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
        for state in self.processing_states:
            for effect in self.effects:
                if state in effect.dependencies:
                    effect.callback()

    def on_state_change_effect_cleanups(self):
        for state in self.processing_states:
            for effect in reversed(self.effects):
                if state in effect.dependencies:
                    if effect.cleanup:
                        effect.cleanup()

    def on_fully_rendered(self):
        if not self.render_manager.is_destroying:
            if self.is_mounted:
                if self.render_manager.render_cause == RenderCause.STATE_CHANGE:
                    self.on_state_change_effect_callbacks()
            else:
                self.is_mounted = True

                for effect in self.effects:
                    cleanup = effect.callback()
                    if cleanup and not effect.cleanup:
                        effect.cleanup = cleanup

                state_manager.deprecated_event_fire_on_mount(self)

            self.processing_states.clear()
            self.render_cause.clear()

    def on_hover(self, gpos):
        new_hovered_id = None
        prev_hovered_id = state_manager.get_hovered_id()
        for button_id in list(self.meta_state.buttons):
            node = self.meta_state.id_to_node.get(button_id, None)
            if node.is_fully_clipped_by_scroll():
                continue
            if node and node.box_model.padding_rect.contains(gpos):
                new_hovered_id = button_id
                if new_hovered_id != prev_hovered_id:
                    state_manager.set_hovered_id(button_id)
                    self.unhighlight(prev_hovered_id)
                    self.highlight(button_id, color=node.properties.highlight_color)
                break

        if not new_hovered_id and prev_hovered_id:
            self.unhighlight(prev_hovered_id)
            state_manager.set_hovered_id(None)

    def draw_busy_disable(self):
        if self.draw_busy:
            cron.cancel(self.draw_busy)
        self.draw_busy = None
        self.render_cause.clear()

    def refresh_dragging_canvas(self):
        if not self.draw_busy:
            self.render_cause.set_is_dragging()
            self.canvas_base.freeze()
            self.draw_busy = cron.after("16ms", self.draw_busy_disable)

    def get_mouse_hovered_input_id(self, gpos):
        for id, input_data in list(self.meta_state.inputs.items()):
            if input_data.input and input_data.input.rect.contains(gpos):
                return id
        return None

    def on_mousemove(self, gpos):
        drag_relative_offset = state_manager.get_drag_relative_offset()
        if drag_relative_offset:
            if not state_manager.is_drag_active():
                drag_start_pos = state_manager.get_mousedown_start_pos()
                if abs(gpos.x - drag_start_pos.x) > DRAG_INIT_THRESHOLD or abs(gpos.y - drag_start_pos.y) > DRAG_INIT_THRESHOLD:
                    state_manager.set_drag_active(True)

            if state_manager.is_drag_active():
                x = gpos.x - drag_relative_offset.x
                y = gpos.y - drag_relative_offset.y
                self.draggable_node_delta_pos = Point2d(x, y)

        if state_manager.get_mousedown_start_pos():
            self.refresh_dragging_canvas()

    def on_mousedown(self, gpos):
        hovered_id = state_manager.get_hovered_id()

        if self.draggable_node and self.drag_handle_node:
            draggable_rect = self.draggable_node.box_model.margin_rect
            drag_handle_rect = self.drag_handle_node.box_model.border_rect
            if drag_handle_rect.contains(gpos):
                state_manager.set_mousedown_start_pos(gpos)
                relative_offset = Point2d(gpos.x - draggable_rect.x, gpos.y - draggable_rect.y)
                state_manager.set_drag_relative_offset(relative_offset)

        if hovered_id in list(self.meta_state.buttons):
            node = self.meta_state.id_to_node.get(hovered_id)
            if node:
                state_manager.set_mousedown_start_id(hovered_id)
                active_color = get_active_color_from_highlight_color(node.properties.highlight_color)
                state_manager.focus_node(node)
                self.highlight(hovered_id, color=active_color)
                return

        input_id = self.get_mouse_hovered_input_id(gpos)
        if input_id:
            node = self.meta_state.id_to_node.get(input_id)
            if node:
                state_manager.focus_node(node)
                return

        if self.root_node.box_model:
            if self.root_node.box_model.content_children_rect.contains(gpos):
                state_manager.blur()
            else:
                state_manager.blur_all()

    def click_node(self, node: NodeType):
        sig = inspect.signature(node.on_click)
        if len(sig.parameters) == 0:
            node.on_click()
        else:
            node.on_click(ClickEvent(id=node.id))

    def on_mouseup(self, gpos):
        hovered_id = state_manager.get_hovered_id()
        mousedown_start_id = state_manager.get_mousedown_start_id()

        if mousedown_start_id and hovered_id == mousedown_start_id:
            node = self.meta_state.id_to_node.get(mousedown_start_id)
            if node:
                self.highlight(mousedown_start_id, color=node.properties.highlight_color)
                if not state_manager.is_drag_active():
                    self.click_node(node)

        state_manager.set_mousedown_start_id(None)

        if self.draggable_node and self.drag_handle_node:
            state_manager.set_drag_relative_offset(None)
            state_manager.set_mousedown_start_pos(None)
            state_manager.set_drag_active(False)

            cron.after("17ms", self.render_manager.render_drag_end)

    def on_mouse(self, e: MouseEvent):
        # print("on_mouse", e)
        if not self.render_manager.is_destroying:
            if e.event == "mousemove":
                self.on_mousemove(e.gpos)
                self.on_hover(e.gpos)
            elif e.event == "mousedown":
                self.on_mousedown(e.gpos)
            elif e.event == "mouseup":
                self.on_mouseup(e.gpos)

    def on_scroll_tick(self, e):
        if not self.render_manager.is_destroying:
            smallest_node = None
            if self.meta_state.scrollable:
                for id, data in list(self.meta_state.scrollable.items()):
                    node = self.meta_state.id_to_node.get(id)
                    if getattr(node, 'box_model', None) and node.box_model.scroll_box_rect.contains(e.gpos):
                        smallest_node = node if not smallest_node or node.box_model.scroll_box_rect.height < smallest_node.box_model.scroll_box_rect.height else smallest_node

                if smallest_node:
                    offset_y = e.degrees.y
                    if offset_y > 0:
                        offset_y = -self.scroll_amount_per_tick
                    elif offset_y < 0:
                        offset_y = self.scroll_amount_per_tick

                    max_height = smallest_node.box_model.intrinsic_padding_rect.height
                    view_height = smallest_node.box_model.scroll_box_rect.height

                    max_top_scroll_y = 0
                    max_bottom_scroll_y = max_height - view_height

                    new_offset_y = self.meta_state.scrollable[smallest_node.id].offset_y + offset_y

                    if new_offset_y < max_top_scroll_y:
                        new_offset_y = max_top_scroll_y
                    elif new_offset_y > max_bottom_scroll_y:
                        new_offset_y = max_bottom_scroll_y

                    self.meta_state.scrollable[smallest_node.id].offset_y = new_offset_y
                    self.canvas_base.freeze()

    def on_scroll(self, e):
        global scroll_throttle_job
        if not scroll_throttle_job:
            self.on_scroll_tick(e)
            scroll_throttle_job = cron.after(scroll_throttle_time, scroll_throttle_clear)

    def destroy_blockable_canvas(self):
        if self.canvas_blockable:
            for canvas in self.canvas_blockable:
                canvas.unregister("mouse", self.on_mouse)
                canvas.unregister("scroll", self.on_scroll)
                canvas.close()
            self.is_blockable_canvas_init = False
            self.last_blockable_rects.clear()
            self.canvas_blockable.clear()

    def destroy(self):
        global scroll_throttle_job
        self.render_manager.prepare_destroy()
        for effect in reversed(self.effects):
            if effect.cleanup:
                effect.cleanup()

        state_manager.deprecated_event_fire_on_unmount(self)

        if self.render_debounce_job:
            cron.cancel(self.render_debounce_job)
            self.render_debounce_job = None

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

        self._renderer = None
        self.render_manager.destroy()
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
        self.draw_busy_disable()
        scroll_throttle_job = None
        hint_clear_state()
        self.render_cause.clear()
        state_manager.clear_state()

    def _assign_dragging_node_and_handle(self, node: NodeType):
        if hasattr(node.properties, "draggable") and node.properties.draggable:
            if node.depth > 1 or node.element_type != ELEMENT_ENUM_TYPE["div"]:
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
        if node.properties.is_scrollable():
            requires_id = True

        if requires_id and not node.id:
            node_index_path_str = "-".join(map(str, node_index_path)) # "1-2-0"
            node.id = self.guid + node_index_path_str

    def _use_meta_state(self, node: NodeType):
        if node.id:
            self.meta_state.map_id_to_node(node.id, node)

            if overrides := self.meta_state.get_ref_property_overrides(node.id):
                node.properties.update_overrides(overrides)

            if node.element_type == ELEMENT_ENUM_TYPE["button"]:
                self.meta_state.add_button(node.id)
            elif node.element_type == ELEMENT_ENUM_TYPE["text"]:
                self.meta_state.use_text_mutation(node.id, initial_text=node.text)

            if node.properties.is_scrollable():
                self.meta_state.add_scrollable(node.id)

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

    def _check_deprecated_ui(self, node: NodeType):
        if node.element_type == ELEMENT_ENUM_TYPE["screen"] and node.deprecated_ui:
            self.render_version = 1

    def _apply_justify_content_if_space_evenly(self, node: NodeType):
        if node.properties.justify_content == "space_evenly":
            for child_node in node.children_nodes:
                child_node.properties.flex = 1

    def init_node_hierarchy(
            self,
            current_node: NodeType,
            node_index_path = [], # [1, 2, 0]
            constraint_nodes: list[NodeType] = None
        ):
        current_node.tree = self
        current_node.depth = len(node_index_path)
        current_node.node_index_path = node_index_path

        self._assign_dragging_node_and_handle(current_node)
        self._assign_missing_ids(current_node, node_index_path)
        if not self.is_mounted:
            state_manager.autofocus_node(current_node)
        self._use_meta_state(current_node)
        constraint_nodes = self._apply_constraint_nodes(current_node, constraint_nodes)
        self._check_deprecated_ui(current_node)
        self._apply_justify_content_if_space_evenly(current_node)

        for i, child_node in enumerate(current_node.children_nodes):
            child_node.inherit_cascaded_properties(current_node)
            self.init_node_hierarchy(child_node, node_index_path + [i], constraint_nodes)

        entity_manager.synchronize_global_ids()

    def consume_effects(self):
        for effect in list(store.staged_effects):
            if effect.tree == self or effect.tree is None:
                self.effects.append(effect)
                store.staged_effects.remove(effect)

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

    def move_blockable_canvas_rects(self, blockable_rects):
        if blockable_rects and len(blockable_rects) == len(self.canvas_blockable):
            for i, rect in enumerate(blockable_rects):
                self.canvas_blockable[i].move(rect.x, rect.y)
        self.last_blockable_rects.clear()
        self.last_blockable_rects.extend(blockable_rects)

    def should_rerender_blockable_canvas(self):
        return self.render_manager.render_cause == RenderCause.STATE_CHANGE \
            or self.render_cause.is_dragging() \
            or self.render_manager.render_cause == RenderCause.DRAG_END

    def calculate_blockable_rects(self):
        """
        If we have at least one button or input, then we will consider the whole content area as blockable.
        If we have an inputs, then we need to carve holes for those inputs because they are managed separately.
        """
        blockable_rects = []

        if self.meta_state.buttons or self.meta_state.inputs or self.draggable_node:
            full_rect = self.draggable_node.box_model.border_rect \
                if getattr(self.draggable_node, 'box_model', None) \
                else self.root_node.box_model.content_children_rect

            if self.meta_state.inputs:
                bottom_rect = None
                for input_data in list(self.meta_state.inputs.values()):
                    if not input_data.input:
                        continue
                    input = input_data.input
                    current_rect = bottom_rect or full_rect

                    top_rect = Rect(current_rect.x, current_rect.y, current_rect.width, input.rect.y - current_rect.y)
                    blockable_rects.append(top_rect)

                    left_rect = Rect(current_rect.x, input.rect.y, input.rect.x - current_rect.x, input.rect.height)
                    blockable_rects.append(left_rect)

                    right_rect = Rect(input.rect.x + input.rect.width, input.rect.y, current_rect.x + current_rect.width - input.rect.x - input.rect.width, input.rect.height)
                    blockable_rects.append(right_rect)

                    bottom_rect = Rect(current_rect.x, input.rect.y + input.rect.height, current_rect.width, current_rect.y + current_rect.height - input.rect.y - input.rect.height)
                blockable_rects.append(bottom_rect)
            else:
                blockable_rects.append(full_rect)

        return blockable_rects

    def draw_blockable_canvases(self):
        is_rerender = False

        if self.is_blockable_canvas_init:
            if self.should_rerender_blockable_canvas():
                # print(">>> should_rerender_blockable_canvas")
                is_rerender = True
            else:
                return

        if not self.root_node or not self.root_node.box_model:
            return

        blockable_rects = self.calculate_blockable_rects()

        # print("****************************************")
        # print(">>> root_node border_rect", self.root_node.children_nodes[0].box_model.border_rect)
        # print("^^^ blockable_rects", blockable_rects)
        # print("****************************************")
        if is_rerender:
            if self.render_cause.is_dragging():
                self.move_blockable_canvas_rects(blockable_rects)
                return
            dimension_change, position_change = self.have_blockable_rects_changed(blockable_rects)
            if dimension_change:
                # print(">>> dimension_change")
                self.destroy_blockable_canvas()
            elif position_change:
                # print(">>> position_change")
                self.move_blockable_canvas_rects(blockable_rects)
                return

        if not self.is_blockable_canvas_init:
            self.is_blockable_canvas_init = True
            self.last_blockable_rects.clear()
            self.last_blockable_rects.extend(blockable_rects)
            for rect in blockable_rects:
                # print(">>> rect", rect)
                canvas = CanvasWeakRef(Canvas.from_rect(rect))
                self.canvas_blockable.append(canvas)
                canvas.blocks_mouse = True
                canvas.register("mouse", self.on_mouse)
                canvas.register("scroll", self.on_scroll)
                canvas.freeze()

def render_ui(
        renderer: callable,
        props: dict[str, Any] = None,
        on_mount: callable = None,
        on_unmount: callable = None,
        show_hints: bool = None,
        initial_state = dict[str, Any],
    ):

    t = entity_manager.get_tree_with_hash_for_renderer(renderer)
    tree = t["tree"]
    hash = t["hash"]

    if not tree:
        tree = Tree(renderer, hash, props, initial_state)
        entity_manager.add_tree(tree)

    if show_hints is None:
        show_hints = settings.get("user.ui_elements_hints_show")

    tree.render_manager.render_mount(props, on_mount, on_unmount, show_hints)