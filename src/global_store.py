from typing import Dict
from .interfaces import EffectType, ReactiveStateType, GlobalStoreType

class ReactiveState(ReactiveStateType):
    def __init__(self, value):
        self.value = value
        self.subscriber_root_nodes = []
        self.next_state_queue = []

    def set_value(self, value):
        self.next_state_queue.append(value)

    def add_subscriber(self, root_node):
        self.subscriber_root_nodes.append(root_node)

    def activate_next_state_value(self):
        next_state = self.value

        for new_state in self.next_state_queue:
            if type(new_state) == callable:
                next_state = new_state(next_state)
            else:
                next_state = new_state

        self.value = next_state

class GlobalStore(GlobalStoreType):
    def __init__(self):
        self.root_nodes = []
        self.id_nodes = {}
        self.active_component = None
        self.reactive_global_state = {}
        self.staged_effects = []

global_store = GlobalStore()
