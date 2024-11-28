from talon.skia.canvas import Canvas as SkiaCanvas
from talon.canvas import Canvas
from talon.screen import Screen
from talon.skia import RoundRect
from talon.types import Rect, Point2d
from talon import cron
from typing import List, Optional, Any
from ..core.cursor import Cursor
from ..interfaces import TreeType, NodeType, MetaStateType, ScrollRegionType
from ..entity_manager import entity_manager
from ..state_manager import state_manager
from ..options import UIOptions
from ..store import store
from ..constants import HIGHLIGHT_COLOR, CLICK_COLOR
from ..utils import generate_hash, get_screen, canvas_from_screen, draw_text_simple
import time

import uuid

# class NodeRefs():
#     def __init__(self):
#         self.buttons = {}
#         self.inputs = {}
#         self.dynamic_text = {}
#         self.highlighted = {}
#         self.scrollable_regions = {}

#     def clear(self):
#         self.buttons.clear()
#         self.inputs.clear()
#         self.dynamic_text.clear()
#         self.highlighted.clear()
#         self.scrollable_regions.clear()

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

    def add_input(self, id, initial_value):
        self._inputs[id] = initial_value

    def add_button(self, id):
        self._buttons.add(id)

    def map_id_to_node(self, id, node):
        self._id_to_node[id] = node

    def add_scroll_region(self, id):
        self._scroll_regions[id] = ScrollRegion(0, 0)

    def set_highlighted(self, id, color = HIGHLIGHT_COLOR):
        if id in self._id_to_node:
            self._highlighted[id] = color

    def set_unhighlighted(self, id):
        if id in self._id_to_node and id in self._highlighted:
            self._highlighted.pop(id)

    def set_input_value(self, id, value):
        if id in self._id_to_node:
            self._inputs[id] = value

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

    def set_text_mutation(self, id, text):
        if id in self._id_to_node:
            self._text_mutations[id] = text

    def use_text_mutation(self, id, initial_text):
        if id not in self._text_mutations:
            self._text_mutations[id] = initial_text
        return self._text_mutations[id]

    def set_style_mutation(self, id, style):
        if id in self._id_to_node:
            self._style_mutations[id] = style

    def clear_nodes(self):
        self._id_to_node.clear()
        entity_manager.synchronize_global_ids()

    def clear(self):
        self._buttons.clear()
        self._highlighted.clear()
        self._id_to_node.clear()
        self._inputs.clear()
        self._scroll_regions.clear()
        self._style_mutations.clear()
        self._text_mutations.clear()
        for job in list(self.unhighlight_jobs.values()):
            if job:
                cron.cancel(job[0])
        self.unhighlight_jobs.clear()
        self.active_button = None
        entity_manager.synchronize_global_ids()

class Tree(TreeType):
    def __init__(self, renderer: callable, hashed_renderer: str):
        self.canvas_base = None
        self.canvas_blockable = []
        self.canvas_decorator = None
        self.canvas_draw = None
        self.canvas_mouse = None
        self.cursor = None
        self.effects = []
        self.hashed_renderer = hashed_renderer
        self.is_blockable_canvas_init = False
        self.is_mounted = False
        self.meta_state = MetaState()
        # self.node_refs = NodeRefs()
        self._renderer = renderer
        self.root_node = None
        self.screen = None
        self.screen_index = None
        self.surfaces = []
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
        self.root_node = self._renderer()
        self.init_screen()

    @with_tree
    def on_draw_base_canvas(self, canvas: SkiaCanvas):
        # self.root_node = self.renderer()
        # self.init_screen()
        start = time.time()
        self.reset_cursor()
        self.init_node_hierarchy(self.root_node)
        self.consume_effects()
        print(f"init_node_hierarchy: {time.time() - start}")
        self.root_node.virtual_render(canvas, self.cursor)
        print(f"virtual_render: {time.time() - start}")
        self.root_node.grow_intrinsic_size(canvas, self.cursor)
        self.root_node.render(canvas, self.cursor)
        print(f"on_draw_base_canvas: {time.time() - start}")

        self.render_decorator_canvas()
        print(f"on_draw_base_canvas + decorator: {time.time() - start}")

    def draw_highlights(self, canvas: SkiaCanvas):
        canvas.paint.style = canvas.paint.Style.FILL
        for id, color in list(self.meta_state.highlighted.items()):
            if id in self.meta_state.id_to_node:
                node = self.meta_state.id_to_node[id]
                box_model = node.box_model
                canvas.paint.color = color or HIGHLIGHT_COLOR

                if hasattr(node.options, 'border_radius'):
                    border_radius = node.options.border_radius
                    canvas.draw_rrect(RoundRect.from_rect(box_model.padding_rect, x=border_radius, y=border_radius))
                else:
                    canvas.draw_rect(box_model.padding_rect)

    def draw_text_mutations(self, canvas: SkiaCanvas):
        for id, text_value in self.meta_state.text_mutations.items():
            if id in self.meta_state.id_to_node:
                node = self.meta_state.id_to_node[id]
                x, y = node.cursor_pre_draw_text
                draw_text_simple(canvas, text_value, node.options, x, y)

    def refresh_decorator_canvas(self):
        if self.canvas_decorator:
            self.canvas_decorator.freeze()

    def highlight(self, id: str, color: str = None):
        self.meta_state.set_highlighted(id, color)
        self.canvas_decorator.freeze()

    def unhighlight(self, id: str):
        if id in self.meta_state.highlighted:
            self.meta_state.set_unhighlighted(id)

            if self.meta_state.unhighlight_jobs.get(id):
                cron.cancel(self.meta_state.unhighlight_jobs[id][0])
                self.meta_state.unhighlight_jobs[id][1]()
                self.meta_state.unhighlight_jobs[id] = None

            self.canvas_decorator.freeze()

    def highlight_briefly(self, id: str, color: str = None, duration: int = 150):
        self.highlight(id, color)
        pending_unhighlight = lambda: self.unhighlight(id)
        self.meta_state.unhighlight_jobs[id] = (cron.after(f"{duration}ms", pending_unhighlight), pending_unhighlight)

    @with_tree
    def on_draw_decorator_canvas(self, canvas: SkiaCanvas):
        start = time.time()
        self.draw_highlights(canvas)
        self.draw_text_mutations(canvas)

        if not self.is_blockable_canvas_init:
            self.init_blockable_canvases()
        self.on_fully_rendered()
        # print(f"on_draw_decorator_canvas: {time.time() - start}")

    @with_tree
    def on_draw_mouse_canvas(self, canvas: SkiaCanvas):
        pass

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

    def render(self, props: dict[str, Any] = None, on_mount: callable = None, on_unmount: callable = None, show_hints: bool = False):
        if self.is_mounted:
            self.meta_state.clear_nodes()
            self.effects.clear()
            # if self.canvas_blockable:
            #     for canvas in self.canvas_blockable:
            #         canvas.unregister("mouse", self.on_mouse)
            #         # canvas.unregister("mouse", self.on_scroll)
            #         canvas.close()
            #     self.is_blockable_canvas_init = False
            self.init_nodes_and_screen()
        if on_mount:
            state_manager.register_effect(self, on_mount, [])
        self.render_base_canvas()

    def hide(self):
        self.destroy()

    def on_fully_rendered(self):
        if not self.is_mounted:
            self.is_mounted = True

            for effect in self.effects:
                effect['callback']()

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
                    self.highlight(button_id, color=HIGHLIGHT_COLOR)
                break

        if not new_hovered_id and prev_hovered_id:
            self.unhighlight(prev_hovered_id)
            state_manager.set_hovered_id(None)

    def on_mousedown(self, gpos):
        hovered_id = state_manager.get_hovered_id()

        if hovered_id in list(self.meta_state.buttons):
            state_manager.set_mousedown_start_id(hovered_id)
            self.highlight(hovered_id, color=CLICK_COLOR)

    def on_mouseup(self, gpos):
        hovered_id = state_manager.get_hovered_id()
        mousedown_start_id = state_manager.get_mousedown_start_id()

        if mousedown_start_id and hovered_id == mousedown_start_id:
            node = self.meta_state.id_to_node[mousedown_start_id]
            self.highlight(mousedown_start_id, color=HIGHLIGHT_COLOR)
            node.on_click()

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
        if self.canvas_base:
            self.canvas_base.unregister("draw", self.on_draw_base_canvas)
            self.canvas_base.close()
            self.canvas_base = None

        if self.canvas_decorator:
            self.canvas_decorator.unregister("draw", self.on_draw_decorator_canvas)
            self.canvas_decorator.close()
            self.canvas_decorator = None

        if self.canvas_mouse:
            self.canvas_mouse.unregister("draw", self.on_draw_mouse_canvas)
            self.canvas_mouse.close()
            self.canvas_mouse = None

        if self.canvas_blockable:
            for canvas in self.canvas_blockable:
                canvas.unregister("mouse", self.on_mouse)
                # canvas.unregister("mouse", self.on_scroll)
                canvas.close()
            self.is_blockable_canvas_init = False

        self.meta_state.clear()
        self.effects.clear()
        self.is_mounted = False
        state_manager.clear_state()

    def init_node_hierarchy(self, current_node: NodeType, depth = 0, constraint_nodes: list[NodeType] = None):
        current_node.tree = self
        current_node.depth = depth

        if constraint_nodes:
            current_node.constraint_nodes = constraint_nodes

        if current_node.options.width is not None or current_node.options.max_width is not None:
            if constraint_nodes is None:
                constraint_nodes = []
            constraint_nodes = constraint_nodes + [current_node]

        if current_node.id:
            self.meta_state.map_id_to_node(current_node.id, current_node)

            if current_node.element_type == 'button':
                self.meta_state.add_button(current_node.id)
            elif current_node.element_type == 'text':
                self.meta_state.use_text_mutation(current_node.id, initial_text=current_node.text)
            # elif current_node.element_type == 'input':
            #     self.meta_state.add_input(current_node.id, initial_value=current_node.value)

        for child_node in current_node.children_nodes:
            self.init_node_hierarchy(child_node, depth + 1, constraint_nodes)

        entity_manager.synchronize_global_ids()

    def consume_effects(self):
        for effect in list(store.staged_effects):
            if effect['tree'] == self:
                self.effects.append(effect)
                store.staged_effects.remove(effect)

    def init_blockable_canvases(self):
        """
        If we have at least one button or input, then we will consider the whole content area as blockable.
        If we have an inputs, then everything should be blockable except for those inputs.
        """
        start = time.time()
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
                for input in list(self.meta_state.inputs.values()):
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
                canvas.focused = True
                # but we can't be recreating canvas every time otherwise
                # this is even more expensive switching back and forth
                # between "applications"

        self.is_blockable_canvas_init = True
        # print(f"init_blockable_canvases: {time.time() - start}")

def render_ui(renderer: callable, props: dict[str, Any] = None, on_mount: callable = None, on_unmount: callable = None, show_hints: bool = False):
    hash = generate_hash(renderer)
    tree = None
    for t in entity_manager.get_all_trees():
        if t.hashed_renderer == hash:
            tree = t
            break

    if not tree:
        tree = Tree(renderer, hash)
        entity_manager.add_tree(tree)

    start = time.time()
    tree.render(props, on_mount, on_unmount, show_hints)