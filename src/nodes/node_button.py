from ..properties import Properties
from .node_container import NodeContainer

class NodeButton(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="button", properties=properties)
        self.on_click = self.properties.on_click or (lambda: None)
        self.is_hovering = False
        self.interactive = True