import inspect
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..interfaces import SubmitEvent
from ..properties import NodeFormProperties

INPUT_ELEMENT_TYPES = {
    ELEMENT_ENUM_TYPE["input_text"],
    ELEMENT_ENUM_TYPE["textarea"],
    ELEMENT_ENUM_TYPE["select"],
}

class NodeForm(NodeContainer):
    def __init__(self, properties: NodeFormProperties = None):
        super().__init__(ELEMENT_ENUM_TYPE["form"], properties=properties)
        self.on_submit = self.properties.on_submit

    def collect_input_values(self) -> dict:
        """Collect values from all child input/textarea/select elements."""
        from ..platform.custom_input import custom_input_manager
        data = {}
        self._collect_from_children(self, data, custom_input_manager)
        return data

    def _collect_from_children(self, node, data, custom_input_manager):
        for child in node.get_children_nodes():
            if child.element_type in INPUT_ELEMENT_TYPES and child.id:
                data[child.id] = custom_input_manager.get_value(child.id)
            if hasattr(child, 'get_children_nodes'):
                self._collect_from_children(child, data, custom_input_manager)

    def fire_submit(self):
        """Collect input values and call on_submit with SubmitEvent."""
        if not self.on_submit:
            return
        data = self.collect_input_values()
        event = SubmitEvent(data=data)
        sig = inspect.signature(self.on_submit)
        if len(sig.parameters) == 0:
            self.on_submit()
        else:
            self.on_submit(event)

def find_parent_form(node):
    """Walk up the tree from a node to find the nearest parent NodeForm."""
    current = node.parent_node
    while current is not None:
        if isinstance(current, NodeForm):
            return current
        current = current.parent_node
    return None
