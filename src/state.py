from typing import Dict, List, Optional

class State:
    def __init__(self):
        self.builders: Dict[str, dict] = {}
        self.nodes: Dict[str, dict] = {}
        self.buttons: Dict[str, dict] = {}
        self.inputs: Dict[str, dict] = {}
        self.reactive_states: Dict[str, dict] = {}
        self.highlighted: Dict[str, dict] = {}
        self.text: Dict[str, dict] = {}
        self.scrollable_regions: Dict[str, dict] = {}

    def get_builder_text_nodes(self, builder_id) -> List[dict]:
        return [node for node in self.text if node["builder_id"] == builder_id]

    def get_builder_highlighted_nodes(self, builder_id) -> List[dict]:
        return [node for node in self.highlighted if node["builder_id"] == builder_id]

    # def find_text(self, id: str) -> Optional[dict]:
    #     return self.text.get(id)

state = State()
