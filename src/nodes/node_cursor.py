from talon import ctrl
from talon.types import Point2d
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_CURSOR_REFRESH_RATE
from ..properties import Properties

class NodeCursor(NodeContainer):
    def __init__(self, outer_properties: dict, inner_properties: dict):
        outer_props = Properties(**outer_properties)
        inner_props = Properties(**inner_properties)

        super().__init__(element_type=ELEMENT_ENUM_TYPE["cursor"], properties=outer_props)

        self.inner_wrapper = NodeContainer(element_type=ELEMENT_ENUM_TYPE["div"], properties=inner_props)
        self.add_child(self.inner_wrapper)

        self.refresh_rate = inner_properties.get('refresh_rate', DEFAULT_CURSOR_REFRESH_RATE)

    def __getitem__(self, children_nodes=None):
        if children_nodes is None:
            children_nodes = []

        if not isinstance(children_nodes, list):
            children_nodes = [children_nodes]

        for node in children_nodes:
            self.inner_wrapper.add_child(node)

        return self