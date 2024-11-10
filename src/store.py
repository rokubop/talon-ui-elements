from typing import Dict, List, Optional

class Store:
    def __init__(self):
        # nodes
        self.nodes: Dict[str, dict] = {}
        self.builder_nodes: Dict[str, dict] = {}
        self.button_nodes: Dict[str, dict] = {}
        self.input_nodes: Dict[str, dict] = {}

        self.reactive_states: Dict[str, dict] = {}
        self.highlighted: Dict[str, dict] = {}
        self.text: Dict[str, dict] = {}
        self.scrollable_regions: Dict[str, dict] = {}

    def get_builder_text_nodes(self, builder_id) -> List[dict]:
        if len(self.builder_nodes) == 1:
            return list(self.text.values())
        else:
            return [node for node in self.text if node["builder_id"] == builder_id]

    def get_builder_highlighted_nodes(self, builder_id) -> List[dict]:
        return [node for node in self.highlighted if node["builder_id"] == builder_id]

    # def find_text(self, id: str) -> Optional[dict]:
    #     return self.text.get(id)

    def has_buttons_or_inputs(self, builder_node):
        if len(self.builder_nodes) == 1:
            return self.button_nodes or self.input_nodes
        else:
            return any([node for node in self.button_nodes if node["builder"] == self.id]) or any([node for node in self.input_nodes if node["builder_id"] == self.id])

    def hide_all(self):
        for node in list(self.builder_nodes.values()):
            node.hide()

        self.nodes = {}
        self.builder_nodes = {}
        self.button_nodes = {}
        self.input_nodes = {}

        self.reactive_states = {}
        self.highlighted = {}
        self.text = {}
        self.scrollable_regions = {}

store = Store()
