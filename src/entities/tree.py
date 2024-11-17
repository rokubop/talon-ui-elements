from talon.skia.canvas import Canvas as SkiaCanvas
from talon.canvas import Canvas
from talon.screen import Screen
from typing import List, Optional
from ..core.cursor import Cursor
from ..interfaces import TreeType, TreeManagerType, NodeType
from ..managers import state_manager, entity_manager
from ..options import UIOptions
from ..store import store
from ..utils import generate_hash, get_screen, canvas_from_screen, draw_text_simple

import uuid

class NodeRefs():
    def __init__(self):
        self.components = []
        self.buttons = []
        self.inputs = []
        self.dynamic_text = []
        self.highlighted = []
        self.scrollable_regions = []

    def clear(self):
        self.components.clear()
        self.buttons.clear()
        self.inputs.clear()
        self.dynamic_text.clear()
        self.highlighted.clear()
        self.scrollable_regions.clear()

class Tree(TreeType):
    def __init__(self, update_tree: callable, hashed_update_tree: str):
        self.canvas_base = None
        self.canvas_decorator = None
        self.canvas_mouse = None
        self.canvas_draw = None
        self.cursor = None
        self.effects = []
        self.surfaces = []
        self.update_tree = update_tree
        self.hashed_update_tree = hashed_update_tree
        self.node_refs = NodeRefs()
        self.is_mounted = False
        self.screen_index = None
        self.screen = None
        self.cursor = None
        self.root_node = None
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
        self.root_node = self.update_tree()
        self.init_screen()

    @with_tree
    def on_draw_base_canvas(self, canvas: SkiaCanvas):
        # self.root_node = self.update_tree()
        # self.init_screen()
        self.reset_cursor()
        self.init_node_hierarchy(self.root_node)
        self.consume_effects()

        self.root_node.virtual_render(canvas, self.cursor)
        self.root_node.render(canvas, self.cursor)

        self.render_decorator_canvas()

    @with_tree
    def on_draw_decorator_canvas(self, canvas: SkiaCanvas):
        self.on_fully_rendered()

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

    def render(self):
        self.render_base_canvas()

    def hide(self):
        self.destroy()

    def on_fully_rendered(self):
        if not self.is_mounted:
            self.is_mounted = True

            for effect in self.effects:
                effect['callback']()

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

        self.node_refs.clear()
        self.effects.clear()
        self.is_mounted = False

    def init_node_hierarchy(self, current_node: NodeType, depth = 0):
        current_node.tree = self
        current_node.depth = depth

        for child_node in current_node.children_nodes:
            if child_node.element_type == 'button':
                self.node_store.buttons.append(child_node)
            elif child_node.element_type == 'text' and child_node.id:
                self.node_store.dynamic_text.append(child_node)

            self.init_node_hierarchy(child_node, depth + 1)

    def consume_effects(self):
        for effect in list(store.staged_effects):
            if effect['tree'] == self:
                self.effects.append(effect)
                store.staged_effects.remove(effect)

def render_tree(update_tree: callable):
    hash = generate_hash(update_tree)
    tree = None
    for t in entity_manager.get_all_trees():
        if t.hashed_update_tree == hash:
            tree = t
            break

    if not tree:
        tree = Tree(update_tree, hash)
        entity_manager.add_tree(tree)

    tree.render()