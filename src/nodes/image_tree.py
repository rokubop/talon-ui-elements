"""A tree that paints into an image instead of onto the screen.

No canvas, and it never joins store.trees. It runs the base pipeline once,
then the parts of the decorator that are content rather than interaction.
"""

import inspect

from talon.skia import Color, Image, Surface
from talon.types import Point2d, Rect

from ..core.state_manager import state_manager
from ..core.store import store
from ..events import StateEvent
from ..interfaces import RenderTransforms
from ..utils import log_trace
from .tree import Tree


def _call(callback):
    try:
        if len(inspect.signature(callback).parameters) == 1:
            return callback(StateEvent())
        return callback()
    except Exception as e:
        print(f"ui_elements: render_image effect failed: {e}")
        log_trace()


class ImageTree(Tree):
    offscreen = True

    def paint(self, effects: bool = False) -> tuple[Image, Rect]:
        """The whole root area on a transparent background, and where that
        area is on screen."""
        bounds = self.root_node.boundary_rect
        width = max(1, int(round(bounds.width)))
        height = max(1, int(round(bounds.height)))
        surface = Surface(width, height)
        canvas = surface.canvas()
        canvas.clear(Color.from_components(0, 0, 0, 0))
        # Nodes lay out in screen coordinates
        canvas.translate(-bounds.x, -bounds.y)
        self.current_base_canvas = canvas

        state_manager.set_processing_tree(self)
        try:
            self.meta_state.clear_nodes()
            self.reset_cursor()
            self.init_node_hierarchy(self.root_node)
            self.transition_manager.end_render()
            self.consume_components()
            if effects:
                self.consume_own_effects()
            self.root_node.v2_measure_intrinsic_size(canvas)
            self.root_node.v2_grow_size()
            self.root_node.v2_constrain_size()
            self.root_node.v2_layout(self.cursor_v2)
            self.nonlayout_flow()
            self.compute_clip_regions_cache()
            self.build_base_render_layers()
            self.commit_base_canvas()

            # Decorator content: highlight_style nodes, an open modal, and
            # text with an id. Hover, focus, hints and scrollbars are left out.
            transforms = RenderTransforms(offset=Point2d(0, 0))
            if self._active_modal_node_ref:
                self.draw_decoration_renders(canvas, transforms, behind_modal=True)
                self.draw_modal_layers(canvas)
            self.draw_decoration_renders(canvas, transforms)
            self.draw_text_mutations(canvas, Point2d(0, 0))
        finally:
            state_manager.set_processing_tree(None)

        return surface.snapshot(), Rect(bounds.x, bounds.y, width, height)

    def consume_own_effects(self):
        """consume_effects also takes effects with no tree, which belong to
        whichever tree shows next."""
        for effect in list(store.staged_effects):
            if effect.tree is self:
                self.effects.append(effect)
                store.staged_effects.remove(effect)

    def run_effects(self):
        """Mount, then unmount straight away. The tree ends with the call."""
        for effect in self.effects:
            if effect.callback:
                cleanup = _call(effect.callback)
                if cleanup and not effect.cleanup:
                    effect.cleanup = cleanup
        for effect in reversed(self.effects):
            if effect.cleanup:
                _call(effect.cleanup)

    def dispose(self):
        """Tree.destroy also clears hover, hints, focus and fonts, which
        belong to the trees on screen."""
        self.transition_manager.destroy()
        self.render_manager.destroy()
        self.meta_state.clear()
        self.effects.clear()
        store.processing_components.pop(self, None)
        if self.root_node:
            self.root_node.destroy()
        self.root_node = None
        self._tree_constructor = None
        self.current_base_canvas = None
        self.draggable_nodes.clear()
        self.drag_handles.clear()
        self.interactive_node_list.clear()
        self.absolute_nodes.clear()
        self.fixed_nodes.clear()
        self.render_list.clear()
        self.render_layers.clear()
        self.modal_render_layers = []
