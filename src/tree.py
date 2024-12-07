from talon.skia.canvas import Canvas as SkiaCanvas
from talon.canvas import Canvas
from talon.skia import RoundRect
from talon.types import Rect
from talon import cron, settings
from typing import Any
from .constants import ELEMENT_ENUM_TYPE
from .cursor import Cursor
from .interfaces import (
    TreeType,
    NodeType,
    MetaStateInput,
    MetaStateType,
    Effect,
    ClickEvent,
    ScrollRegionType,
    RenderCauseStateType
)
from .entity_manager import entity_manager
from .hints import draw_hint, get_hint_generator, hint_tag_enable, hint_clear_state
from .state_manager import state_manager
from .store import store
from .utils import get_screen, draw_text_simple, get_active_color_from_highlight_color
import inspect
import uuid

class ScrollRegion(ScrollRegionType):
    def __init__(self, scroll_y: int, scroll_x: int):
        self.scroll_y = scroll_y
        self.scroll_x = scroll_x

class MetaState(MetaStateType):
    def __init__(self):
        self._buttons = set()
        self._highlighted = {}
        self._id_to_node = {}
        self._inputs = {}
        self._scroll_regions = {}
        self._style_mutations = {}
        self._text_mutations = {}
        self.ref_property_overrides = {}
        self.focused_id = None
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
    def style_mutations(self):
        return self._style_mutations

    @property
    def text_mutations(self):
        return self._text_mutations

    def add_input(self, id, input, initial_value = None):
        self._inputs[id] = MetaStateInput(
            value=initial_value,
            input=input,
            previous_value=None
        )

    def add_button(self, id):
        self._buttons.add(id)

    def map_id_to_node(self, id, node):
        self._id_to_node[id] = node

    def add_scroll_region(self, id):
        self._scroll_regions[id] = ScrollRegion(0, 0)

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
                input_data.input.hide()

        for job in list(self.unhighlight_jobs.values()):
            if job:
                cron.cancel(job[0])

        self._buttons.clear()
        self._highlighted.clear()
        self._id_to_node.clear()
        self._inputs.clear()
        self._scroll_regions.clear()
        self._style_mutations.clear()
        self._text_mutations.clear()
        self.unhighlight_jobs.clear()
        self.focused_id = None
        self.ref_property_overrides.clear()
        entity_manager.synchronize_global_ids()

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
        self.processing_states = []
        self.guid = uuid.uuid4().hex
        self.hashed_renderer = hashed_renderer
        self.is_blockable_canvas_init = False
        self.is_mounted = False
        self.meta_state = MetaState()
        self.props = props
        self.render_cause = RenderCauseState()
        self._renderer = renderer
        self.render_version = 2
        self.render_debounce_job = None
        self.redistribute_box_model = False
        self.root_node = None
        self.screen = None
        self.screen_index = None
        self.show_hints = False
        self.surfaces = []
        state_manager.init_states(initial_state)
        self.init_nodes_and_screen()

    def with_tree(func):
        def wrapper(self, *args, **kwargs):
            state_manager.set_processing_tree(self)
            result = func(self, *args, **kwargs)
            state_manager.set_processing_tree(None)
            return result
        return wrapper

    def reset_cursor(self):
        if self.cursor is None:
            self.cursor = Cursor(self.screen)
        else:
            self.cursor.reset()

    def init_screen(self):
        if self.root_node.element_type != "screen":
            raise Exception("Root node must be a screen element")

        if not self.screen or self.screen_index != self.root_node.screen_index:
            self.screen_index = self.root_node.screen_index
            self.screen = get_screen(self.screen_index)

    @with_tree
    def init_nodes_and_screen(self):
        if len(inspect.signature(self._renderer).parameters) > 0:
            if not isinstance(self.props, dict):
                print(f"props: {self.props}")
                raise Exception("props passed to actions.user.ui_elements_show should be a dictionary, and the receiving function should accept a single argument `props`")
            self.root_node = self._renderer(self.props or {})
        else:
            self.root_node = self._renderer()

        if not isinstance(self.root_node, NodeType):
            raise Exception("actions.user.ui_elements_show was passed a function that didn't return any elements. Be sure to return an element tree composed of `screen`, `div`, `text`, etc.")

        self.init_screen()

    @with_tree
    def on_draw_base_canvas(self, canvas: SkiaCanvas):
        self.reset_cursor()
        self.init_node_hierarchy(self.root_node)
        self.consume_effects()
        self.redistribute_box_model = False
        self.root_node.virtual_render(canvas, self.cursor)
        self.root_node.grow_intrinsic_size(canvas, self.cursor)
        # Do we need another pass here for redistribution?
        # self.redistribute_box_model = True
        # self.root_node.virtual_render(canvas, self.cursor)
        # self.root_node.grow_intrinsic_size(canvas, self.cursor)
        self.root_node.render(canvas, self.cursor)
        self.show_inputs()
        self.render_decorator_canvas()

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
        for id, text_value in self.meta_state.text_mutations.items():
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

    def render_text_mutation(self):
        if self.canvas_decorator:
            self.render_cause.set_text_change()
            self.canvas_decorator.freeze()

    def refresh_decorator_canvas(self):
        if self.canvas_decorator:
            self.canvas_decorator.freeze()

    def focus_input(self, id: str):
        focused_node = self.meta_state.id_to_node.get(id)
        if focused_node and focused_node.input:
            # workaround for focus
            focused_node.input.hide()
            focused_node.input.show()

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
                if id == self.meta_state.focused_id:
                    focused_input = input_data.input
                    continue
                if input_data.input:
                    input_data.input.show()

            # do this last so that focused input is on top
            if focused_input:
                focused_input.show()


    @with_tree
    def on_draw_decorator_canvas(self, canvas: SkiaCanvas):
        # start = time.time()
        # if self.render_cause.is_highlight_change():
        self.draw_highlights(canvas)
        # self.render_cause.clear()
        # return

        # if self.render_cause.is_text_change():
        self.draw_text_mutations(canvas)
        # self.render_cause.clear()
        # return

        if self.show_hints:
            self.draw_hints(canvas)

        if not self.is_blockable_canvas_init:
            self.init_blockable_canvases()

        self.on_fully_rendered()

    def render_decorator_canvas(self):
        if not self.canvas_decorator:
            self.canvas_decorator = Canvas.from_screen(self.screen)
            self.canvas_decorator.register("draw", self.on_draw_decorator_canvas)

        self.canvas_decorator.freeze()

    def render_base_canvas(self):
        if not self.canvas_base:
            self.canvas_base = Canvas.from_screen(self.screen)
            self.canvas_base.register("draw", self.on_draw_base_canvas)

        self.canvas_base.freeze()

    def render(self, props: dict[str, Any] = {}, on_mount: callable = None, on_unmount: callable = None, show_hints: bool = None):
        self.props = self.props or props
        self.render_cause.state_change()

        if self.is_mounted:
            self.on_state_change_effect_cleanups()
            self.meta_state.clear_nodes()
            if self.canvas_blockable:
                for canvas in self.canvas_blockable:
                    canvas.unregister("mouse", self.on_mouse)
                    # canvas.unregister("mouse", self.on_scroll)
                    canvas.close()
                self.is_blockable_canvas_init = False
            self.init_nodes_and_screen()

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
        if self.is_mounted:
            if self.render_cause.is_state_change():
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

    def on_mousedown(self, gpos):
        hovered_id = state_manager.get_hovered_id()

        if hovered_id in list(self.meta_state.buttons):
            node = self.meta_state.id_to_node[hovered_id]
            state_manager.set_mousedown_start_id(hovered_id)
            active_color = get_active_color_from_highlight_color(node.properties.highlight_color)
            self.highlight(hovered_id, color=active_color)

    def on_mouseup(self, gpos):
        hovered_id = state_manager.get_hovered_id()
        mousedown_start_id = state_manager.get_mousedown_start_id()

        if mousedown_start_id and hovered_id == mousedown_start_id:
            node = self.meta_state.id_to_node[mousedown_start_id]
            self.highlight(mousedown_start_id, color=node.properties.highlight_color)

            sig = inspect.signature(node.on_click)
            if len(sig.parameters) == 0:
                node.on_click()
            else:
                node.on_click(ClickEvent(id=mousedown_start_id))

        state_manager.set_mousedown_start_id(None)

    def on_mouse(self, e):
        found_clickable = False
        if e.event == "mousemove":
            self.on_hover(e.gpos)
        elif e.event == "mousedown":
            found_clickable = self.on_mousedown(e.gpos)
        elif e.event == "mouseup":
            self.on_mouseup(e.gpos)

        # if not found_clickable and self.window:
        #     self.on_mouse_window(e)

    def destroy(self):
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
            self.canvas_decorator.unregister("draw", self.on_draw_decorator_canvas)
            self.canvas_decorator.close()
            self.canvas_decorator = None

        if self.canvas_blockable:
            for canvas in self.canvas_blockable:
                canvas.unregister("mouse", self.on_mouse)
                # canvas.unregister("mouse", self.on_scroll)
                canvas.close()
            self.is_blockable_canvas_init = False

        self.meta_state.clear()
        self.effects.clear()
        self.processing_states.clear()
        self.is_mounted = False
        hint_clear_state()
        state_manager.clear_state()

    def init_node_hierarchy(
            self,
            current_node: NodeType,
            index_path = [], # [1, 2, 0]
            constraint_nodes: list[NodeType] = None
        ):
        current_node.tree = self
        current_node.depth = len(index_path)

        if current_node.interactive and not current_node.id:
            index_path_str = "-".join(map(str, index_path)) # "1-2-0"
            current_node.id = self.guid + index_path_str

        if current_node.id:
            self.meta_state.map_id_to_node(current_node.id, current_node)

            if overrides := self.meta_state.get_ref_property_overrides(current_node.id):
                current_node.properties.update_overrides(overrides)

            if current_node.element_type == ELEMENT_ENUM_TYPE["button"]:
                self.meta_state.add_button(current_node.id)
            elif current_node.element_type == ELEMENT_ENUM_TYPE["text"]:
                self.meta_state.use_text_mutation(current_node.id, initial_text=current_node.text)
            elif current_node.element_type == ELEMENT_ENUM_TYPE["input_text"]:
                if not self.meta_state.focused_id:
                    self.meta_state.focused_id = current_node.id
                # no need to add input to meta state, it is managed on render

        if constraint_nodes:
            current_node.constraint_nodes = constraint_nodes

        if current_node.properties.width is not None or current_node.properties.max_width is not None:
            if constraint_nodes is None:
                constraint_nodes = []
            constraint_nodes = constraint_nodes + [current_node]

        if current_node.element_type == ELEMENT_ENUM_TYPE["screen"] and current_node.deprecated_ui:
            self.render_version = 1

        for i, child_node in enumerate(current_node.children_nodes):
            self.init_node_hierarchy(child_node, index_path + [i], constraint_nodes)

        entity_manager.synchronize_global_ids()

    def consume_effects(self):
        for effect in list(store.staged_effects):
            if effect.tree == self or effect.tree is None:
                self.effects.append(effect)
                store.staged_effects.remove(effect)

    def init_blockable_canvases(self):
        """
        If we have at least one button or input, then we will consider the whole content area as blockable.
        If we have an inputs, then everything should be blockable except for those inputs.
        """
        # start = time.time()
        if not self.root_node or not self.root_node.box_model:
            return

        if self.meta_state.buttons or self.meta_state.inputs:
            full_rect = self.root_node.box_model.content_children_rect
            # if self.window and self.window.offset:
            #     full_rect.x += self.window.offset.x
            #     full_rect.y += self.window.offset.y

            #     for input in list(self.meta_state.inputs.values()):
            #         input.rect.x += self.window.offset.x
            #         input.rect.y += self.window.offset.y

            if self.meta_state.inputs:
                bottom_rect = None
                for input_data in list(self.meta_state.inputs.values()):
                    if not input_data.input:
                        continue
                    input = input_data.input
                    current_rect = bottom_rect or full_rect

                    top_rect = Rect(current_rect.x, current_rect.y, current_rect.width, input.rect.y - current_rect.y)
                    self.canvas_blockable.append(Canvas.from_rect(top_rect))

                    left_rect = Rect(current_rect.x, input.rect.y, input.rect.x - current_rect.x, input.rect.height)
                    self.canvas_blockable.append(Canvas.from_rect(left_rect))

                    right_rect = Rect(input.rect.x + input.rect.width, input.rect.y, current_rect.x + current_rect.width - input.rect.x - input.rect.width, input.rect.height)
                    self.canvas_blockable.append(Canvas.from_rect(right_rect))

                    bottom_rect = Rect(current_rect.x, input.rect.y + input.rect.height, current_rect.width, current_rect.y + current_rect.height - input.rect.y - input.rect.height)
                self.canvas_blockable.append(Canvas.from_rect(bottom_rect))
            else:
                self.canvas_blockable = [Canvas.from_rect(full_rect)]

            for canvas in self.canvas_blockable:
                canvas.blocks_mouse = True
                canvas.register("mouse", self.on_mouse)
                # canvas.register("scroll", self.on_scroll)
                canvas.freeze()
                # canvas.focused = True
                # but we can't be recreating canvas every time otherwise
                # this is even more expensive switching back and forth
                # between "applications"

        self.is_blockable_canvas_init = True
        # print(f"init_blockable_canvases: {time.time() - start}")

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

    tree.render(props, on_mount, on_unmount, show_hints)