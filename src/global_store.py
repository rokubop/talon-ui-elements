from typing import Dict

class GlobalStore:
    def __init__(self):
        self.root_nodes: Dict[str, dict] = []
        self.id_nodes: Dict[str, dict] = {}

global_store = GlobalStore()
