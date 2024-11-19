from talon import cron
from .interfaces import ReactiveStateType, TreeType, EffectType, MetaStateType, ScrollRegionType
from typing import Union
from .store import store


class ReactiveState(ReactiveStateType):
    def __init__(self):
        self._initial_value = None
        self._value = None
        self.next_state_queue = []

    @property
    def initial_value(self):
        return self._initial_value

    @property
    def value(self):
        return self._value

    def resolve_value(self, value_or_callable):
        if callable(value_or_callable):
            return value_or_callable(self._value)
        return value_or_callable

    def set_initial_value(self, value):
        if not self._initial_value:
            self._initial_value = value
            self._value = value

    def set_value(self, value_or_callable):
        self.next_state_queue.append(value_or_callable)

    def activate_next_state_value(self):
        next_state = self._value

        for new_state in self.next_state_queue:
            next_state = self.resolve_value(new_state)

        self.next_state_queue.clear()

        self._value = next_state

class StateManager:
    def __init__(self):
        self.debounce_render_job = None

    def set_processing_tree(self, tree: TreeType):
        store.processing_tree = tree

    def get_processing_tree(self) -> TreeType:
        return store.processing_tree

    def init_state(self, key, initial_value):
        if key not in store.state:
            store.state[key] = ReactiveState()

        store.state[key].set_initial_value(initial_value)

    def rerender_state(self):
        for state in store.state.values():
            state.activate_next_state_value()

        for tree in store.trees:
            tree.render()
        self.debounce_render_job = None

    def set_state_value(self, key, value):
        print(f"Setting state value for {key} to {value}")
        self.init_state(key, value)
        store.state[key].set_value(value)

        if not self.debounce_render_job:
            # Let the current event loop finish before rendering
            self.debounce_render_job = cron.after("1ms", self.rerender_state)

    def use_state(self, key, initial_value):
        self.init_state(key, initial_value)
        return store.state[key].value, lambda new_value: self.set_state_value(key, new_value)

    def register_effect(self, tree, callback, dependencies):
        effect: EffectType = {
            'name': callback.__name__,
            'callback': callback,
            'dependencies': dependencies,
            'tree': tree
        }
        store.staged_effects.append(effect)

    def clear_state(self):
        store.state.clear()

state_manager = StateManager()
