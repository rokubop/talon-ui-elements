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
        print(f"Resolving value {value_or_callable}")
        if callable(value_or_callable):
            print(f"Value is callable")
            return value_or_callable(self._value)
        print(f"Value is not callable")
        return value_or_callable

    def set_initial_value(self, value):
        if self._initial_value is None:
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

    def get_hovered_id(self):
        return store.mouse_state['hovered_id']

    def set_hovered_id(self, id):
        store.mouse_state['hovered_id'] = id

    def get_mousedown_start_id(self):
        return store.mouse_state['mousedown_start_id']

    def set_mousedown_start_id(self, id):
        store.mouse_state['mousedown_start_id'] = id

    def set_processing_tree(self, tree: TreeType):
        store.processing_tree = tree

    def get_processing_tree(self) -> TreeType:
        return store.processing_tree

    def init_state(self, key, initial_value):
        if type(key) is not str:
            raise ValueError("use_state must include a string name like this: use_state('my_state', initial_value)")

        if key not in store.reactive_state:
            store.reactive_state[key] = ReactiveState()

        store.reactive_state[key].set_initial_value(initial_value)

    def rerender_state(self):
        for state in store.reactive_state.values():
            state.activate_next_state_value()

        for tree in store.trees:
            tree.render()
        self.debounce_render_job = None

    def set_state_value(self, key, value):
        print(f"Setting state value for {key} to {value}")
        self.init_state(key, value)
        store.reactive_state[key].set_value(value)

        if not self.debounce_render_job:
            # Let the current event loop finish before rendering
            self.debounce_render_job = cron.after("1ms", self.rerender_state)

    def use_state(self, key, initial_value):
        self.init_state(key, initial_value)
        return store.reactive_state[key].value, lambda new_value: self.set_state_value(key, new_value)

    def register_effect(self, tree, callback, dependencies):
        effect: EffectType = {
            'name': callback.__name__,
            'callback': callback,
            'dependencies': dependencies,
            'tree': tree
        }
        store.staged_effects.append(effect)

    def clear_state(self):
        store.reactive_state.clear()
        store.reset_mouse_state()

state_manager = StateManager()
