from .interfaces import Effect
from .core.state_manager import state_manager

def use_effect_no_tree(callback, arg2, arg3=None):
    dependencies: list[str] = []
    cleanup = None

    if arg3 is not None:
        cleanup = arg2
        dependencies = arg3
    else:
        dependencies = arg2

    effect = Effect(
        name=callback.__name__,
        callback=callback,
        cleanup=cleanup,
        dependencies=dependencies,
        tree=None,
        component=None
    )
    state_manager.register_effect(effect)

def use_effect(callback, arg2, arg3=None):
    """
    Register callbacks on state change or on mount/unmount.

    Usage #1: `effect(callback, dependencies)`

    Usage #2: `effect(callback, cleanup, dependencies)`

    Dependencies are `str` state keys, or empty `[]` for mount/unmount effects.
    """
    dependencies: list[str] = []
    cleanup = None

    if arg3 is not None:
        cleanup = arg2
        dependencies = arg3
    else:
        dependencies = arg2

    tree = state_manager.get_processing_tree()
    component = state_manager.get_processing_component()

    if not tree:
        raise ValueError("""
            effect(callback, [cleanup], dependencies) must be called during render of a tree, such as during ui_elements_show(ui).
            You can also optionally use register on_mount and on_unmount effects directly with ui_elements_show(ui, on_mount=callback, on_unmount=callback)
        """)

    if (component and component.id and not component.id in tree.meta_state.components) \
            or not tree.is_mounted:
        effect = Effect(
            name=callback.__name__,
            callback=callback,
            cleanup=cleanup,
            dependencies=dependencies,
            tree=tree,
            component=component
        )
        state_manager.register_effect(effect)