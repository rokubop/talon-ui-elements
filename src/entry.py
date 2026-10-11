from talon import settings
from typing import Any
from .core.entity_manager import entity_manager
from .core.store import store
from .nodes.tree import Tree
from .nodes.mocks import MockTree
from .nodes.image_tree import ImageTree
from .platform.custom_input import custom_input_manager
from .utils import generate_hash

def render_ui(
        tree_constructor: callable,
        props: dict[str, Any] = None,
        on_mount: callable = None,
        on_unmount: callable = None,
        show_hints: bool = None,
        initial_state: dict[str, Any] = None,
        test_mode: bool = False,
        scale: float = None,
    ):
    t = entity_manager.get_tree_with_hash(tree_constructor)
    tree = t["tree"]
    hash = t["hash"]

    if not tree:
        Constructor = MockTree if test_mode else Tree
        tree = Constructor(tree_constructor, hash, props, initial_state)
        entity_manager.add_tree(tree)

    if scale is not None:
        entity_manager.set_scale(scale, tree)

    if show_hints is None:
        show_hints = settings.get("user.ui_elements_hints_show")

    tree.render_manager.render_mount(props, on_mount, on_unmount, show_hints)
    return tree

# What a render of input_text or textarea writes into custom_input_manager
_CUSTOM_INPUT_STATE = (
    "_inputs",
    "_multiline_ids",
    "_on_change_callbacks",
    "_on_submit_callbacks",
    "_render_callbacks",
    "_trees",
    "_prev_props_value",
)

def render_image(
        tree_constructor: callable,
        initial_state: dict[str, Any] = None,
        effects: bool = False,
    ):
    """Paint a tree to (image, rect) without showing it.

    State and inputs are keyed globally, so the render gets its own and the
    trees on screen get theirs back after. Stores are shared, not copied.
    """
    saved_state = store.reactive_state
    saved_inputs = {name: getattr(custom_input_manager, name) for name in _CUSTOM_INPUT_STATE}
    saved_focused_input = custom_input_manager._focused_id
    staged_effects = set(map(id, store.staged_effects))

    tree = None
    try:
        # Inside the try, so a swap that fails partway is still undone
        store.reactive_state = {
            key: value for key, value in saved_state.items() if store.owning_store(key)
        }
        for name, value in saved_inputs.items():
            setattr(custom_input_manager, name, type(value)())
        custom_input_manager._focused_id = None

        tree = ImageTree(tree_constructor, generate_hash(tree_constructor), None, initial_state)
        image, rect = tree.paint(effects)
        if effects:
            tree.run_effects()
        return image, rect
    finally:
        # Restore first, so a failing merge can't leave the render's state in place
        render_state = store.reactive_state
        store.reactive_state = saved_state
        for name, value in saved_inputs.items():
            setattr(custom_input_manager, name, value)
        custom_input_manager._focused_id = saved_focused_input
        # A store key first set during the render belongs to the store
        if render_state is not saved_state:
            for key, value in list(render_state.items()):
                if store.owning_store(key) and key not in saved_state:
                    saved_state[key] = value
        # Effects staged by the render and never consumed
        store.staged_effects = [e for e in store.staged_effects if id(e) in staged_effects]
        if tree:
            tree.dispose()
