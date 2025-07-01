from .node_container import NodeContainer
from ..properties import Properties

class NodeButton(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(properties.element_type or "button", properties=properties)
        self.on_click = self.properties.on_click or (lambda: None)
        self.is_hovering = False
        self.disabled = self.properties.disabled or False
        self.interactive = False if self.properties.disabled else True