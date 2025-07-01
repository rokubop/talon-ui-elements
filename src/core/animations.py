class Transition:
    def __init__(self, property: str, duration: float = 0.2, from_value: float = None, to_value: float = None):
        self.property = property
        self.duration = duration
        self.from_value = from_value
        self.to_value = to_value

    def __repr__(self):
        return f"Transition(property={self.property}, duration={self.duration}, from_value={self.from_value}, to_value={self.to_value})"

class TransitionManager:
    def __init__(self):
        self.nodes = {}

    def start_transition(self, node_id: str, transitions: list[Transition]):
        if node_id not in self.nodes:
            self.nodes[node_id] = {}
        self.nodes[node_id]['transitions'] = transitions
        self.nodes[node_id]['state'] = 'running'