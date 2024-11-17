from ..interfaces import NodeScreenType
from ..options import UIOptions
from .node_container import NodeContainer

class NodeScreen(NodeContainer, NodeScreenType):
    def __init__(self, element_type, options: UIOptions = None):
        super().__init__(
            element_type=element_type,
            options=options
        )
        self.screen_index = 0