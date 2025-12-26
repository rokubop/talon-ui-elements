from talon import settings
from typing import Any
from .core.entity_manager import entity_manager
from .nodes.tree import Tree
from .nodes.mocks import MockTree

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

    # Set scale if provided (overrides stored/default scale)
    if scale is not None:
        entity_manager.set_scale(scale, tree)

    if show_hints is None:
        show_hints = settings.get("user.ui_elements_hints_show")

    tree.render_manager.render_mount(props, on_mount, on_unmount, show_hints)
    return tree