from talon import Module, Context

mod = Module()
ctx = Context()
ctx_hints_active_browser = Context()

# Import after creating ctx so src/hints can access it
from .src.hints import (
    trigger_hint_click,
    trigger_hint_focus,
    focus_next,
    focus_previous,
    set_hint_context,
    show_scale_notification,
)
from .src.core.entity_manager import entity_manager
from .src.core.state_manager import state_manager
from .src.core.store import store
from .src.constants import ELEMENT_ENUM_TYPE, KEY_DOWN, KEY_UP
from .src.events import WindowCloseEvent

# Pass ctx to src/hints so it can enable/disable tags. Context objects must stay here (not src/)
# because user reloads trigger import chain reloading of src files, but this file isn't imported
# by Python (only loaded by Talon), so Module/Context objects survive and .talon bindings stay intact.
set_hint_context(ctx, ctx_hints_active_browser)

mod.tag("ui_elements_hints_active", desc="tag for ui elements")

ctx_hints_active_browser.matches = """
tag: user.ui_elements_hints_active
and tag: browser
"""

@mod.capture(rule="<user.letter> <user.letter>")
def ui_elements_hint_target(m) -> list[str]:
    return "".join(m.letter_list)

def _has_overflow(node):
    """Check if a scrollable node's content actually exceeds its view."""
    if not node or not getattr(node, 'box_model', None):
        return False
    max_h = node.box_model.content_children_with_padding_size.height
    view_h = node.box_model.padding_size.height
    return max_h > view_h

def _find_scroll_target(tree):
    """Find scrollable region: ancestor of focused/clicked node, or only scrollable region."""
    if not tree.meta_state.scrollable:
        return None, None

    # Try focused node's nearest scrollable ancestor
    if store.focused_id:
        node = tree.meta_state.id_to_node.get(store.focused_id)
        while node:
            if node.id and node.id in tree.meta_state.scrollable and _has_overflow(node):
                data = tree.meta_state.scrollable[node.id]
                return node, data
            node = node.parent_node

    # Try blur_pos (click on non-interactive area) — find smallest containing scrollable
    if store.blur_pos:
        best = None
        best_area = float('inf')
        for id, data in tree.meta_state.scrollable.items():
            node = tree.meta_state.id_to_node.get(id)
            if node and _has_overflow(node) \
                    and node.box_model.padding_rect.contains(store.blur_pos):
                area = node.box_model.padding_rect.width * node.box_model.padding_rect.height
                if area < best_area:
                    best = (node, data)
                    best_area = area
        if best:
            return best

    # Fall back to first scrollable region with overflow
    for id, data in tree.meta_state.scrollable.items():
        node = tree.meta_state.id_to_node.get(id)
        if _has_overflow(node):
            return node, data

    return None, None

def _resolve_focused_scroll_target():
    """Resolve (tree, node) for a scrollable region in the focused tree, or None."""
    tree = store.focused_tree
    if not tree:
        for t in store.trees:
            if t.meta_state.scrollable:
                tree = t
                break
    if not tree:
        return None, None
    node, data = _find_scroll_target(tree)
    if not node or not data:
        return None, None
    return tree, node

def _scroll_focused_tree(direction: int):
    """Scroll the focused tree. direction: 1=up, -1=down."""
    tree, node = _resolve_focused_scroll_target()
    if not node:
        return
    state_manager.smooth_scroll_node(node.id, "y", direction)

@mod.action_class
class Actions:
    def ui_elements_hint_action(action: str, ui_elements_hint_target: str = None):
        """Trigger ui_elements specific hint action"""
        if action == "click":
            if ui_elements_hint_target:
                trigger_hint_click(ui_elements_hint_target)
        elif action == "focus":
            if ui_elements_hint_target:
                trigger_hint_focus(ui_elements_hint_target)

    def ui_elements_key_action(action: str, key_down: bool = None):
        """Trigger ui_elements specific key action"""
        # Route up/down to open select dropdown instead of focus navigation
        if action in ("focus_next", "focus_previous"):
            for tree in store.trees:
                for node in tree.interactive_node_list:
                    if node.element_type == ELEMENT_ENUM_TYPE["select"] and getattr(node, 'is_open', False):
                        if key_down:
                            key = KEY_DOWN if action == "focus_next" else KEY_UP
                            node.on_key(key, True)
                        return

        if action == "focus_next":
            focus_next.execute(key_down)
        elif action == "focus_previous":
            focus_previous.execute(key_down)
        elif action == "close":
            state_manager._smooth_scroll_stop()
            tree = store.focused_tree
            if not tree:
                entity_manager.hide_all_trees()
                return
            if tree.destroying:
                return
            # Route through the window's on_close handler so it follows the
            # same deferred-teardown path as the close button (avoids
            # half-close leaving the base canvas alive while the decorator
            # canvas tears down).
            for wid in list(tree.meta_state.windows):
                node = tree.meta_state.id_to_node.get(wid)
                on_close = getattr(node, "on_close", None) if node else None
                if on_close:
                    on_close(WindowCloseEvent(hide=True))
                    return
            tree.destroy()
            if not store.trees:
                store.clear()

    def ui_elements_scale_increase():
        """Increase UI scale by browser-like increments"""
        new_scale = entity_manager.increase_scale()
        show_scale_notification(new_scale)

    def ui_elements_scale_decrease():
        """Decrease UI scale by browser-like increments"""
        new_scale = entity_manager.decrease_scale()
        show_scale_notification(new_scale)

    def ui_elements_scale_reset():
        """Reset UI scale to default (1.0)"""
        new_scale = entity_manager.reset_scale()
        show_scale_notification(new_scale)

    def ui_elements_scroll_action(action: str):
        """Trigger a ui_elements scroll action on the focused tree's scrollable region.
        action: "down", "up", "top", "bottom"."""
        if action == "down":
            _scroll_focused_tree(-1)
        elif action == "up":
            _scroll_focused_tree(1)
        elif action == "top":
            _, node = _resolve_focused_scroll_target()
            if node:
                state_manager.scroll_to_top(node.id)
        elif action == "bottom":
            _, node = _resolve_focused_scroll_target()
            if node:
                state_manager.scroll_to_bottom(node.id)

