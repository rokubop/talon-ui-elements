from .global_store import global_store

class StateManager:
    def get_active_component(self):
        return global_store.active_component

    def set_active_component(self, component):
        global_store.active_component = component

state_manager = StateManager()