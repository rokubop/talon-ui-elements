from ..interfaces import NodeType, TreeType
from typing import Optional, List
from ..state_manager import state_manager
import inspect
import weakref

class Component:
    def __init__(self, renderer: callable, props: dict = None):
        if not callable(renderer):
            raise ValueError("component must be passed a render function")
        tree = state_manager.get_processing_tree()
        if not tree:
            raise ValueError("""
                component must be initialized during rendering.
                Tried to use a component outside of a render which is not allowed.
            """)
        self.renderer = renderer
        self.name = renderer.__name__
        self.props = props or {}
        self._parent_node: weakref.ReferenceType[NodeType] = None
        self._children_nodes: List[weakref.ReferenceType[NodeType]] = []
        self._tree: weakref.ReferenceType[TreeType] = weakref.ref(tree)
        self._root_node: weakref.ReferenceType[NodeType] = None
        self.states = set()
        self.tree.meta_state.add_component(self.name, self)

    @property
    def parent_node(self):
        return self._parent_node() if self._parent_node else None

    @property
    def children_nodes(self):
        return [node() for node in self._children_nodes if node() is not None]

    @property
    def tree(self):
        return self._tree() if self._tree else None

    def init_tree(self):
        state_manager.set_processing_component(self)
        # TODO: pass props to the renderer
        sig = inspect.signature(self.renderer)
        if len(sig.parameters) == 0:
            node = self.renderer()
        else:
            node = self.renderer(self.props)
        state_manager.remove_processing_component(self)
        self._root_node = weakref.ref(node)
        return node