import inspect
import weakref
from typing import List
from ..core.state_manager import state_manager
from ..style import Style
from ..interfaces import NodeType, TreeType, ComponentType

class Component(ComponentType):
    """
    Has it's own renderer for containing rerenders, state, and styles.
    """
    participates_in_layout = False  # Components are replaced by their nodes before layout

    def __init__(self, renderer: callable, props: dict = None):
        if not callable(renderer):
            raise ValueError("component must be passed a render function")
        tree = state_manager.get_processing_tree()
        if not tree:
            raise ValueError("""
                component must be initialized during rendering.
                Tried to use a component outside of a render which is not allowed.
            """)
        self.id = None
        self.renderer = renderer
        self.name = renderer.__name__
        self.props = props or {}
        self.style: Style = None
        self._parent_node: weakref.ReferenceType[NodeType] = None
        self._children_nodes: List[weakref.ReferenceType[NodeType]] = []
        self._tree: weakref.ReferenceType[TreeType] = weakref.ref(tree)
        self._root_node: weakref.ReferenceType[NodeType] = None
        self.states = set()

    @property
    def parent_node(self):
        return self._parent_node() if self._parent_node else None

    @parent_node.setter
    def parent_node(self, value: NodeType):
        self._parent_node = weakref.ref(value) if value else None

    @property
    def children_nodes(self):
        return [node() for node in self._children_nodes if node() is not None]

    def get_children_nodes(self):
        return [node() for node in self._children_nodes if node() is not None]

    @property
    def tree(self):
        return self._tree() if self._tree else None

    def replace_self_with_nodes(self, node_tree: NodeType):
        index = self.parent_node.children_nodes.index(self)
        self.parent_node.children_nodes[index] = node_tree

    def initialize(self, node_index_path: List[int]):
        self.id = (self.name, tuple(node_index_path))
        state_manager.set_processing_component(self)
        # TODO: pass props to the renderer
        sig = inspect.signature(self.renderer)
        if len(sig.parameters) == 0:
            node_tree = self.renderer()
        else:
            node_tree = self.renderer(self.props)
        state_manager.remove_processing_component(self)
        self._root_node = weakref.ref(node_tree)
        self.replace_self_with_nodes(node_tree)
        return node_tree

    def v2_reposition(self, offset = None):
        # Should not be called - should be calling nodes instead
        return

    def destroy(self):
        for node in self.children_nodes:
            node.destroy()
        self._children_nodes.clear()
        self._parent_node = None
        self._tree = None
        self._root_node = None
        self.props.clear()